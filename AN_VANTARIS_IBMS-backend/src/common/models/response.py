# src/common/models/response.py
from dataclasses import dataclass, asdict
from typing import Optional, Any
from flask import jsonify


@dataclass
class Result:
    """全局统一 API 响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[Any] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_response(self):
        """返回 Flask Response 对象"""
        return jsonify(self.to_dict()), self.code

    @classmethod
    def success(cls, data: Any = None, message: str = "success"):
        """成功响应快捷方法"""
        return cls(code=200, message=message, data=data).to_response()

    @classmethod
    def error(cls, code: int = 500, message: str = "error", data: Any = None):
        """失败响应快捷方法"""
        return cls(code=code, message=message, data=data).to_response()


class ErrorCode:
    """业务错误码常量（可按模块扩展）"""
    # 通用错误
    PARAM_ERROR = 40000
    SERVER_ERROR = 50000
    UNAUTHORIZED = 40001
    FORBIDDEN = 40003

    # DID_Back 模块专用
    DID_INVALID = 41001
    DID_RESOLVE_FAILED = 41002
    VC_INVALID = 41003
    VP_VERIFY_FAILED = 41004
    ISSUER_UNTRUSTED = 41005
    PERMISSION_DENIED = 41006