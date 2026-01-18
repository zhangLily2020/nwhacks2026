import random
import matplotlib.pyplot as plt

# --- Configuration ---
NUM_DECKS = 2
MIN_BET = 25          # Standard table minimum
MAX_BET = 500         # Standard table maximum
STARTING_BANKROLL = 10000
ROUNDS_TO_SIMULATE = 1000
DECK_PENETRATION = 0.75 # Shuffle after 75% of cards are dealt

# --- Constants ---
SUITS = ['H', 'D', 'C', 'S']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 
    '10': 10, 'J': 10, 'Q': 10, 'K': 10, 'A': 11
}
HI_LO_VALUES = {
    '2': 1, '3': 1, '4': 1, '5': 1, '6': 1, 
    '7': 0, '8': 0, '9': 0, 
    '10': -1, 'J': -1, 'Q': -1, 'K': -1, 'A': -1
}

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
        self.value = VALUES[rank]
        self.count_value = HI_LO_VALUES[rank]

class Shoe:
    def __init__(self, num_decks):
        self.num_decks = num_decks
        self.cards = []
        self.reshuffle()

    def reshuffle(self):
        self.cards = [Card(r, s) for r in RANKS for s in SUITS] * self.num_decks
        random.shuffle(self.cards)
        self.running_count = 0

    def draw(self):
        if not self.cards:
            self.reshuffle()
        card = self.cards.pop()
        self.running_count += card.count_value
        return card

    def needs_shuffle(self):
        total_cards = 52 * self.num_decks
        return (len(self.cards) / total_cards) < (1 - DECK_PENETRATION)

    def get_true_count(self):
        decks_remaining = max(len(self.cards) / 52, 0.5)
        return self.running_count / decks_remaining

class Hand:
    def __init__(self):
        self.cards = []
        self.bet = 0
        self.surrendered = False

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = sum(c.value for c in self.cards)
        aces = sum(1 for c in self.cards if c.rank == 'A')
        while value > 21 and aces:
            value -= 10
            aces -= 1
        return value

    def is_soft(self):
        low_ace_val = sum(c.value if c.rank != 'A' else 1 for c in self.cards)
        if low_ace_val > 21: return False
        return any(c.rank == 'A' for c in self.cards) and (low_ace_val + 10 <= 21)

class AI_Player:
    def __init__(self, bankroll):
        self.bankroll = bankroll
        self.history = [bankroll]

    def decide_bet(self, true_count):
        # --- SMARTER BETTING: KELLY CRITERION ---
        
        # 1. Estimate Player Advantage
        # Rule of thumb: House edge is ~0.5%. Player gains ~0.5% edge per True Count point over 1.
        if true_count <= 1:
            advantage = -0.005 # House has edge
        else:
            advantage = 0.005 * (true_count - 1.5)

        # 2. Apply Kelly Criterion
        # Kelly Formula: Bet Fraction = Advantage / Variance
        # In Blackjack, variance is roughly 1.3
        if advantage <= 0:
            bet = MIN_BET
        else:
            kelly_fraction = advantage / 1.3
            # We use "Fractional Kelly" (e.g., 0.5 Kelly) to reduce volatility.
            # Full Kelly is mathematically optimal for growth but very risky emotionally.
            safe_kelly = kelly_fraction * 0.75
            bet = self.bankroll * safe_kelly

        # 3. Apply Table Limits & Integer rounding
        bet = max(MIN_BET, min(bet, MAX_BET))
        
        # 4. Don't bet more than we have
        return min(bet, self.bankroll)

    def get_move(self, player_hand, dealer_up_card):
        player_val = player_hand.get_value()
        dealer_val = dealer_up_card.value
        is_soft = player_hand.is_soft()

        # Surrender
        if len(player_hand.cards) == 2:
            if player_val == 16 and dealer_val in [9, 10, 11]: return 'SURRENDER'
            if player_val == 15 and dealer_val == 10: return 'SURRENDER'

        # Soft Totals
        if is_soft:
            if player_val >= 20: return 'STAND'
            if player_val == 19: return 'DOUBLE' if dealer_val == 6 and len(player_hand.cards)==2 else 'STAND'
            if player_val == 18:
                if dealer_val in [2,3,4,5,6]: return 'DOUBLE' if len(player_hand.cards)==2 else 'STAND'
                if dealer_val in [9,10,11]: return 'HIT'
                return 'STAND'
            if player_val == 17: return 'DOUBLE' if dealer_val in [3,4,5,6] and len(player_hand.cards)==2 else 'HIT'
            if player_val in [15,16]: return 'DOUBLE' if dealer_val in [4,5,6] and len(player_hand.cards)==2 else 'HIT'
            if player_val in [13,14]: return 'DOUBLE' if dealer_val in [5,6] and len(player_hand.cards)==2 else 'HIT'
            return 'HIT'

        # Hard Totals
        else:
            if player_val >= 17: return 'STAND'
            if player_val == 16: return 'STAND' if dealer_val in [2,3,4,5,6] else 'HIT'
            if player_val == 15: return 'STAND' if dealer_val in [2,3,4,5,6] else 'HIT'
            if player_val in [13,14]: return 'STAND' if dealer_val in [2,3,4,5,6] else 'HIT'
            if player_val == 12: return 'STAND' if dealer_val in [4,5,6] else 'HIT'
            if player_val == 11: return 'DOUBLE' if len(player_hand.cards)==2 else 'HIT'
            if player_val == 10: return 'DOUBLE' if dealer_val < 10 and len(player_hand.cards)==2 else 'HIT'
            if player_val == 9: return 'DOUBLE' if dealer_val in [3,4,5,6] and len(player_hand.cards)==2 else 'HIT'
            return 'HIT'

def play_round(shoe, ai):
    if shoe.needs_shuffle(): shoe.reshuffle()

    # Bet
    true_count = shoe.get_true_count()
    bet = ai.decide_bet(true_count)
    ai.bankroll -= bet
    player_hand = Hand()
    dealer_hand = Hand()
    player_hand.bet = bet

    # Deal
    player_hand.add_card(shoe.draw())
    dealer_hand.add_card(shoe.draw())
    player_hand.add_card(shoe.draw())
    dealer_up_card = shoe.draw()
    dealer_hand.add_card(dealer_up_card)

    # Check Naturals
    p_bj = (player_hand.get_value() == 21)
    d_bj = (dealer_hand.get_value() == 21)

    if d_bj and p_bj:
        ai.bankroll += bet
        ai.history.append(ai.bankroll)
        return
    if d_bj:
        ai.history.append(ai.bankroll)
        return
    if p_bj:
        ai.bankroll += bet + (bet * 1.5)
        ai.history.append(ai.bankroll)
        return

    # Player Turn
    while True:
        move = ai.get_move(player_hand, dealer_up_card)
        if move == 'SURRENDER':
            player_hand.surrendered = True
            ai.bankroll += bet * 0.5
            ai.history.append(ai.bankroll)
            return
        elif move == 'DOUBLE':
            if ai.bankroll >= bet:
                ai.bankroll -= bet
                player_hand.bet += bet
                player_hand.add_card(shoe.draw())
                break
            else:
                move = 'HIT'
        
        if move == 'HIT':
            player_hand.add_card(shoe.draw())
            if player_hand.get_value() > 21: # Bust
                ai.history.append(ai.bankroll)
                return
        elif move == 'STAND':
            break

    # Dealer Turn
    while dealer_hand.get_value() < 17:
        dealer_hand.add_card(shoe.draw())

    p_val = player_hand.get_value()
    d_val = dealer_hand.get_value()

    if d_val > 21 or p_val > d_val:
        ai.bankroll += player_hand.bet * 2
    elif p_val == d_val:
        ai.bankroll += player_hand.bet

    ai.history.append(ai.bankroll)

# --- RUN SIMULATION ---
shoe = Shoe(NUM_DECKS)
ai = AI_Player(STARTING_BANKROLL)

print(f"Simulating {ROUNDS_TO_SIMULATE} hands using Kelly Criterion betting...")
for _ in range(ROUNDS_TO_SIMULATE):
    if ai.bankroll < MIN_BET:
        print("Bankrupt!")
        break
    play_round(shoe, ai)

# --- VISUALIZATION ---
plt.figure(figsize=(12, 6))
plt.plot(ai.history, linewidth=1, color='#2c3e50')
plt.title(f'Blackjack AI Performance (Kelly Criterion)\nStarting: ${STARTING_BANKROLL} | Final: ${ai.bankroll:.2f}')
plt.xlabel('Hands Played')
plt.ylabel('Bankroll ($)')
plt.axhline(y=STARTING_BANKROLL, color='r', linestyle='--', label='Break Even')
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()