class BlackjackAgent:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.running_count = 0
        self.cards_seen = 0
        self.total_cards = num_decks * 52
        
        # Values for counting (Hi-Lo System)
        self.HI_LO = {
            '2': 1, '3': 1, '4': 1, '5': 1, '6': 1,
            '7': 0, '8': 0, '9': 0,
            '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
        }
        
        # Values for hand calculation
        self.VALUES = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
        }

    def _parse_card(self, card_str):
        """Extracts rank from card strings like '10H', 'Ah', '10'."""
        # Remove suit characters (H, D, C, S) if present, case insensitive
        rank = card_str.upper().strip('HDCS')
        return rank

    def update_count(self, new_cards):
        """Call this whenever NEW cards are revealed on the table."""
        for card in new_cards:
            rank = self._parse_card(card)
            if rank in self.HI_LO:
                self.running_count += self.HI_LO[rank]
                self.cards_seen += 1

    def get_true_count(self):
        decks_remaining = max((self.total_cards - self.cards_seen) / 52, 0.5)
        return self.running_count / decks_remaining

    def analyze_hand(self, cards):
        """Calculates value and checks if hand is soft."""
        value = 0
        aces = 0
        for card in cards:
            rank = self._parse_card(card)
            value += self.VALUES.get(rank, 0)
            if rank == 'A':
                aces += 1
        
        # Adjust Aces
        while value > 21 and aces:
            value -= 10
            aces -= 1
            
        # Is Soft? (True if we have an Ace counting as 11)
        # We check this by seeing if the raw total without reducing that specific Ace 
        # would allow an 11. 
        # Simplified: If we used an Ace as 11 and didn't bust, it's soft.
        is_soft = (aces > 0) and (value <= 21) 
        # Note: The logic above simplifies 'aces' to mean "aces currently counting as 11"
        # because we decremented 'aces' in the while loop for every Ace forced to be 1.
        
        return value, (aces > 0)

    def get_move(self, player_cards, dealer_cards):
        """
        Main decision method.
        player_cards: list of strings e.g. ['10H', '7D']
        dealer_cards: list of strings e.g. ['6C'] (Only need the Upcard)
        """
        player_val, is_soft = self.analyze_hand(player_cards)
        
        # Parse dealer upcard (assume index 0 is visible)
        if not dealer_cards:
            raise ValueError("Dealer must have at least one card")
        dealer_rank = self._parse_card(dealer_cards[0])
        dealer_val = self.VALUES[dealer_rank]

        # --- 1. SURRENDER CHECK ---
        if len(player_cards) == 2:
            if player_val == 16 and dealer_val in [9, 10, 11]: return 'SURRENDER'
            if player_val == 15 and dealer_val == 10: return 'SURRENDER'

        # --- 2. SOFT TOTALS ---
        if is_soft:
            if player_val >= 20: return 'STAND'
            if player_val == 19:
                return 'DOUBLE' if dealer_val == 6 and len(player_cards) == 2 else 'STAND'
            if player_val == 18:
                if dealer_val in [2,3,4,5,6]: return 'DOUBLE' if len(player_cards) == 2 else 'STAND'
                if dealer_val in [9,10,11]: return 'HIT'
                return 'STAND'
            if player_val == 17:
                return 'DOUBLE' if dealer_val in [3,4,5,6] and len(player_cards) == 2 else 'HIT'
            if player_val in [15, 16]:
                return 'DOUBLE' if dealer_val in [4,5,6] and len(player_cards) == 2 else 'HIT'
            if player_val in [13, 14]:
                return 'DOUBLE' if dealer_val in [5,6] and len(player_cards) == 2 else 'HIT'
            return 'HIT'

        # --- 3. HARD TOTALS ---
        else:
            if player_val >= 17: return 'STAND'
            if player_val == 16: return 'STAND' if dealer_val in [2,3,4,5,6] else 'HIT'
            if player_val == 15: return 'STAND' if dealer_val in [2,3,4,5,6] else 'HIT'
            if player_val in [13,14]: return 'STAND' if dealer_val in [2,3,4,5,6] else 'HIT'
            if player_val == 12: return 'STAND' if dealer_val in [4,5,6] else 'HIT'
            
            # Double logic
            if player_val == 11: 
                return 'DOUBLE' if len(player_cards) == 2 else 'HIT'
            if player_val == 10: 
                return 'DOUBLE' if dealer_val < 10 and len(player_cards) == 2 else 'HIT'
            if player_val == 9: 
                return 'DOUBLE' if dealer_val in [3,4,5,6] and len(player_cards) == 2 else 'HIT'
            
            return 'HIT'
