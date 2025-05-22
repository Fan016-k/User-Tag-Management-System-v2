# main.py - 网易云音乐用户标签服务主文件
from fastapi import FastAPI, Depends, Path, Body, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from pydantic import ValidationError
import uvicorn

# 导入数据库相关模块
import database as db
from database import get_db
from repository import TagRepository
import schemas
import errors
from errors import ErrorCodes, raise_http_exception

# 初始化数据库
db.init_db()

# 初始化 FastAPI 应用实例
app = FastAPI(
    title="网易云音乐用户标签服务",
    description="用于管理网易云音乐中的用户画像标签的服务",
    version="2.0.0"
)

# 配置跨域中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（开发阶段使用）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有请求方法
    allow_headers=["*"],  # 允许所有请求头
)


# 健康检查接口
@app.get("/ping")
async def ping():
    """
    健康检查接口，用于确认服务是否正在运行
    """
    return {"status": "成功", "message": "用户标签服务正在运行"}


# 创建用户接口
@app.post("/users", response_model=schemas.ApiResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user: schemas.UserCreate = Body(...),
        db_session: Session = Depends(get_db)
):
    """
    创建新用户
    """
    try:
        # 检查用户是否已存在
        existing_user = TagRepository.get_user_by_username(db_session, user.username)
        if existing_user:
            raise_http_exception(ErrorCodes.USER_ALREADY_EXISTS)

        # 创建用户
        new_user = TagRepository.create_user(db_session, user.username)

        return {
            "status": "成功",
            "message": "用户创建成功",
            "data": {
                "user_id": new_user.user_id,
                "username": new_user.username
            }
        }
    except ValidationError as e:
        # 处理数据验证错误
        raise_http_exception(
            ErrorCodes.INVALID_REQUEST_FORMAT,
            "请求数据验证失败",
            {"errors": e.errors()}
        )
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 获取用户信息接口
@app.get("/users/{user_id}", response_model=schemas.ApiResponse)
async def get_user(
        user_id: int = Path(..., gt=0, description="用户ID"),
        db_session: Session = Depends(get_db)
):
    """
    获取用户信息
    """
    try:
        # 根据用户ID查询用户
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            raise_http_exception(ErrorCodes.USER_NOT_FOUND)

        return {
            "status": "成功",
            "message": "成功获取用户信息",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "tags": [tag.tag_name for tag in user.tags]
            }
        }
    except ValidationError as e:
        # 处理路径参数验证错误
        raise_http_exception(
            ErrorCodes.INVALID_USER_ID,
            "无效的用户ID",
            {"errors": e.errors()}
        )
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 获取所有用户接口
@app.get("/users", response_model=schemas.ApiResponse)
async def get_all_users(
        db_session: Session = Depends(get_db)
):
    """
    获取所有用户
    """
    try:
        # 查询所有用户
        users = TagRepository.get_all_users(db_session)

        return {
            "status": "成功",
            "message": "成功获取所有用户",
            "data": {
                "users": [
                    {
                        "user_id": user.user_id,
                        "username": user.username,
                        "tags_count": len(user.tags)
                    }
                    for user in users
                ],
                "total": len(users)
            }
        }
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 获取用户标签接口
@app.get("/users/{user_id}/tags", response_model=schemas.ApiResponse)
async def get_user_tags(
        user_id: int = Path(..., gt=0, description="用户ID"),
        db_session: Session = Depends(get_db)
):
    """
    获取指定用户的所有标签
    """
    try:
        # 查询用户及其标签
        user, tags = TagRepository.get_user_tags(db_session, user_id)

        if not user:
            raise_http_exception(ErrorCodes.USER_NOT_FOUND)

        return {
            "status": "成功",
            "message": "成功获取标签" if tags else "用户没有标签",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "tags": [tag.tag_name for tag in tags]
            }
        }
    except ValidationError as e:
        # 处理路径参数验证错误
        raise_http_exception(
            ErrorCodes.INVALID_USER_ID,
            "无效的用户ID",
            {"errors": e.errors()}
        )
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 添加用户标签接口
@app.post("/users/{user_id}/tags", response_model=schemas.ApiResponse, status_code=status.HTTP_201_CREATED)
async def add_user_tags(
        user_id: int = Path(..., gt=0, description="用户ID"),
        request: schemas.TagAddRequest = Body(...),
        db_session: Session = Depends(get_db)
):
    """
    为指定用户添加一个或多个标签
    """
    try:
        # 验证用户是否存在
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            raise_http_exception(ErrorCodes.USER_NOT_FOUND)

        # 为用户添加标签
        user, tags = TagRepository.add_tags_to_user(db_session, user_id, request.tags)

        return {
            "status": "成功",
            "message": "标签添加成功",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "tags": [tag.tag_name for tag in user.tags]
            }
        }
    except ValidationError as e:
        # 处理请求体验证错误
        raise_http_exception(
            ErrorCodes.INVALID_REQUEST_FORMAT,
            "请求数据验证失败",
            {"errors": e.errors()}
        )
    except ValueError as e:
        # 处理业务逻辑错误
        raise_http_exception(ErrorCodes.USER_NOT_FOUND, str(e))
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 批量删除用户标签接口
@app.delete("/users/{user_id}/tags", response_model=schemas.ApiResponse)
async def remove_user_tags(
        user_id: int = Path(..., gt=0, description="用户ID"),
        request: schemas.TagDeleteRequest = Body(...),
        db_session: Session = Depends(get_db)
):
    """
    删除指定用户的特定标签
    """
    try:
        # 验证用户是否存在
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            raise_http_exception(ErrorCodes.USER_NOT_FOUND)

        # 从用户中删除标签
        success, removed_tags = TagRepository.remove_tags_from_user(db_session, user_id, request.tags)

        if not success:
            raise_http_exception(ErrorCodes.TAG_NOT_ASSOCIATED)

        return {
            "status": "成功",
            "message": "标签删除成功",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "removed_tags": list(removed_tags),
                "remaining_tags": [tag.tag_name for tag in user.tags]
            }
        }
    except ValidationError as e:
        # 处理请求体验证错误
        raise_http_exception(
            ErrorCodes.INVALID_REQUEST_FORMAT,
            "请求数据验证失败",
            {"errors": e.errors()}
        )
    except ValueError as e:
        # 处理业务逻辑错误
        raise_http_exception(ErrorCodes.USER_NOT_FOUND, str(e))
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 删除单个用户标签接口（向后兼容）
@app.delete("/users/{user_id}/tags/{tag_name}", response_model=schemas.ApiResponse)
async def remove_user_tag(
        user_id: int = Path(..., gt=0, description="用户ID"),
        tag_name: str = Path(..., description="要删除的标签名称"),
        db_session: Session = Depends(get_db)
):
    """
    删除指定用户的单个标签
    """
    try:
        # 验证标签名称
        if not tag_name or not tag_name.strip():
            raise_http_exception(ErrorCodes.INVALID_TAG_NAME)

        # 从用户中删除标签
        success = TagRepository.remove_tag_from_user(db_session, user_id, tag_name)

        if not success:
            raise_http_exception(
                ErrorCodes.TAG_NOT_ASSOCIATED,
                f"用户 '{user_id}' 没有标签 '{tag_name}'"
            )

        # 获取更新后的用户信息
        user = TagRepository.get_user_by_id(db_session, user_id)

        return {
            "status": "成功",
            "message": f"成功删除标签 '{tag_name}'",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "removed_tag": tag_name,
                "remaining_tags": [tag.tag_name for tag in user.tags]
            }
        }
    except ValidationError as e:
        # 处理路径参数验证错误
        raise_http_exception(
            ErrorCodes.INVALID_REQUEST_FORMAT,
            "请求数据验证失败",
            {"errors": e.errors()}
        )
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 清空用户所有标签接口
@app.delete("/users/{user_id}/all_tags", response_model=schemas.ApiResponse)
async def clear_user_tags(
        user_id: int = Path(..., gt=0, description="用户ID"),
        db_session: Session = Depends(get_db)
):
    """
    清空指定用户的所有标签
    """
    try:
        # 清空用户的所有标签
        success = TagRepository.clear_user_tags(db_session, user_id)

        if not success:
            raise_http_exception(ErrorCodes.USER_NOT_FOUND)

        # 获取更新后的用户信息
        user = TagRepository.get_user_by_id(db_session, user_id)

        return {
            "status": "成功",
            "message": "成功清空所有标签",
            "data": {
                "user_id": user.user_id,
                "username": user.username,
                "tags": []
            }
        }
    except ValidationError as e:
        # 处理路径参数验证错误
        raise_http_exception(
            ErrorCodes.INVALID_USER_ID,
            "无效的用户ID",
            {"errors": e.errors()}
        )
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 获取所有标签接口
@app.get("/tags", response_model=schemas.ApiResponse)
async def get_all_tags(
        db_session: Session = Depends(get_db)
):
    """
    获取系统中所有存在的标签
    """
    try:
        # 查询所有标签
        tags = TagRepository.get_all_tags(db_session)

        return {
            "status": "成功",
            "message": "成功获取所有标签",
            "data": {
                "tags": [tag.tag_name for tag in tags],
                "total": len(tags)
            }
        }
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 根据标签查找用户接口
@app.get("/tags/{tag_name}/users", response_model=schemas.ApiResponse)
async def get_users_with_tag(
        tag_name: str = Path(..., description="标签名称"),
        db_session: Session = Depends(get_db)
):
    """
    获取所有拥有某个标签的用户
    """
    try:
        # 验证标签名称
        if not tag_name or not tag_name.strip():
            raise_http_exception(ErrorCodes.INVALID_TAG_NAME)

        # 查询拥有该标签的用户
        tag, users = TagRepository.get_users_with_tag(db_session, tag_name)

        if not tag:
            raise_http_exception(ErrorCodes.TAG_NOT_FOUND)

        return {
            "status": "成功",
            "message": f"成功获取拥有标签 '{tag_name}' 的用户",
            "data": {
                "tag": tag.tag_name,
                "users": [
                    {
                        "user_id": user.user_id,
                        "username": user.username
                    }
                    for user in users
                ],
                "total": len(users)
            }
        }
    except ValidationError as e:
        # 处理路径参数验证错误
        raise_http_exception(
            ErrorCodes.INVALID_TAG_NAME,
            "无效的标签名称",
            {"errors": e.errors()}
        )
    except SQLAlchemyError as e:
        # 处理数据库错误
        errors.handle_database_error(e)
    except Exception as e:
        # 处理其他未预期错误
        raise_http_exception(ErrorCodes.INTERNAL_SERVER_ERROR, str(e))


# 应用程序入口点
if __name__ == "__main__":
    # 启动 uvicorn 服务器
    uvicorn.run(app, host="0.0.0.0", port=8000)