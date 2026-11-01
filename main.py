
import chess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Create one chessboard for our game
board = chess.Board()


class MoveRequest(BaseModel):
    move: str


@app.get("/")
def home():
    return {"message": "Chess AI Coach is running!"}


@app.get("/board")
def get_board():
    
    return {
        "fen": board.fen(),
        "turn": "White" if board.turn else "Black",
        "legal_moves": [move.uci() for move in board.legal_moves],
        "move_history": [move.uci() for move in board.move_stack]
    }


@app.post("/move")
def make_move(request: MoveRequest):
    try:
        move = chess.Move.from_uci(request.move)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move format")

    if move not in board.legal_moves:
        raise HTTPException(status_code=400, detail="Illegal move")

    san_move = board.san(move)
    board.push(move)

    return {
        "move": san_move,
        "fen": board.fen(),
        "turn": "White" if board.turn else "Black",
        "legal_moves": [m.uci() for m in board.legal_moves],
        "move_history": [m.uci() for m in board.move_stack]
    }

@app.post("/undo")
def undo_move():
    if len(board.move_stack) == 0:
        raise HTTPException(
            status_code=400,
            detail="No moves to undo"
        )

    undone_move = board.pop()

    return {
        "undone_move": undone_move.uci(),
        "fen": board.fen(),
        "turn": "White" if board.turn else "Black",
        "legal_moves": [m.uci() for m in board.legal_moves],
        "move_history": [m.uci() for m in board.move_stack]
    }

@app.post("/reset")
def reset_game():
    board.reset()

    return {
        "message": "New game started",
        "fen": board.fen(),
        "turn": "White",
        "legal_moves": [m.uci() for m in board.legal_moves],
        "move_history": []
    }
