
import chess
import chess.engine

engine = chess.engine.SimpleEngine.popen_uci(
    r"D:\ChessAI-Coach\stockfish\stockfish-windows-x86-64-universal.exe"
)

board = chess.Board()

result = engine.analyse(
    board,
    chess.engine.Limit(time=2)
)

print("Best move:", result["pv"][0])
print("Evaluation:", result["score"])

engine.quit()
