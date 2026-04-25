import random

import numpy as np

from app.models.star import Star

_JITTER_SCALE = 0.5  # 새 항성에 적용할 좌표 단위 랜덤 오프셋


def place_new_star(
    existing_stars: list[Star],
    new_embedding: list[float],
    k: int = 3,
) -> tuple[float, float]:
    """
    기존 항성 좌표를 다시 계산하지 않고 새 항성의 (x, y) 위치를 정한다.

    전략:
    - 기존 항성이 0개면 원점에 배치
    - 기존 항성이 1개면 해당 항성 기준 (1.0, 0.0)에 배치
    - 기존 항성이 2개 이상이면 유사도 상위 k개의 가중 중심 + jitter 적용

    Args:
        existing_stars: 같은 Galaxy에 이미 저장된 기존 Star 목록.
        new_embedding: 새 Star의 title/content에서 만든 임베딩 벡터.
        k: 좌표 가중 중심 계산에 사용할 유사 이웃 최대 개수.
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
    # 의미적으로 가장 가까운 이웃만 배치에 사용한다. 기존 좌표는 anchor로 읽기만 하고 쓰지 않는다.
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
    """
    의미적으로 겹치는 이웃 항성도 클릭 가능하도록 작은 오프셋을 더한다.

    Args:
        x: 기준 x 좌표.
        y: 기준 y 좌표.
    """
    return (
        x + random.uniform(-_JITTER_SCALE, _JITTER_SCALE),
        y + random.uniform(-_JITTER_SCALE, _JITTER_SCALE),
    )
