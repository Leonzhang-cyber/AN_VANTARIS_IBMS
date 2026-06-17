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
