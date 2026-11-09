
import chess
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from analyzer import analyze_position, compare_move, validate_threats
from classifier import classify_move
from feature_extractor import (
    extract_move_features,
    extract_position_context
)
from coach import generate_explanation

app = FastAPI()

# Shared chessboard
board = chess.Board()

# None means spectator mode
player_color = None

class MoveRequest(BaseModel):
    move: str

class GameStartRequest(BaseModel):
    player_color: str

@app.get("/")
def home():
    return {
        "message": "Chess AI Coach is running!"
    }


@app.post("/start")
def start_game(request: GameStartRequest):

    global player_color

    selected_color = request.player_color.lower()

    if selected_color == "white":
        player_color = chess.WHITE

    elif selected_color == "black":
        player_color = chess.BLACK

    elif selected_color == "spectator":
        player_color = None

    else:
        raise HTTPException(
            status_code=400,
            detail="Choose white, black, or spectator"
        )

    board.reset()

    return {
        "message": "Game started",
        "player_color": selected_color,
        "fen": board.fen(),
        "turn": "White",
        "legal_moves": [move.uci() for move in board.legal_moves],
        "move_history": []
    }


# Get current board information
@app.get("/board")
def get_board():
    return {
        "fen": board.fen(),
        "turn": "White" if board.turn else "Black",
        "legal_moves": [move.uci() for move in board.legal_moves],
        "move_history": [move.uci() for move in board.move_stack]
    }


# Play a move and evaluate its quality
@app.post("/move")
def make_move(request: MoveRequest):

    if board.is_game_over():
        raise HTTPException(
            status_code=400,
            detail="Game is already over. Reset to start a new game."
        )

    try:
        move = chess.Move.from_uci(request.move)

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid move format"
        )

    if move not in board.legal_moves:
        raise HTTPException(
            status_code=400,
            detail="Illegal move"
        )

    # Remember whose move is being played
    moving_color = board.turn

    if player_color is None:
        coaching_mode = "spectator"

    elif moving_color == player_color:
        coaching_mode = "your_move"

    else:
        coaching_mode = "opponent_move"


    # 1. Extract move features
    features = extract_move_features(board, move)

    # create a temporary board with the player's move applied 

    next_board = board.copy()
    next_board.push(move)

    position_context = extract_position_context(next_board)


    # validate attack against opponent pieces
    threat_validation = validate_threats(
        next_board,
        features["player_attacks"]
    )


    # 2. Compare player's move against Stockfish's best move
    comparison = compare_move(board, move)

    # 3. Classify the move
    classification = classify_move(comparison)

    # 4. Convert move into human-readable notation
    san_move = board.san(move)

    # 5. Prepare actual chess data for Gemini
    chess_data = {
        "move": san_move,
        "features": features,
        "position_before_move": board.fen(),
        "threat_validation": threat_validation,
        "position_context": position_context
    }

    # Only reveal engine recommendations when explaining the player's move
    if coaching_mode == "your_move":

        chess_data.update({
            "best_move": comparison["best_move"],
            "best_evaluation": comparison["best_evaluation"],
            "played_move_evaluation": comparison["played_move_evaluation"],
            "evaluation_loss": classification["evaluation_loss"],
            "move_quality": classification["move_quality"]
        })

    # 6. Ask Gemini to explain the move
    try:
        coach_explanation = generate_explanation(
            chess_data,
            coaching_mode
        )
        coach_status = "success"

    except Exception as e:
        print("Gemini error:", e)
        coach_explanation = "Coach explanation is temporarily unavailable."
        coach_status = "unavailable"

    # 7. Apply the move to the actual board
    board.push(move)

    return {
        "move": san_move,
        "best_move": comparison["best_move"],
        "best_evaluation": comparison["best_evaluation"],
        "played_move_evaluation": comparison["played_move_evaluation"],
        "evaluation_loss": classification["evaluation_loss"],
        "move_quality": classification["move_quality"],
        "features": features,
        "coaching_mode": coaching_mode,
        "coach_explanation": coach_explanation,
        "coach_status": coach_status,
        "fen": board.fen(),
        "turn": "White" if board.turn else "Black",
        "legal_moves": [m.uci() for m in board.legal_moves],
        "move_history": [m.uci() for m in board.move_stack],
        "threat_validation" : threat_validation
    }


# Undo the last move
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


# Reset the game
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


# Analyse the current position using Stockfish
@app.get("/analyze")
def analyze_position_endpoint():

    if board.is_game_over():
        return {
            "game_over": True,
            "result": board.result(),
            "message": "Game has ended. No more moves available."
        }

    analysis = analyze_position(board)

    return {
        "game_over": False,
        **analysis
    }
