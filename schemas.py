# schemas.py - Pydantic 数据模型定义文件，用于请求和响应的数据验证
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# 基础模型类，用于请求和响应
class TagBase(BaseModel):
    """标签基础模型"""
    tag_name: str

    @validator('tag_name')
    def tag_name_must_not_be_empty(cls, v):
        """验证标签名称不能为空且长度不超过50个字符"""
        if not v or not v.strip():
            raise ValueError('标签名称不能为空')
        if len(v) > 50:
            raise ValueError('标签名称不能超过50个字符')
        return v.strip()


class UserBase(BaseModel):
    """用户基础模型"""
    username: str

    @validator('username')
    def username_must_not_be_empty(cls, v):
        """验证用户名不能为空且长度不超过50个字符"""
        if not v or not v.strip():
            raise ValueError('用户名不能为空')
        if len(v) > 50:
            raise ValueError('用户名不能超过50个字符')
        return v.strip()


# 请求模型类
class UserCreate(UserBase):
    """创建用户请求模型"""
    pass


class TagCreate(TagBase):
    """创建标签请求模型"""
    pass


class TagAddRequest(BaseModel):
    """添加标签请求模型"""
    tags: List[str]

    @validator('tags')
    def tags_must_not_be_empty(cls, v):
        """验证标签列表不能为空，且每个标签都符合要求"""
        if not v:
            raise ValueError('至少需要提供一个标签')
        for tag in v:
            if not tag or not tag.strip():
                raise ValueError('标签名称不能为空')
            if len(tag) > 50:
                raise ValueError('标签名称不能超过50个字符')
        return [tag.strip() for tag in v]


class TagDeleteRequest(BaseModel):
    """删除标签请求模型"""
    tags: List[str]

    @validator('tags')
    def tags_must_not_be_empty(cls, v):
        """验证删除标签列表不能为空"""
        if not v:
            raise ValueError('至少需要提供一个要删除的标签')
        for tag in v:
            if not tag or not tag.strip():
                raise ValueError('标签名称不能为空')
        return [tag.strip() for tag in v]


# 响应模型类
class TagResponse(TagBase):
    """标签响应模型"""
    tag_id: int
    created_at: datetime

    class Config:
        orm_mode = True  # 启用 ORM 模式，支持从数据库对象创建


class UserResponse(UserBase):
    """用户响应模型"""
    user_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = []

    class Config:
        orm_mode = True  # 启用 ORM 模式，支持从数据库对象创建


class UserTagsResponse(BaseModel):
    """用户标签响应模型"""
    user_id: int
    username: str
    tags: List[str]


# 统一 API 响应模型
class ApiResponse(BaseModel):
    """统一的 API 响应格式模型"""
    status: str      # 响应状态：成功/错误
    message: str     # 响应消息描述
    data: Optional[Dict[str, Any]] = None  # 可选的响应数据


# 错误响应模型
class ErrorResponse(BaseModel):
    """错误响应模型"""
    status: str = "错误"    # 默认状态为错误
    code: str              # 错误码
    message: str           # 错误消息
    details: Optional[Dict[str, Any]] = None  # 可选的错误详情


# 路径参数模型类
class UserIdPath(BaseModel):
    """用户ID路径参数模型"""
    user_id: int

    @validator('user_id')
    def user_id_must_be_positive(cls, v):
        """验证用户ID必须是正整数"""
        if v <= 0:
            raise ValueError('用户ID必须是正整数')
        return v


class TagNamePath(BaseModel):
    """标签名称路径参数模型"""
    tag_name: str

    @validator('tag_name')
    def tag_name_must_not_be_empty(cls, v):
        """验证标签名称不能为空"""
        if not v or not v.strip():
            raise ValueError('标签名称不能为空')
        return v