GALAXY_COLOR_PALETTE = [
    "#4A9EFF",
    "#FF7043",
    "#66BB6A",
    "#AB47BC",
    "#FFA726",
    "#26C6DA",
    "#EC407A",
    "#8D6E63",
]


def default_galaxy_color(existing_count: int) -> str:
    """기존 은하 수를 기준으로 기본 색상을 결정적으로 순환 선택한다."""
    return GALAXY_COLOR_PALETTE[existing_count % len(GALAXY_COLOR_PALETTE)]
