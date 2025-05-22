# repository.py - 数据访问层，处理用户和标签相关的数据库操作
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from typing import List, Optional, Tuple, Set
import database as db
from database import User, Tag


class TagRepository:
    """
    标签仓库类，用于处理与用户和标签相关的数据库操作
    """

    @staticmethod
    def create_user(db_session: Session, username: str) -> User:
        """
        在数据库中创建新用户

        参数:
            db_session: 数据库会话
            username: 新用户的用户名

        返回:
            创建的用户对象

        异常:
            IntegrityError: 如果用户名已存在
        """
        # 创建用户对象
        user = User(username=username)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    @staticmethod
    def get_user_by_id(db_session: Session, user_id: int) -> Optional[User]:
        """
        根据用户ID获取用户

        参数:
            db_session: 数据库会话
            user_id: 要查询的用户ID

        返回:
            如果找到则返回用户对象，否则返回None
        """
        return db_session.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def get_user_by_username(db_session: Session, username: str) -> Optional[User]:
        """
        根据用户名获取用户

        参数:
            db_session: 数据库会话
            username: 要查询的用户名

        返回:
            如果找到则返回用户对象，否则返回None
        """
        return db_session.query(User).filter(User.username == username).first()

    @staticmethod
    def get_all_users(db_session: Session) -> List[User]:
        """
        获取所有用户

        参数:
            db_session: 数据库会话

        返回:
            所有用户的列表
        """
        return db_session.query(User).all()

    @staticmethod
    def create_tag(db_session: Session, tag_name: str) -> Tag:
        """
        创建新标签或获取已存在的标签

        参数:
            db_session: 数据库会话
            tag_name: 标签名称

        返回:
            标签对象
        """
        # 检查标签是否已存在
        tag = db_session.query(Tag).filter(Tag.tag_name == tag_name).first()
        if tag:
            return tag

        # 创建新标签
        tag = Tag(tag_name=tag_name)
        db_session.add(tag)
        db_session.commit()
        db_session.refresh(tag)
        return tag

    @staticmethod
    def get_tag_by_name(db_session: Session, tag_name: str) -> Optional[Tag]:
        """
        根据标签名称获取标签

        参数:
            db_session: 数据库会话
            tag_name: 要查询的标签名称

        返回:
            如果找到则返回标签对象，否则返回None
        """
        return db_session.query(Tag).filter(Tag.tag_name == tag_name).first()

    @staticmethod
    def get_all_tags(db_session: Session) -> List[Tag]:
        """
        获取所有标签

        参数:
            db_session: 数据库会话

        返回:
            所有标签的列表
        """
        return db_session.query(Tag).all()

    @staticmethod
    def add_tag_to_user(db_session: Session, user_id: int, tag_name: str) -> Tuple[User, Tag]:
        """
        为用户添加标签

        参数:
            db_session: 数据库会话
            user_id: 用户ID
            tag_name: 要添加的标签名称

        返回:
            用户对象和标签对象的元组

        异常:
            ValueError: 如果用户不存在
        """
        # 获取用户对象
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")

        # 获取或创建标签
        tag = TagRepository.create_tag(db_session, tag_name)

        # 如果用户还没有该标签，则添加
        if tag not in user.tags:
            user.tags.append(tag)
            db_session.commit()
            db_session.refresh(user)

        return user, tag

    @staticmethod
    def add_tags_to_user(db_session: Session, user_id: int, tag_names: List[str]) -> Tuple[User, List[Tag]]:
        """
        为用户添加多个标签

        参数:
            db_session: 数据库会话
            user_id: 用户ID
            tag_names: 要添加的标签名称列表

        返回:
            用户对象和标签对象列表的元组

        异常:
            ValueError: 如果用户不存在
        """
        # 获取用户对象
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            raise ValueError(f"用户ID {user_id} 不存在")

        # 遍历标签名称列表，为用户添加每个标签
        tags = []
        for tag_name in tag_names:
            tag = TagRepository.create_tag(db_session, tag_name)
            if tag not in user.tags:
                user.tags.append(tag)
            tags.append(tag)

        # 提交数据库更改
        db_session.commit()
        db_session.refresh(user)

        return user, tags

    @staticmethod
    def get_user_tags(db_session: Session, user_id: int) -> Tuple[Optional[User], List[Tag]]:
        """
        获取用户的所有标签

        参数:
            db_session: 数据库会话
            user_id: 用户ID

        返回:
            用户对象和标签列表的元组，如果用户不存在则返回(None, [])
        """
        # 获取用户对象
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            return None, []

        return user, user.tags

    @staticmethod
    def remove_tag_from_user(db_session: Session, user_id: int, tag_name: str) -> bool:
        """
        从用户中删除标签

        参数:
            db_session: 数据库会话
            user_id: 用户ID
            tag_name: 要删除的标签名称

        返回:
            如果成功删除返回True，如果用户或标签不存在返回False
        """
        # 获取用户对象
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            return False

        # 获取标签对象并检查用户是否拥有该标签
        tag = TagRepository.get_tag_by_name(db_session, tag_name)
        if not tag or tag not in user.tags:
            return False

        # 从用户的标签列表中删除该标签
        user.tags.remove(tag)
        db_session.commit()
        return True

    @staticmethod
    def remove_tags_from_user(db_session: Session, user_id: int, tag_names: List[str]) -> Tuple[bool, Set[str]]:
        """
        从用户中删除多个标签

        参数:
            db_session: 数据库会话
            user_id: 用户ID
            tag_names: 要删除的标签名称列表

        返回:
            成功状态和已删除标签名称集合的元组
        """
        # 获取用户对象
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            return False, set()

        # 遍历标签名称列表，删除用户拥有的标签
        removed_tags = set()
        for tag_name in tag_names:
            tag = TagRepository.get_tag_by_name(db_session, tag_name)
            if tag and tag in user.tags:
                user.tags.remove(tag)
                removed_tags.add(tag_name)

        # 提交数据库更改
        db_session.commit()
        return bool(removed_tags), removed_tags

    @staticmethod
    def clear_user_tags(db_session: Session, user_id: int) -> bool:
        """
        清空用户的所有标签

        参数:
            db_session: 数据库会话
            user_id: 用户ID

        返回:
            如果成功返回True，如果用户不存在返回False
        """
        # 获取用户对象
        user = TagRepository.get_user_by_id(db_session, user_id)
        if not user:
            return False

        # 清空用户的所有标签
        user.tags.clear()
        db_session.commit()
        return True

    @staticmethod
    def get_users_with_tag(db_session: Session, tag_name: str) -> Tuple[Optional[Tag], List[User]]:
        """
        获取拥有特定标签的所有用户

        参数:
            db_session: 数据库会话
            tag_name: 标签名称

        返回:
            标签对象和用户列表的元组，如果标签不存在则返回(None, [])
        """
        # 获取标签对象
        tag = TagRepository.get_tag_by_name(db_session, tag_name)
        if not tag:
            return None, []

        return tag, tag.users