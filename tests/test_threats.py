import chess

from feature_extractor import detect_hanging_pieces
from analyzer import validate_threats


board = chess.Board()

# Create a position where White's knight attacks Black's queen
moves = ["e2e4", "d7d5", "e4d5", "d8d5", "b1c3"]

for move in moves:
    board.push_uci(move)


print("Position:")
print(board)

# Find Black's potentially hanging pieces
threats = detect_hanging_pieces(
    board,
    target_color=chess.BLACK,
    attacker_color=chess.WHITE
)

print("\nPython detected threats:")
print(threats)

# Ask Stockfish to analyse Black's best response
result = validate_threats(board, threats)

print("\nStockfish validation:")
print(result)