import chess
from feature_extractor import extract_move_features

board = chess.Board()

# Play a sequence that creates a knight attack
moves = ["e2e4", "d7d5", "e4d5", "d8d5"]

for uci in moves:
    board.push_uci(uci)

# White plays Nc3, attacking Black's queen on d5
move = chess.Move.from_uci("b1c3")

features = extract_move_features(board, move)

from pprint import pprint
pprint(features)