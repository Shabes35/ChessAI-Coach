
def classify_move(comparison):

    best = comparison["best_evaluation"]
    played = comparison["played_move_evaluation"]
    loss = comparison["evaluation_loss"]

    # Handle forced checkmate situations
    if played["type"] == "mate":

        mate = played["value"]

        if mate is not None and mate < 0:
            quality = "Blunder - Forced mate against you"

        elif mate is not None and mate > 0:
            quality = "Winning - Forced mate available"

        else:
            quality = "Checkmate"

    elif best["type"] == "mate":

        mate = best["value"]

        if mate is not None and mate > 0:
            quality = "Missed forced mate"

        elif mate is not None and mate < 0:
            quality = "Position is already lost"

        else:
            quality = "Needs further analysis"

    elif loss is None:
        quality = "Needs further analysis"

    # Classify normal positions using evaluation loss
    elif loss <= 0.15:
        quality = "Good"

    elif loss <= 0.50:
        quality = "Inaccuracy"

    elif loss <= 1.50:
        quality = "Mistake"

    else:
        quality = "Blunder"

    return {
        "move_quality": quality,
        "evaluation_loss": loss
    }
