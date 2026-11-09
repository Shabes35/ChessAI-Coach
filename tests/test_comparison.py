
import chess
from analyzer import compare_move

board = chess.Board()

# Test the player's move: e2e4
move = chess.Move.from_uci("e2e4")

result = compare_move(board, move)

print(result)
