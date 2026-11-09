from classifier import classify_move

comparison = {
    "best_move": "e2e4",
    "best_evaluation": {
        "type": "cp",
        "value": 0.35
    },
    "played_move_evaluation": {
        "type": "cp",
        "value": 0.30
    },
    "evaluation_loss": 0.05
}

result = classify_move(comparison)

print(result)