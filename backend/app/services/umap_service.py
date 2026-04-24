import random

import numpy as np

from app.models.star import Star

_JITTER_SCALE = 0.5  # coordinate units of random offset for new stars


def place_new_star(
    existing_stars: list[Star],
    new_embedding: list[float],
    k: int = 3,
) -> tuple[float, float]:
    """
    Compute (x, y) placement for a new star without recalculating existing coordinates.

    Strategy:
    - 0 existing stars → place at origin
    - 1 existing star  → place at (1.0, 0.0) relative to it
    - 2+ existing stars → weighted centroid of top-k similar, plus jitter
    """
    if not existing_stars:
        return 0.0, 0.0

    if len(existing_stars) == 1:
        sole = existing_stars[0]
        return sole.pos_x + 1.0, sole.pos_y

    new_vec = np.array(new_embedding, dtype=np.float32)
    new_norm = np.linalg.norm(new_vec)
    if new_norm == 0:
        return _jittered(0.0, 0.0)

    similarities: list[tuple[float, Star]] = []
    for star in existing_stars:
        existing_vec = np.array(star.embedding, dtype=np.float32)
        norm = np.linalg.norm(existing_vec)
        if norm == 0:
            continue
        cosine_sim = float(np.dot(new_vec, existing_vec) / (new_norm * norm))
        similarities.append((cosine_sim, star))

    similarities.sort(key=lambda t: t[0], reverse=True)
    top_k = similarities[:k]

    if not top_k:
        return _jittered(0.0, 0.0)

    total_weight = sum(sim for sim, _ in top_k)
    if total_weight == 0:
        cx = sum(s.pos_x for _, s in top_k) / len(top_k)
        cy = sum(s.pos_y for _, s in top_k) / len(top_k)
    else:
        cx = sum(sim * s.pos_x for sim, s in top_k) / total_weight
        cy = sum(sim * s.pos_y for sim, s in top_k) / total_weight

    return _jittered(cx, cy)


def _jittered(x: float, y: float) -> tuple[float, float]:
    return (
        x + random.uniform(-_JITTER_SCALE, _JITTER_SCALE),
        y + random.uniform(-_JITTER_SCALE, _JITTER_SCALE),
    )
