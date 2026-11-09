
import chess


# Approximate chess piece values
PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 100
}


def find_attacked_pieces(board, target_color, attacker_color):

    attacked_pieces = []

    for square in chess.SQUARES:

        piece = board.piece_at(square)

        if piece is None or piece.color != target_color:
            continue

        # Find enemy pieces attacking this square
        attackers = board.attackers(attacker_color, square)

        if not attackers:
            continue

        # Find friendly pieces defending this square
        defenders = board.attackers(target_color, square)

        attacked_pieces.append({
            "piece": chess.piece_name(piece.piece_type),
            "square": chess.square_name(square),

            "attacked_by": [
                {
                    "piece": chess.piece_name(
                        board.piece_at(sq).piece_type
                    ),
                    "square": chess.square_name(sq)
                }
                for sq in attackers
            ],

            "defended_by": [
                {
                    "piece": chess.piece_name(
                        board.piece_at(sq).piece_type
                    ),
                    "square": chess.square_name(sq)
                }
                for sq in defenders
            ]
        })

    return attacked_pieces


def detect_hanging_pieces(board, target_color, attacker_color):

    attacked_pieces = find_attacked_pieces(
        board,
        target_color,
        attacker_color
    )

    potential_hanging = []

    for item in attacked_pieces:

        attacker_count = len(item["attacked_by"])
        defender_count = len(item["defended_by"])

        # First-pass heuristic, not a confirmed tactical verdict
        if attacker_count > defender_count:

            square = chess.parse_square(item["square"])
            piece = board.piece_at(square)

            piece_value = PIECE_VALUES[piece.piece_type]

            potential_hanging.append({
                **item,
                "piece_value": piece_value,
                "attacker_count": attacker_count,
                "defender_count": defender_count,
                "status": "potentially_hanging"
            })

    return potential_hanging


def extract_move_features(board, move):

    # Identify the moving piece
    moving_piece = board.piece_at(move.from_square)

    # Identify captured piece
    captured_piece = None

    if board.is_en_passant(move):

        capture_square = (
            move.to_square - 8
            if board.turn == chess.WHITE
            else move.to_square + 8
        )

        captured_piece = board.piece_at(capture_square)

    else:
        captured_piece = board.piece_at(move.to_square)

    # Check whether the move gives check
    gives_check = board.gives_check(move)

    # Check special move types
    is_capture = board.is_capture(move)
    is_castling = board.is_castling(move)
    is_en_passant = board.is_en_passant(move)

    # Check promotion
    promotion = (
        chess.piece_name(move.promotion)
        if move.promotion
        else None
    )

    # Apply move on a temporary board
    next_board = board.copy()
    next_board.push(move)

    # Find opponent's attacks against our pieces
    opponent_threats = find_attacked_pieces(
        next_board,
        target_color=not next_board.turn,
        attacker_color=next_board.turn
    )

    # Find our attacks against opponent's pieces
    player_attacks = find_attacked_pieces(
        next_board,
        target_color=next_board.turn,
        attacker_color=not next_board.turn
    )

    # Detect potentially hanging pieces on both sides
    opponent_hanging = detect_hanging_pieces(
        next_board,
        target_color=not next_board.turn,
        attacker_color=next_board.turn
    )

    player_hanging = detect_hanging_pieces(
        next_board,
        target_color=next_board.turn,
        attacker_color=not next_board.turn
    )

    return {
        "moving_piece": chess.piece_name(moving_piece.piece_type),

        "captured_piece": (
            chess.piece_name(captured_piece.piece_type)
            if captured_piece
            else None
        ),

        "is_capture": is_capture,
        "gives_check": gives_check,
        "is_checkmate": next_board.is_checkmate(),
        "is_castling": is_castling,
        "is_en_passant": is_en_passant,
        "promotion": promotion,

        "opponent_threats": opponent_threats,
        "player_attacks": player_attacks,

        "opponent_potentially_hanging": opponent_hanging,
        "player_potentially_hanging": player_hanging
    }


def extract_position_context(board):

    center_squares = ["d4", "e4", "d5", "e5"]

    position_context = {
        "center_control": {},
        "piece_development": {},
        "castling_rights": {}
    }

    home_squares = {
        chess.WHITE: ["b1", "g1", "c1", "f1"],
        chess.BLACK: ["b8", "g8", "c8", "f8"]
    }

    for color, name in [
        (chess.WHITE, "white"),
        (chess.BLACK, "black")
    ]:

        # 1. Centre control
        controlled_squares = [
            square for square in center_squares
            if board.is_attacked_by(
                color,
                chess.parse_square(square)
            )
        ]

        occupied_center = [
            {
                "square": chess.square_name(square),
                "piece": chess.piece_name(piece.piece_type)
            }
            for square, piece in board.piece_map().items()
            if piece.color == color
            and chess.square_name(square) in center_squares
        ]

        position_context["center_control"][name] = {
            "controlled_squares": controlled_squares,
            "control_count": len(controlled_squares),
            "occupied_squares": occupied_center
        }

        # 2. Minor piece development
        developed_pieces = []

        for square, piece in board.piece_map().items():

            if piece.color != color:
                continue

            if piece.piece_type not in [
                chess.KNIGHT,
                chess.BISHOP
            ]:
                continue

            square_name = chess.square_name(square)

            if square_name not in home_squares[color]:
                developed_pieces.append({
                    "piece": chess.piece_name(piece.piece_type),
                    "square": square_name
                })

        position_context["piece_development"][name] = {
            "developed_pieces": developed_pieces,
            "developed_count": len(developed_pieces)
        }

        # 3. Castling rights
        position_context["castling_rights"][name] = {
            "kingside": board.has_kingside_castling_rights(color),
            "queenside": board.has_queenside_castling_rights(color)
        }

    return position_context

