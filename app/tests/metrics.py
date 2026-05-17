"""
Evaluation metrics utilities.
"""


def calculate_mean(values):

    if not values:
        return 0

    return sum(values) / len(values)


def precision_at_k(
    relevant,
    retrieved,
    k=10
):

    retrieved = retrieved[:k]

    hits = 0

    for item in retrieved:

        if item in relevant:
            hits += 1

    return hits / k