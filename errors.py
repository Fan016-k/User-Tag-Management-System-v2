# errors.py
from fastapi import HTTPException, status
from typing import Optional, Dict, Any, Union
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


# 错误码定义
class ErrorCodes:
    # 用户错误（1xxx）
    USER_NOT_FOUND = "1001"
    USER_ALREADY_EXISTS = "1002"
    INVALID_USER_ID = "1003"

    # 标签错误（2xxx）
    TAG_NOT_FOUND = "2001"
    TAG_ALREADY_EXISTS = "2002"
    INVALID_TAG_NAME = "2003"
    TAG_NOT_ASSOCIATED = "2004"

    # 验证错误（3xxx）
    INVALID_REQUEST_FORMAT = "3001"
    MISSING_REQUIRED_FIELD = "3002"
    INVALID_FIELD_VALUE = "3003"

    # 数据库错误（4xxx）
    DATABASE_ERROR = "4001"
    INTEGRITY_ERROR = "4002"

    # 通用错误（5xxx）
    INTERNAL_SERVER_ERROR = "5001"


# 错误消息模板
ERROR_MESSAGES = {
    # 用户错误
    ErrorCodes.USER_NOT_FOUND: "用户不存在",
    ErrorCodes.USER_ALREADY_EXISTS: "用户已存在",
    ErrorCodes.INVALID_USER_ID: "无效的用户ID",

    # 标签错误
    ErrorCodes.TAG_NOT_FOUND: "标签不存在",
    ErrorCodes.TAG_ALREADY_EXISTS: "标签已存在",
    ErrorCodes.INVALID_TAG_NAME: "无效的标签名称",
    ErrorCodes.TAG_NOT_ASSOCIATED: "用户未关联该标签",

    # 验证错误
    ErrorCodes.INVALID_REQUEST_FORMAT: "请求格式无效",
    ErrorCodes.MISSING_REQUIRED_FIELD: "缺少必填字段",
    ErrorCodes.INVALID_FIELD_VALUE: "字段值无效",

    # 数据库错误
    ErrorCodes.DATABASE_ERROR: "数据库操作错误",
    ErrorCodes.INTEGRITY_ERROR: "数据完整性错误",

    # 通用错误
    ErrorCodes.INTERNAL_SERVER_ERROR: "服务器内部错误"
}

# HTTP 状态码映射
ERROR_STATUS_CODES = {
    # 用户错误
    ErrorCodes.USER_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCodes.USER_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    ErrorCodes.INVALID_USER_ID: status.HTTP_400_BAD_REQUEST,

    # 标签错误
    ErrorCodes.TAG_NOT_FOUND: status.HTTP_404_NOT_FOUND,
    ErrorCodes.TAG_ALREADY_EXISTS: status.HTTP_409_CONFLICT,
    ErrorCodes.INVALID_TAG_NAME: status.HTTP_400_BAD_REQUEST,
    ErrorCodes.TAG_NOT_ASSOCIATED: status.HTTP_404_NOT_FOUND,

    # 验证错误
    ErrorCodes.INVALID_REQUEST_FORMAT: status.HTTP_400_BAD_REQUEST,
    ErrorCodes.MISSING_REQUIRED_FIELD: status.HTTP_400_BAD_REQUEST,
    ErrorCodes.INVALID_FIELD_VALUE: status.HTTP_400_BAD_REQUEST,

    # 数据库错误
    ErrorCodes.DATABASE_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR,
    ErrorCodes.INTEGRITY_ERROR: status.HTTP_409_CONFLICT,

    # 通用错误
    ErrorCodes.INTERNAL_SERVER_ERROR: status.HTTP_500_INTERNAL_SERVER_ERROR
}


def get_error_response(
        error_code: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
) -> Dict[str, Union[str, Dict[str, Any]]]:
    """
    生成标准化的错误响应

    参数:
        error_code: 错误码（来自 ErrorCodes）
        message: 自定义错误信息（可选）
        details: 附加错误详情（可选）

    返回:
        标准化的错误响应字典
    """
    return {
        "status": "错误",
        "code": error_code,
        "message": message or ERROR_MESSAGES.get(error_code, "未知错误"),
        "details": details
    }


def raise_http_exception(
        error_code: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
) -> None:
    """
    抛出标准格式的 HTTP 异常

    参数:
        error_code: 错误码（来自 ErrorCodes）
        message: 自定义错误信息（可选）
        details: 附加错误详情（可选）

    异常:
        HTTPException: FastAPI 的 HTTP 异常，包含合适的状态码和错误详情
    """
    status_code = ERROR_STATUS_CODES.get(error_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
    error_response = get_error_response(error_code, message, details)
    raise HTTPException(status_code=status_code, detail=error_response)


def handle_database_error(error: SQLAlchemyError) -> None:
    """
    处理 SQLAlchemy 异常并抛出对应的 HTTP 异常

    参数:
        error: SQLAlchemy 异常对象

    异常:
        HTTPException: FastAPI 的 HTTP 异常，包含合适的状态码和错误详情
    """
    if isinstance(error, IntegrityError):
        # 处理完整性错误（唯一约束、外键等）
        error_message = str(error)
        if "UNIQUE constraint failed: users.username" in error_message:
            raise_http_exception(ErrorCodes.USER_ALREADY_EXISTS)
        elif "UNIQUE constraint failed: tags.tag_name" in error_message:
            raise_http_exception(ErrorCodes.TAG_ALREADY_EXISTS)
        else:
            raise_http_exception(ErrorCodes.INTEGRITY_ERROR, str(error))
    else:
        # 处理其他数据库错误
        raise_http_exception(ErrorCodes.DATABASE_ERROR, str(error))
