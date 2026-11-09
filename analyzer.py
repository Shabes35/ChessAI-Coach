
import chess
import chess.engine


# Stockfish executable location
ENGINE_PATH = r"D:\ChessAI-Coach\stockfish\stockfish-windows-x86-64-universal.exe"


# Convert Stockfish score into a consistent dictionary
def format_evaluation(score):

    if score.is_mate():
        return {
            "type": "mate",
            "value": score.mate()
        }

    return {
        "type": "cp",
        "value": score.score() / 100
    }


# Evaluate a position from a particular player's perspective
def evaluate_position(position, color):

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    try:
        result = engine.analyse(
            position,
            chess.engine.Limit(time=1)
        )

        score = result["score"].pov(color)

        return format_evaluation(score)

    finally:
        engine.quit()


# Analyse a position and find the best move
def analyze_position(position):

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    try:
        result = engine.analyse(
            position,
            chess.engine.Limit(time=2)
        )

        score = result["score"].white()
        best_move = result["pv"][0] if result.get("pv") else None

        return {
            "best_move": best_move.uci() if best_move else None,
            "evaluation": format_evaluation(score),
            "principal_variation": [
                move.uci() for move in result.get("pv", [])
            ]
        }

    finally:
        engine.quit()


# Compare the player's move against Stockfish's best move
def compare_move(board, move):

    player = board.turn

    if move not in board.legal_moves:
        raise ValueError("Illegal move")

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    try:
        # Find Stockfish's best move
        best_result = engine.analyse(
            board,
            chess.engine.Limit(time=2)
        )

        # Analyse the player's move only
        played_result = engine.analyse(
            board,
            chess.engine.Limit(time=2),
            root_moves=[move]
        )

        # Both evaluations use the same player's perspective
        best_score = best_result["score"].pov(player)
        played_score = played_result["score"].pov(player)

        best_move = (
            best_result["pv"][0]
            if best_result.get("pv")
            else None
        )

        # Calculate evaluation loss for normal positions
        if not best_score.is_mate() and not played_score.is_mate():

            evaluation_loss = max(
                0,
                (best_score.score() - played_score.score()) / 100
            )

        else:
            evaluation_loss = None

        return {
            "best_move": best_move.uci() if best_move else None,
            "best_evaluation": format_evaluation(best_score),
            "played_move_evaluation": format_evaluation(played_score),
            "evaluation_loss": (
                round(evaluation_loss, 2)
                if evaluation_loss is not None
                else None
            )
        }

    finally:
        engine.quit()


# Validate potential threats using Stockfish

def validate_threats(board, threats):

    if not threats:
        return {
            "best_response": None,
            "evaluation": None,
            "validated_threats": []
        }

    engine = chess.engine.SimpleEngine.popen_uci(ENGINE_PATH)

    try:
        result = engine.analyse(
            board,
            chess.engine.Limit(time=2)
        )

        best_move = (
            result["pv"][0]
            if result.get("pv")
            else None
        )

        if best_move is None:
            return {
                "best_response": None,
                "evaluation": None,
                "validated_threats": []
            }

        response_board = board.copy()
        response_board.push(best_move)

        validated_threats = []

        for threat in threats:

            original_square = chess.parse_square(
                threat["square"]
            )

            original_piece = board.piece_at(original_square)

            if original_piece is None:
                continue

            target_color = original_piece.color
            piece_type = original_piece.piece_type

            # Find the same piece type and color after the response
            surviving_squares = [
                square
                for square, piece in response_board.piece_map().items()
                if piece.color == target_color
                and piece.piece_type == piece_type
            ]

            # Check whether the piece still exists
            piece_survives = bool(surviving_squares)

            # Find whether any surviving piece is still attacked
            still_attacked = False

            if piece_survives:
                still_attacked = any(
                    response_board.attackers(
                        not target_color,
                        square
                    )
                    for square in surviving_squares
                )

            validated_threats.append({
                "piece": threat["piece"],
                "original_square": threat["square"],
                "surviving_squares": [
                    chess.square_name(sq)
                    for sq in surviving_squares
                ],
                "piece_survives": piece_survives,
                "still_attacked_after_best_response": still_attacked
            })

        return {
            "best_response": best_move.uci(),
            "evaluation": format_evaluation(
                result["score"].pov(board.turn)
            ),
            "principal_variation": [
                move.uci() for move in result.get("pv", [])
            ],
            "validated_threats": validated_threats
        }

    finally:
        engine.quit()
