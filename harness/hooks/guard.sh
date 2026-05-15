#!/usr/bin/env bash
# PreToolUse hook — 위험 명령 사전 차단
# Claude Code가 도구 실행 전 이 스크립트를 호출한다.
# exit 2 → 차단 + stdout 메시지를 에이전트에게 전달
# exit 0 → 통과

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

# Bash 툴이 아니면 통과
if [[ "$TOOL_NAME" != "Bash" ]]; then
    exit 0
fi

COMMAND=$(echo "$INPUT" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('tool_input', {}).get('command', ''))
except:
    print('')
" 2>/dev/null || echo "")

# ── 차단 패턴 ──────────────────────────────────────────────
# 1. git commit — CLAUDE.md: 커밋은 사용자가 직접 실행
if echo "$COMMAND" | grep -qE '^\s*git\s+commit'; then
    echo "[guard] BLOCKED: 'git commit'"
    echo "CLAUDE.md 규칙: 커밋은 사용자가 직접 실행합니다. AI 에이전트 실행 금지."
    exit 2
fi

# 2. git push — 원격 반영은 사용자 확인 필요
if echo "$COMMAND" | grep -qE '^\s*git\s+push'; then
    echo "[guard] BLOCKED: 'git push'"
    echo "원격 push는 사용자가 직접 실행해야 합니다."
    exit 2
fi

# 3. git reset --hard / git checkout -- / git clean -f — 변경사항 파괴
if echo "$COMMAND" | grep -qE 'git\s+(reset\s+--hard|checkout\s+--|clean\s+-f)'; then
    echo "[guard] BLOCKED: 파괴적 git 명령"
    echo "변경사항을 폐기하는 git 명령은 사용자 확인 후 실행하세요."
    exit 2
fi

# 4. rm -rf — 재귀 삭제
if echo "$COMMAND" | grep -qE 'rm\s+-[a-zA-Z]*r[a-zA-Z]*f|rm\s+-[a-zA-Z]*f[a-zA-Z]*r'; then
    echo "[guard] BLOCKED: 'rm -rf'"
    echo "재귀 삭제 명령은 차단됩니다. 필요하면 사용자가 직접 실행하세요."
    exit 2
fi

# 5. DROP TABLE / TRUNCATE — DB 파괴
if echo "$COMMAND" | grep -qiE 'DROP\s+TABLE|TRUNCATE\s+TABLE'; then
    echo "[guard] BLOCKED: DB 파괴 명령"
    echo "DROP TABLE / TRUNCATE 는 Alembic 마이그레이션을 통해서만 처리합니다."
    exit 2
fi

# 6. pos_x / pos_y 직접 UPDATE — 좌표 고정 규칙 위반
if echo "$COMMAND" | grep -qE 'UPDATE.*(pos_x|pos_y)|SET\s+(pos_x|pos_y)'; then
    echo "[guard] BLOCKED: pos_x / pos_y 직접 UPDATE"
    echo "CLAUDE.md 규칙: 항성 좌표는 생성 시 1회 계산 후 고정. 덮어쓰기 금지."
    exit 2
fi

# 7. alembic downgrade — 프로덕션 데이터 위험
if echo "$COMMAND" | grep -qE 'alembic\s+downgrade'; then
    echo "[guard] BLOCKED: 'alembic downgrade'"
    echo "다운그레이드는 데이터 손실 위험이 있습니다. 사용자가 직접 실행하세요."
    exit 2
fi

# 8. pytest에 앱 DB URL을 테스트 DB로 주입 — 테스트 fixture가 drop_all/create_all 실행
if echo "$COMMAND" | grep -qE 'TEST_DATABASE_URL\s*=\s*\$DATABASE_URL|env\[[\"'\'']TEST_DATABASE_URL[\"'\'']\]\s*=\s*env\[[\"'\'']DATABASE_URL[\"'\'']\]|os\.environ\[[\"'\'']TEST_DATABASE_URL[\"'\'']\]\s*=\s*os\.environ\[[\"'\'']DATABASE_URL[\"'\'']\]'; then
    echo "[guard] BLOCKED: TEST_DATABASE_URL reuses DATABASE_URL"
    echo "테스트 fixture는 연결된 DB에서 drop_all/create_all을 실행합니다. 앱 DB를 테스트 DB로 재사용 금지."
    exit 2
fi

# 9. 원격 테스트 DB로 pytest 실행 — Supabase/dev/prod 스키마 삭제 방지
if echo "$COMMAND" | grep -qE 'pytest|python\s+-m\s+pytest'; then
    TEST_DB_URL="${TEST_DATABASE_URL:-}"
    if [[ -n "$TEST_DB_URL" ]]; then
        TEST_DB_HOST=$(echo "$TEST_DB_URL" | python3 -c "import sys, urllib.parse; p=urllib.parse.urlparse(sys.stdin.read().strip()); print(p.hostname or '')" 2>/dev/null || echo "")
        TEST_DB_NAME=$(echo "$TEST_DB_URL" | python3 -c "import sys, urllib.parse; p=urllib.parse.urlparse(sys.stdin.read().strip()); print((p.path.rsplit('/', 1)[-1]) if p.path else '')" 2>/dev/null || echo "")
        if [[ "$TEST_DB_HOST" != "localhost" && "$TEST_DB_HOST" != "127.0.0.1" && "$TEST_DB_HOST" != "::1" ]]; then
            echo "[guard] BLOCKED: pytest with remote TEST_DATABASE_URL"
            echo "테스트 DB reset은 로컬 DB에서만 허용합니다. host=$TEST_DB_HOST"
            exit 2
        fi
        if ! echo "$TEST_DB_NAME" | grep -qi 'test'; then
            echo "[guard] BLOCKED: pytest with non-test database name"
            echo "TEST_DATABASE_URL database name must contain 'test'. database=$TEST_DB_NAME"
            exit 2
        fi
    fi
fi

# 10. Python implicit namespace package 정책 — backend/app/**/__init__.py 생성 금지
if echo "$COMMAND" | grep -qE '(__init__\.py|explicit_package_bases)'; then
    echo "[guard] BLOCKED: Python package marker/config change"
    echo "CLAUDE.md 규칙: Python 3.12 implicit namespace package 사용. __init__.py 생성 및 explicit_package_bases 설정 금지."
    exit 2
fi

exit 0
