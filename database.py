# database.py
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, DateTime, Index, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

# 如果不存在则创建数据库目录
os.makedirs('data', exist_ok=True)

# 定义 SQLite 数据库的 URL
DATABASE_URL = "sqlite:///./data/user_tags.db"

# 创建 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 创建 sessionmaker 用于生成会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建用于声明模型的 Base 类
Base = declarative_base()

# 定义多对多关系的关联表
user_tags = Table(
    "user_tags",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.user_id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True),
    Column("created_at", DateTime, default=datetime.utcnow)
)


# 定义用户模型
class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 通过关联表建立与标签的关系
    tags = relationship("Tag", secondary=user_tags, back_populates="users")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, username={self.username})>"


# 定义标签模型
class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, autoincrement=True)
    tag_name = Column(String(50), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # 通过关联表建立与用户的关系
    users = relationship("User", secondary=user_tags, back_populates="tags")

    def __repr__(self):
        return f"<Tag(tag_id={self.tag_id}, tag_name={self.tag_name})>"


# 创建数据库表
def init_db():
    Base.metadata.create_all(bind=engine)


# 获取数据库会话的辅助函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
