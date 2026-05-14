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

    # mypy — "Duplicate module" 은 __init__.py 미사용 프로젝트의 known issue라 제외
    MYPY_OUT=$(cd "$BACKEND" && "$VENV/mypy" app/ 2>&1)
    MYPY_REAL_ERRORS=$(echo "$MYPY_OUT" | grep "error:" | grep -v "Duplicate module" || true)
    if [[ -n "$MYPY_REAL_ERRORS" ]]; then
        FAILED=1
        REPORT="$REPORT\n[FAIL] mypy:\n$(echo "$MYPY_REAL_ERRORS" | head -10)"
    else
        echo "[quality-gate] ✓ mypy"
    fi

    # pytest — TEST_DATABASE_URL 또는 로컬 DB가 응답할 때만 실행
    TEST_DB_URL="${TEST_DATABASE_URL:-}"
    DB_REACHABLE=false

    if [[ -n "$TEST_DB_URL" ]]; then
        # Supabase 등 외부 DB: URL에서 호스트/포트 추출 후 연결 확인
        DB_HOST=$(echo "$TEST_DB_URL" | python3 -c "import sys,re; m=re.search(r'@([^:/]+):(\d+)', sys.stdin.read()); print(m.group(1) if m else '')" 2>/dev/null || echo "")
        DB_PORT=$(echo "$TEST_DB_URL" | python3 -c "import sys,re; m=re.search(r'@([^:/]+):(\d+)', sys.stdin.read()); print(m.group(2) if m else '5432')" 2>/dev/null || echo "5432")
        if [[ -n "$DB_HOST" ]] && nc -z -w3 "$DB_HOST" "$DB_PORT" 2>/dev/null; then
            DB_REACHABLE=true
        fi
    else
        # 로컬 기본 DB 확인
        if nc -z -w2 localhost 5432 2>/dev/null; then
            DB_REACHABLE=true
        fi
    fi

    if ls "$BACKEND/tests/test_"*.py 1>/dev/null 2>&1; then
        if [[ "$DB_REACHABLE" == "true" ]]; then
            PYTEST_OUT=$(cd "$BACKEND" && "$VENV/python" -m pytest tests/ -v --tb=short -q 2>&1)
            if [[ $? -ne 0 ]]; then
                FAILED=1
                REPORT="$REPORT\n[FAIL] pytest:\n$(echo "$PYTEST_OUT" | tail -20)"
            else
                echo "[quality-gate] ✓ pytest"
            fi
        else
            echo "[quality-gate] ⚠ pytest 건너뜀 — 테스트 DB 미연결 (TEST_DATABASE_URL 설정 필요)"
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
