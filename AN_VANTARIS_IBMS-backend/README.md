# imbs-sysytem

#### 介绍
{**以下是 Gitee 平台说明，您可以替换此简介**
Gitee 是 OSCHINA 推出的基于 Git 的代码托管平台（同时支持 SVN）。专为开发者提供稳定、高效、安全的云端软件开发协作平台
无论是个人、团队、或是企业，都能够用 Gitee 实现代码托管、项目管理、协作开发。企业项目请看 [https://gitee.com/enterprises](https://gitee.com/enterprises)}

#### 软件架构
软件架构说明


#### 安装教程

**Local smoke (macOS, Python ≥3.11 required)**

System Python 3.9 is insufficient for pinned dependencies. Install Python 3.11 first:

```bash
brew install python@3.11   # installs /usr/local/bin/python3.11
python3.11 --version       # expect 3.11.x
```

Then create venv and install smoke deps:

```bash
cd AN_VANTARIS_IBMS-backend
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements-macos-smoke.txt
```

If pip reports invalid requirements (UTF-16 encoding in `requirements.txt`), convert at install time without editing the repo file:

```bash
iconv -f UTF-16LE -t UTF-8 requirements.txt > /tmp/ibms-requirements-utf8.txt
echo "-r /tmp/ibms-requirements-utf8.txt" > /tmp/ibms-macos-smoke-utf8.txt
pip install -r /tmp/ibms-macos-smoke-utf8.txt
```

Start local-smoke server (no `.env` required for bind; dev DB fallbacks apply):

```bash
IBMS_ENV=local-smoke PYTHONPATH=. PYTHONUNBUFFERED=1 python -u src/main.py
```

Server defaults to `http://127.0.0.1:5001` in `local-smoke` mode. Blockchain and IoT DeviceManager startup are skipped. Do not commit `.env` — use `.env.example` as reference only.

**Dev JWT smoke (approved, non-production)**

For local JWT verification only — do **not** commit tokens or create `.env`:

```bash
# Generate 15-minute token to /tmp only (uses dev fallback JWT secret)
IBMS_ENV=local-smoke PYTHONPATH=. python - <<'PY' > /tmp/ibms-local-smoke-token.txt
from datetime import datetime, timedelta, timezone
import jwt
from src.common.config.default import Config
payload = {
    "sub": "did:ibms:smoke:dev:local",
    "iat": datetime.now(timezone.utc),
    "exp": datetime.now(timezone.utc) + timedelta(minutes=15),
    "scope": "local-smoke",
}
print(jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256"))
PY

# Use once, then delete
curl -H "Authorization: Bearer $(cat /tmp/ibms-local-smoke-token.txt)" http://127.0.0.1:5001/api/system/menus
rm -f /tmp/ibms-local-smoke-token.txt
```

Never log or commit the token. Do not inject into browser localStorage.

**Local MySQL install (MYSQL-LOCAL-INSTALL-1)**

Install and start Homebrew MySQL before DB smoke:

```bash
brew install mysql          # skip if mysql --version works
brew services start mysql
mysql -uroot -e "SELECT VERSION();"
```

See `docs/architecture/IBMS_MYSQL_LOCAL_INSTALL_1.md`. Fresh Homebrew install uses empty root password (localhost only). Do not commit credentials.

**Local MySQL smoke (DB-LOCAL-SMOKE-EXEC-A)**

System read APIs (`GET /api/system/menus`, `/permissions`, `/versions`) require a disposable local MySQL instance.

1. Ensure MySQL is running (see above).
2. Create disposable DB/user with shell-only credentials — use `<LOCAL_SMOKE_DB_PASSWORD>`, never commit.
3. Apply ORM-aligned smoke DDL — see `docs/architecture/IBMS_DB_LOCAL_SMOKE_MINIMAL_DDL.md`.
4. Start backend with shell env overrides (no `.env` file):

```bash
export IBMS_ENV=local-smoke
export IBMS_DB_HOST=127.0.0.1
export IBMS_DB_PORT=3306
export IBMS_DB_NAME=ibms_db
export IBMS_DB_USER=ibms_user
export IBMS_DB_PASSWORD='<LOCAL_SMOKE_DB_PASSWORD>'
PYTHONPATH=. python src/main.py
```

5. Run GET-only JWT smoke — see `docs/architecture/IBMS_DB_LOCAL_SMOKE_EXEC_A.md`.

Boundary: IBMS only — stop if UFMS content appears. Do not connect to production DB.

**PostgreSQL database URI (POSTGRES-CONFIG-ABSTRACTION-1)**

Runtime DB selection is URI-first. Set `IBMS_DATABASE_URL` in shell (no `.env` commit):

```bash
export IBMS_DATABASE_URL="postgresql+psycopg://ibms_user:<LOCAL_SMOKE_DB_PASSWORD>@127.0.0.1:5432/ibms_db"
# postgresql:// and postgres:// are normalized to postgresql+psycopg://
```

If `IBMS_DATABASE_URL` is unset, legacy MySQL fallback (`mysql+pymysql://` via `IBMS_DB_*`) still applies.

See `docs/architecture/IBMS_POSTGRES_CONFIG_ABSTRACTION_1.md`.

**PostgreSQL local install (POSTGRES-LOCAL-INSTALL-1)**

Install and start Homebrew PostgreSQL before smoke execution:

```bash
brew install postgresql@16    # skip if psql --version works
brew services start postgresql@16
export PATH="/usr/local/opt/postgresql@16/bin:$PATH"
psql postgres -c "SELECT version();"
```

See `docs/architecture/IBMS_POSTGRES_LOCAL_INSTALL_1.md`. No IBMS DB/user created in install task.

**PostgreSQL local smoke result (POSTGRES-LOCAL-SMOKE-EXEC-1)**

PostgreSQL local smoke passed. PostgreSQL is the canonical target database. Smoke-only DDL is not production migration.

Status: **PASS**. Local smoke used `postgresql+psycopg://` with disposable local DB only.

- GET `/api/system/menus`, `/api/system/permissions`, `/api/system/versions` returned 200 with valid dev JWT
- No production DB or customer data used
- Smoke DDL is not production migration
- See `docs/architecture/IBMS_POSTGRES_LOCAL_SMOKE_EXEC_1.md` and `docs/architecture/IBMS_POSTGRES_LOCAL_SMOKE_RESULTS_1.md`

**PostgreSQL driver (POSTGRES-DEPS-PREP-1)**

PostgreSQL is the target canonical DB.

```bash
# After activating .venv — install new driver (UTF-16LE requirements workaround if needed)
iconv -f UTF-16LE -t UTF-8 requirements.txt > /tmp/ibms-requirements-utf8.txt
pip install "psycopg[binary]==3.2.13"   # or pip install -r /tmp/ibms-requirements-utf8.txt
python -c "import psycopg, pymysql; print('drivers ok')"
```

- `psycopg[binary]==3.2.13` — PostgreSQL target driver
- `PyMySQL==1.1.2` — retained for legacy compatibility
- See `docs/architecture/IBMS_POSTGRES_DEPS_PREP_1.md`

**PostgreSQL migration framework baseline (POSTGRES-MIGRATION-FRAMEWORK-RECOVERY-1)**

Migration framework baseline is prepared for IBMS PostgreSQL transition.

- Added dependencies: `Flask-Migrate==4.0.7`, `alembic==1.17.2`
- Baseline files created: `alembic.ini`, `migrations/`
- Import verification passed: `alembic`, `flask_migrate`
- No `flask db upgrade`, no `alembic upgrade`, no autogenerate, no production DB
- See:
  - `docs/architecture/IBMS_POSTGRES_MIGRATION_FRAMEWORK_1.md`
  - `docs/security/IBMS_POSTGRES_MIGRATION_FRAMEWORK_1_RISK_REVIEW.md`
  - `docs/architecture/IBMS_POSTGRES_MIGRATION_FRAMEWORK_RECOVERY_1.md`

1.  xxxx
2.  xxxx
3.  xxxx

#### 使用说明

1.  xxxx
2.  xxxx
3.  xxxx

#### 参与贡献

1.  Fork 本仓库
2.  新建 Feat_xxx 分支
3.  提交代码
4.  新建 Pull Request


#### 特技

1.  使用 Readme\_XXX.md 来支持不同的语言，例如 Readme\_en.md, Readme\_zh.md
2.  Gitee 官方博客 [blog.gitee.com](https://blog.gitee.com)
3.  你可以 [https://gitee.com/explore](https://gitee.com/explore) 这个地址来了解 Gitee 上的优秀开源项目
4.  [GVP](https://gitee.com/gvp) 全称是 Gitee 最有价值开源项目，是综合评定出的优秀开源项目
5.  Gitee 官方提供的使用手册 [https://gitee.com/help](https://gitee.com/help)
6.  Gitee 封面人物是一档用来展示 Gitee 会员风采的栏目 [https://gitee.com/gitee-stars/](https://gitee.com/gitee-stars/)
