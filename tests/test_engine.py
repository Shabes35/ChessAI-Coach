
import chess
from analyzer import evaluate_position, analyze_position

board = chess.Board()

print("Evaluation:")
print(evaluate_position(board, chess.WHITE))

print("\nFull analysis:")
print(analyze_position(board))
