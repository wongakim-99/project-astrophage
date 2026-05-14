#!/usr/bin/env bash
# Stop hook — 에이전트 작업 종료 전 품질 게이트
# 모든 센서를 통과해야만 작업 완료로 인정한다.
# exit 2 → 종료 차단 + 실패 내용을 에이전트에게 전달

set -uo pipefail

ROOT="/Users/gimgawon/Desktop/github-repo/project-astrophage"
BACKEND="$ROOT/backend"
VENV="$BACKEND/.venv/bin"

FAILED=0
REPORT=""

# ── 변경된 파일이 있을 때만 실행 ──────────────────────────
CHANGED=$(git -C "$ROOT" diff --name-only HEAD 2>/dev/null || echo "")
CHANGED_STAGED=$(git -C "$ROOT" diff --cached --name-only 2>/dev/null || echo "")
ALL_CHANGED="$CHANGED $CHANGED_STAGED"

HAS_PYTHON=$(echo "$ALL_CHANGED" | grep -E '\.py$' || true)
HAS_TS=$(echo "$ALL_CHANGED" | grep -E '\.(ts|tsx)$' || true)

# ── Python 센서 ────────────────────────────────────────────
if [[ -n "$HAS_PYTHON" ]]; then
    echo "[quality-gate] Python 변경 감지 → 센서 실행"

    # ruff
    RUFF_OUT=$(cd "$BACKEND" && "$VENV/ruff" check app/ 2>&1)
    if [[ $? -ne 0 ]]; then
        FAILED=1
        REPORT="$REPORT\n[FAIL] ruff:\n$RUFF_OUT"
    else
        echo "[quality-gate] ✓ ruff"
    fi

    # mypy
    MYPY_OUT=$(cd "$BACKEND" && "$VENV/mypy" app/ 2>&1)
    if echo "$MYPY_OUT" | grep -q "error:"; then
        FAILED=1
        REPORT="$REPORT\n[FAIL] mypy:\n$(echo "$MYPY_OUT" | grep 'error:' | head -10)"
    else
        echo "[quality-gate] ✓ mypy"
    fi

    # pytest — 테스트 파일이 있을 때만
    if ls "$BACKEND/tests/test_"*.py 1>/dev/null 2>&1; then
        PYTEST_OUT=$(cd "$BACKEND" && "$VENV/python" -m pytest tests/ -v --tb=short -q 2>&1)
        if [[ $? -ne 0 ]]; then
            FAILED=1
            REPORT="$REPORT\n[FAIL] pytest:\n$(echo "$PYTEST_OUT" | tail -20)"
        else
            echo "[quality-gate] ✓ pytest"
        fi
    fi
fi

# ── TypeScript 센서 ────────────────────────────────────────
if [[ -n "$HAS_TS" ]]; then
    echo "[quality-gate] TypeScript 변경 감지 → 센서 실행"

    FRONTEND="$ROOT/frontend"
    if [[ -f "$FRONTEND/node_modules/.bin/tsc" ]]; then
        TSC_OUT=$(cd "$FRONTEND" && node_modules/.bin/tsc --noEmit 2>&1)
        if [[ $? -ne 0 ]]; then
            FAILED=1
            REPORT="$REPORT\n[FAIL] tsc:\n$(echo "$TSC_OUT" | head -20)"
        else
            echo "[quality-gate] ✓ tsc"
        fi
    fi
fi

# ── 결과 ──────────────────────────────────────────────────
if [[ $FAILED -ne 0 ]]; then
    echo ""
    echo "[quality-gate] 센서 실패 — 작업 완료 선언 차단"
    echo -e "$REPORT"
    echo ""
    echo "위 문제를 해결한 후 다시 완료 선언하세요."
    exit 2
fi

echo "[quality-gate] 모든 센서 통과 ✓"
exit 0
