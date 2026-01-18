import os
import time
from screenshot import capture_and_save_to_out
from blackjack_agent import BlackjackAgent
import cards_viewing
from collections import Counter
from message import post_comment_with_mouse

agent = BlackjackAgent(num_decks=1)
prev_player_hand = []
prev_dealer_hand = []

def get_card_deltas(current, previous):
    # return multiset of newly observed cards (as a list)
    cur_cnt = Counter(current)
    prev_cnt = Counter(previous)
    diff = cur_cnt - prev_cnt
    # expand to list of ranks, preserving multiplicity
    result = []
    for rank, cnt in diff.items():
        result.extend([rank] * cnt)
    return result

while(True):
    time.sleep(10)

    path_to_image = capture_and_save_to_out("curr_board.jpeg")
    try:
        current_player_hand, current_dealer_hand = cards_viewing.analyze_image_file(path_to_image)
    except Exception as e:
        print(f"Failed to analyze image {path_to_image}: {e}")
        continue

    player_delta = get_card_deltas(current_player_hand, prev_player_hand)
    dealer_delta = get_card_deltas(current_dealer_hand, prev_dealer_hand)

    if dealer_delta:
        agent.update_count(dealer_delta) 
    if player_delta:
        agent.update_count(player_delta)

    if player_delta:
        action = agent.get_move(current_player_hand, current_dealer_hand)
        post_comment_with_mouse(action.lower())    
        print(f"{action}")

    prev_player_hand = current_player_hand
    prev_dealer_hand = current_dealer_hand
