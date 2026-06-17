# src/common/utils/jwt_util.py
import jwt
from functools import wraps
from flask import request, current_app, g
from datetime import datetime, timedelta
from src.common.models.response import Result


def _get_secret() -> str:
    """安全获取 JWT 密钥，确保其为非空字符串"""
    secret = current_app.config.get('JWT_SECRET_KEY')
    if not isinstance(secret, str) or not secret.strip():
        raise RuntimeError(
            "❌ JWT_SECRET_KEY 未配置或无效！请在配置中设置一个非空字符串。"
        )
    return secret.strip()

def create_jwt(payload: dict, expires_in_hours: int = None) -> str:
    """
    生成 JWT token
    :param payload: 需要编码的载荷（必须包含 sub 字段作为用户 DID_Back）
    :param expires_in_hours: 过期小时数，默认使用配置中的值
    :return: JWT 字符串
    """
    if expires_in_hours is None:
        expires_in_hours = current_app.config.get('JWT_EXPIRATION_HOURS', 8)

    payload_copy = payload.copy()
    exp = datetime.utcnow() + timedelta(hours=expires_in_hours)
    payload_copy['exp'] = exp
    payload_copy['iat'] = datetime.utcnow()

    secret = _get_secret()  # 👈 使用安全获取函数
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')

    token = jwt.encode(payload_copy, secret, algorithm=algorithm)
    return token

def decode_jwt(token: str) -> dict:
    """
    解码并验证 JWT
    :param token: JWT 字符串
    :return: 解码后的 payload 字典
    :raises: jwt.InvalidTokenError 如果 token 无效或过期
    """
    secret = _get_secret()  # 👈 同样使用安全获取
    algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
    payload = jwt.decode(token, secret, algorithms=[algorithm])
    return payload

def jwt_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return Result.error(code=401, message="Unauthorized")

        token = auth_header.split(' ')[1]
        try:
            payload = decode_jwt(token)
        except jwt.ExpiredSignatureError:
            return Result.error(code=401, message="Unauthorized")
        except jwt.InvalidTokenError:
            return Result.error(code=401, message="Unauthorized")

        g.jwt_payload = payload
        g.current_did = payload.get('sub')

        user_permissions = []
        for key in ('perms', 'permission_codes', 'permissions'):
            raw = payload.get(key)
            if isinstance(raw, (list, tuple)) and raw:
                user_permissions = list(raw)
                break

        g.user_permissions = user_permissions
        g.current_principal = {
            'did': g.current_did,
            'permissions': user_permissions,
        }
        # 兼容旧字段名
        g.frontend_perms = payload.get('frontend_perms', [])
        g.api_perms = payload.get('api_perms', [])

        return func(*args, **kwargs)
    return wrapper

def get_current_permissions() -> list:
    """获取当前用户的权限编码列表"""
    return getattr(g, 'user_permissions', [])

def get_current_frontend_perms() -> list:
    return getattr(g, 'frontend_perms', [])

def get_current_api_perms() -> list:
    return getattr(g, 'api_perms', [])


def get_current_did() -> str:
    """获取当前请求中的 DID_Back（必须在 @jwt_required 装饰器之后调用）"""
    return getattr(g, 'current_did', None)


def get_current_frontend_perms() -> list:
    """获取当前用户的 frontend_permissions"""
    return getattr(g, 'frontend_perms', [])


def get_current_api_perms() -> list:
    """获取当前用户的 api_permissions"""
    return getattr(g, 'api_perms', [])


def verify_api_permission(required_pattern: str, method: str = None) -> bool:
    """
    检查当前用户的 api_perms 是否匹配某个具体的 API 模式。
    支持通配符 * 匹配路径段。
    示例：required_pattern = "/api/devices/*", method = "GET"
         若用户拥有 "GET /api/devices/*" 或 "GET /api/devices/1" 等模式即可放行。
    实际使用时建议在中间件中统一校验，此处提供辅助函数。
    """
    import fnmatch
    api_perms = get_current_api_perms()
    if method is None:
        method = request.method
    required = f"{method} {required_pattern}"
    for pattern in api_perms:
        # pattern 格式例如 "GET /api/devices/*"
        if fnmatch.fnmatch(required, pattern):
            return True
    return False