#!/usr/bin/env bash
# PostToolUse hook — 파일 수정 후 자동 린트/타입 검증
# Edit 또는 Write 툴 실행 직후 호출된다.

set -uo pipefail

INPUT=$(cat)

TOOL_NAME=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_name', ''))
except:
    print('')
" 2>/dev/null || echo "")

# Edit / Write 툴만 대상
if [[ "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "Write" ]]; then
    exit 0
fi

FILE_PATH=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    inp = d.get('tool_input', {})
    print(inp.get('file_path', ''))
except:
    print('')
" 2>/dev/null || echo "")

if [[ -z "$FILE_PATH" ]]; then
    exit 0
fi

ROOT="/Users/gimgawon/Desktop/github-repo/project-astrophage"

# ── Python 파일 ────────────────────────────────────────────
if [[ "$FILE_PATH" == *.py ]]; then
    BACKEND="$ROOT/backend"
    VENV="$BACKEND/.venv/bin"

    echo "[lint-fix] Python 파일 감지: $FILE_PATH"

    # ruff — 자동 수정 후 잔존 오류 확인
    if [[ -x "$VENV/ruff" ]]; then
        "$VENV/ruff" check --fix "$FILE_PATH" 2>&1 || true
        RUFF_OUT=$("$VENV/ruff" check "$FILE_PATH" 2>&1)
        if [[ -n "$RUFF_OUT" ]]; then
            echo "[lint-fix] ruff 경고:"
            echo "$RUFF_OUT"
        fi
    fi

    # mypy — 해당 파일만 타입 검사
    if [[ -x "$VENV/mypy" ]]; then
        MYPY_OUT=$("$VENV/mypy" "$FILE_PATH" --ignore-missing-imports 2>&1)
        if echo "$MYPY_OUT" | grep -q "error:"; then
            echo "[lint-fix] mypy 오류:"
            echo "$MYPY_OUT"
        fi
    fi
fi

# ── TypeScript / TSX 파일 ──────────────────────────────────
if [[ "$FILE_PATH" == *.ts || "$FILE_PATH" == *.tsx ]]; then
    FRONTEND="$ROOT/frontend"

    echo "[lint-fix] TypeScript 파일 감지: $FILE_PATH"

    # eslint
    if [[ -f "$FRONTEND/node_modules/.bin/eslint" ]]; then
        "$FRONTEND/node_modules/.bin/eslint" --fix "$FILE_PATH" 2>&1 || true
    fi

    # tsc — 전체 프로젝트 타입 확인 (증분)
    if [[ -f "$FRONTEND/node_modules/.bin/tsc" ]]; then
        cd "$FRONTEND"
        TSC_OUT=$(node_modules/.bin/tsc --noEmit 2>&1 | head -20)
        if [[ -n "$TSC_OUT" ]]; then
            echo "[lint-fix] tsc 오류 (상위 20줄):"
            echo "$TSC_OUT"
        fi
    fi
fi

exit 0
