from coach import generate_explanation

sample_data = {
    "move": "Qd6",
    "move_quality": "Good",
    "features": {
        "is_capture": False,
        "gives_check": False
    }
}

print(generate_explanation(sample_data, "opponent_move"))