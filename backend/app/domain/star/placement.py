import random
from typing import Protocol

import numpy as np


class PlacedStar(Protocol):
    """신규 항성 배치에 필요한 기존 항성 필드."""

    embedding: list[float]
    pos_x: float
    pos_y: float


_JITTER_SCALE = 6.0


def place_new_star(
    existing_stars: list[PlacedStar],
    new_embedding: list[float],
    k: int = 3,
) -> tuple[float, float]:
    """
    기존 좌표는 고정한 채 신규 항성의 좌표만 계산한다.

    기존 항성이 없으면 원점, 1개면 오른쪽 근처, 2개 이상이면 유사도 상위 k개의
    가중 중심에 작은 jitter를 더한다.
    """
    if not existing_stars:
        return 0.0, 0.0

    if len(existing_stars) == 1:
        sole = existing_stars[0]
        return _jittered(sole.pos_x + 12.0, sole.pos_y)

    new_vec = np.array(new_embedding, dtype=np.float32)
    new_norm = np.linalg.norm(new_vec)
    if new_norm == 0:
        return _jittered(0.0, 0.0)

    similarities: list[tuple[float, PlacedStar]] = []
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
