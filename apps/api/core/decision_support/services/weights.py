"""Weight normalization helper (AC11). Not a scoring engine."""


def normalize_weights(weights: list[float]) -> list[float]:
    total = sum(weights)
    if total <= 0:
        raise ValueError('weights sum must be positive')
    return [w / total for w in weights]
