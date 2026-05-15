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

# ── 안전 정책 센서 ────────────────────────────────────────
FORBIDDEN_INIT=$(find "$BACKEND/app" -path '*/__init__.py' -type f 2>/dev/null || true)
if [[ -n "$FORBIDDEN_INIT" ]]; then
    FAILED=1
    REPORT="$REPORT\n[FAIL] forbidden __init__.py:\n$FORBIDDEN_INIT\nPython 3.12 implicit namespace package 정책: backend/app/**/__init__.py 생성 금지."
fi

if grep -q 'explicit_package_bases' "$BACKEND/pyproject.toml" 2>/dev/null; then
    FAILED=1
    REPORT="$REPORT\n[FAIL] forbidden mypy setting:\nbackend/pyproject.toml contains explicit_package_bases\n__init__.py 생성을 유도하는 mypy 설정을 금지합니다."
fi

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

    # mypy — __init__.py 없이 namespace package를 쓰므로 CLI 플래그로 package base 명시
    MYPY_OUT=$(cd "$BACKEND" && "$VENV/mypy" --explicit-package-bases app/ 2>&1)
    MYPY_REAL_ERRORS=$(echo "$MYPY_OUT" | grep "error:" || true)
    if [[ -n "$MYPY_REAL_ERRORS" ]]; then
        FAILED=1
        REPORT="$REPORT\n[FAIL] mypy:\n$(echo "$MYPY_REAL_ERRORS" | head -10)"
    else
        echo "[quality-gate] ✓ mypy"
    fi

    # pytest — 명시적이고 안전한 로컬 TEST_DATABASE_URL에서만 실행
    TEST_DB_URL="${TEST_DATABASE_URL:-}"
    DB_REACHABLE=false
    DB_SAFE=false

    if [[ -n "$TEST_DB_URL" ]]; then
        DB_HOST=$(echo "$TEST_DB_URL" | python3 -c "import sys, urllib.parse; p=urllib.parse.urlparse(sys.stdin.read().strip()); print(p.hostname or '')" 2>/dev/null || echo "")
        DB_PORT=$(echo "$TEST_DB_URL" | python3 -c "import sys, urllib.parse; p=urllib.parse.urlparse(sys.stdin.read().strip()); print(p.port or 5432)" 2>/dev/null || echo "5432")
        DB_NAME=$(echo "$TEST_DB_URL" | python3 -c "import sys, urllib.parse; p=urllib.parse.urlparse(sys.stdin.read().strip()); print((p.path.rsplit('/', 1)[-1]) if p.path else '')" 2>/dev/null || echo "")
        if [[ "$DB_HOST" == "localhost" || "$DB_HOST" == "127.0.0.1" || "$DB_HOST" == "::1" ]] \
            && echo "$DB_NAME" | grep -qi 'test'; then
            DB_SAFE=true
        fi
        if [[ "$DB_SAFE" == "true" ]] && nc -z -w3 "$DB_HOST" "$DB_PORT" 2>/dev/null; then
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
            echo "[quality-gate] ⚠ pytest 건너뜀 — 안전한 로컬 TEST_DATABASE_URL 미설정"
            echo "[quality-gate]   조건: host localhost/127.0.0.1/::1, database name contains 'test'"
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
