# 网易云音乐用户标签服务(更新后的API接口文档)

## 项目简介

网易云音乐用户标签服务是一个基于 FastAPI 的 RESTful API，用于管理用户的兴趣标签。该服务支持用户创建、标签添加、查询和删除等功能，采用 SQLAlchemy ORM 进行数据持久化，为个性化推荐提供数据支持。

## 功能特点

- 用户管理：创建用户、获取用户信息
- 标签管理：为用户添加一个或多个标签、删除特定标签、清空所有标签
- 查询功能：获取用户的所有标签、查找拥有特定标签的所有用户
- 系统管理：获取所有用户列表、获取所有标签列表
- 数据验证：完整的请求参数校验和错误处理
- 数据持久化：基于 SQLite 数据库的可靠存储

## 技术栈

- **后端框架**: Python + FastAPI 
- **数据库**: SQLite + SQLAlchemy ORM
- **数据验证**: Pydantic
- **API文档**: OpenAPI (Swagger UI)
- **前端界面**: HTML + JavaScript

## 数据库设计

### 表结构

#### users 表
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| user_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 用户唯一ID |
| username | VARCHAR(50) | NOT NULL, UNIQUE | 用户名称 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

#### tags 表  
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| tag_id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 标签唯一ID |
| tag_name | VARCHAR(50) | NOT NULL, UNIQUE | 标签名称 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

#### user_tags 关联表
| 字段名 | 类型 | 约束 | 描述 |
|--------|------|------|------|
| user_id | INTEGER | PRIMARY KEY, FOREIGN KEY | 用户ID |
| tag_id | INTEGER | PRIMARY KEY, FOREIGN KEY | 标签ID |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 关联创建时间 |

## API文档

### 基础信息

- **基础URL**: `http://localhost:8000`
- **内容类型**: 所有请求和响应均使用JSON格式
- **字符编码**: UTF-8
- **API文档**: `http://localhost:8000/docs` (Swagger UI)

### 统一响应格式

所有API响应遵循以下统一格式：

```json
{
  "status": "成功|错误",
  "message": "描述信息",
  "data": { /* 响应数据对象，可选 */ }
}
```

### 参数校验规则

#### 用户名校验
- 不能为空或只包含空白字符
- 长度不能超过50个字符
- 会自动去除首尾空白字符

#### 标签名称校验
- 不能为空或只包含空白字符
- 长度不能超过50个字符
- 会自动去除首尾空白字符

#### 用户ID校验
- 必须是正整数（大于0）

### API端点

#### 1. 健康检查

**请求**
```
GET /ping
```

**响应**
```json
{
  "status": "成功",
  "message": "用户标签服务正在运行"
}
```

#### 2. 创建用户

**请求**
```
POST /users
```

**请求头**
```
Content-Type: application/json
```

**请求体**
```json
{
  "username": "user1"
}
```

**成功响应 (201 Created)**
```json
{
  "status": "成功",
  "message": "用户创建成功",
  "data": {
    "user_id": 1,
    "username": "user1"
  }
}
```

**错误响应 (409 Conflict)**
```json
{
  "status": "错误",
  "code": "1002",
  "message": "用户已存在"
}
```

#### 3. 获取用户信息

**请求**
```
GET /users/{user_id}
```

**路径参数**
| 参数 | 类型 | 必填 | 描述 | 校验规则 |
|------|------|------|------|----------|
| user_id | integer | 是 | 用户唯一ID | 必须是正整数(>0) |

**成功响应 (200 OK)**
```json
{
  "status": "成功",
  "message": "成功获取用户信息",
  "data": {
    "user_id": 1,
    "username": "user1",
    "tags": ["摇滚爱好者", "音乐发烧友"]
  }
}
```

#### 4. 获取所有用户

**请求**
```
GET /users
```

**成功响应 (200 OK)**
```json
{
  "status": "成功",
  "message": "成功获取所有用户",
  "data": {
    "users": [
      {
        "user_id": 1,
        "username": "user1",
        "tags_count": 2
      },
      {
        "user_id": 2,
        "username": "user2",
        "tags_count": 0
      }
    ],
    "total": 2
  }
}
```

#### 5. 获取用户标签

**请求**
```
GET /users/{user_id}/tags
```

**路径参数**
| 参数 | 类型 | 必填 | 描述 | 校验规则 |
|------|------|------|------|----------|
| user_id | integer | 是 | 用户唯一ID | 必须是正整数(>0) |

**成功响应 - 用户有标签 (200 OK)**
```json
{
  "status": "成功",
  "message": "成功获取标签",
  "data": {
    "user_id": 1,
    "username": "user1",
    "tags": ["摇滚爱好者", "音乐发烧友"]
  }
}
```

**成功响应 - 用户无标签 (200 OK)**
```json
{
  "status": "成功",
  "message": "用户没有标签",
  "data": {
    "user_id": 1,
    "username": "user1",
    "tags": []
  }
}
```

#### 6. 添加用户标签

**请求**
```
POST /users/{user_id}/tags
```

**路径参数**
| 参数 | 类型 | 必填 | 描述 | 校验规则 |
|------|------|------|------|----------|
| user_id | integer | 是 | 用户唯一ID | 必须是正整数(>0) |

**请求头**
```
Content-Type: application/json
```

**请求体**
```json
{
  "tags": ["摇滚乐迷", "交响乐爱好者", "ACG爱好者"]
}
```

**参数校验**
- `tags`: 数组类型，至少包含一个标签
- 每个标签名称不能为空，长度不超过50个字符

**成功响应 (201 Created)**
```json
{
  "status": "成功",
  "message": "标签添加成功",
  "data": {
    "user_id": 1,
    "username": "user1",
    "tags": ["摇滚乐迷", "交响乐爱好者", "ACG爱好者"]
  }
}
```

#### 7. 删除用户的多个标签

**请求**
```
DELETE /users/{user_id}/tags
```

**路径参数**
| 参数 | 类型 | 必填 | 描述 | 校验规则 |
|------|------|------|------|----------|
| user_id | integer | 是 | 用户唯一ID | 必须是正整数(>0) |

**请求头**
```
Content-Type: application/json
```

**请求体**
```json
{
  "tags": ["交响乐爱好者", "ACG爱好者"]
}
```

**成功响应 (200 OK)**
```json
{
  "status": "成功",
  "message": "标签删除成功",
  "data": {
    "user_id": 1,
    "username": "user1",
    "removed_tags": ["交响乐爱好者", "ACG爱好者"],
    "remaining_tags": ["摇滚乐迷"]
  }
}
```

#### 8. 删除用户的单个标签

**请求**
```
DELETE /users/{user_id}/tags/{tag_name}
```

**路径参数**
| 参数 | 类型 | 必填 | 描述 | 校验规则 |
|------|------|------|------|----------|
| user_id | integer | 是 | 用户唯一ID | 必须是正整数(>0) |
| tag_name | string | 是 | 要删除的标签名称 | URL编码，不能为空 |

**成功响应 (200 OK)**
```json
{
  "status": "成功",
  "message": "成功删除标签 '交响乐爱好者'",
  "data": {
    "user_id": 1,
    "username": "user1",
    "removed_tag": "交响乐爱好者",
    "remaining_tags": ["摇滚乐迷"]
  }
}
```

#### 9. 清空用户的所有标签

**请求**
```
DELETE /users/{user_id}/all_tags
```

**路径参数**
| 参数 | 类型 | 必填 | 描述 | 校验规则 |
|------|------|------|------|----------|
| user_id | integer | 是 | 用户唯一ID | 必须是正整数(>0) |

**成功响应 (200 OK)**
```json
{
  "status": "成功",
  "message": "成功清空所有标签",
  "data": {
    "user_id": 1,
    "username": "user1",
    "tags": []
  }
}
```

#### 10. 获取所有标签

**请求**
```
GET /tags
```

**成功响应 (200 OK)**
```json
{
  "status": "成功",
  "message": "成功获取所有标签",
  "data": {
    "tags": ["摇滚乐迷", "夜猫子", "ACG爱好者", "古典乐迷", "电子乐迷"],
    "total": 5
  }
}
```

#### 11. 查找拥有特定标签的用户

**请求**
```
GET /tags/{tag_name}/users
```

**路径参数**
| 参数 | 类型 | 必填 | 描述 | 校验规则 |
|------|------|------|------|----------|
| tag_name | string | 是 | 标签名称 | URL编码，不能为空 |

**成功响应 (200 OK)**
```json
{
  "status": "成功",
  "message": "成功获取拥有标签 '摇滚乐迷' 的用户",
  "data": {
    "tag": "摇滚乐迷",
    "users": [
      {
        "user_id": 1,
        "username": "user1"
      },
      {
        "user_id": 3,
        "username": "user2"
      }
    ],
    "total": 2
  }
}
```

### 错误码表

#### 用户相关错误 (1xxx)
| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|------------|----------|------|
| 1001 | 404 | 用户不存在 | 指定的用户ID不存在 |
| 1002 | 409 | 用户已存在 | 用户名已被使用 |
| 1003 | 400 | 无效的用户ID | 用户ID格式错误或为非正整数 |

#### 标签相关错误 (2xxx)
| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|------------|----------|------|
| 2001 | 404 | 标签不存在 | 指定的标签不存在 |
| 2002 | 409 | 标签已存在 | 标签名称已存在（系统级别） |
| 2003 | 400 | 无效的标签名称 | 标签名称为空或格式错误 |
| 2004 | 404 | 用户未关联该标签 | 用户没有该标签，无法删除 |

#### 验证错误 (3xxx)
| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|------------|----------|------|
| 3001 | 400 | 请求格式无效 | JSON格式错误或数据类型错误 |
| 3002 | 400 | 缺少必填字段 | 请求体中缺少必要的字段 |
| 3003 | 400 | 字段值无效 | 字段值不符合验证规则 |

#### 数据库错误 (4xxx)
| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|------------|----------|------|
| 4001 | 500 | 数据库操作错误 | 数据库连接或操作失败 |
| 4002 | 409 | 数据完整性错误 | 违反数据库约束 |

#### 通用错误 (5xxx)
| 错误码 | HTTP状态码 | 错误信息 | 说明 |
|--------|------------|----------|------|
| 5001 | 500 | 服务器内部错误 | 未预期的服务器错误 |

### 错误响应格式

```json
{
  "status": "错误",
  "code": "1001",
  "message": "用户不存在",
  "details": {
    "additional_info": "可选的详细错误信息"
  }
}
```

## 本地开发环境搭建

### 环境要求

- Python 3.7+
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd netease-user-tags-service
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **初始化数据库**

数据库会在首次运行时自动创建，位置：`./data/user_tags.db`

4. **启动服务**
```bash
python main.py
```

或使用 uvicorn：
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

5. **访问服务**
- API服务：http://localhost:8000
- API文档：http://localhost:8000/docs
- 管理界面：打开 `tag-manager.html`

## 使用示例

### curl 命令示例

```bash
# 健康检查
curl http://localhost:8000/ping

# 创建用户
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "user1"}'

# 添加用户标签
curl -X POST http://localhost:8000/users/1/tags \
  -H "Content-Type: application/json" \
  -d '{"tags": ["摇滚乐迷", "夜猫子"]}'

# 获取用户标签
curl http://localhost:8000/users/1/tags

# 获取用户信息
curl http://localhost:8000/users/1

# 删除单个标签
curl -X DELETE http://localhost:8000/users/1/tags/摇滚乐迷

# 删除多个标签
curl -X DELETE http://localhost:8000/users/1/tags \
  -H "Content-Type: application/json" \
  -d '{"tags": ["夜猫子", "古典乐迷"]}'

# 清空所有标签
curl -X DELETE http://localhost:8000/users/1/all_tags

# 查找拥有特定标签的用户
curl http://localhost:8000/tags/摇滚乐迷/users

# 获取所有标签
curl http://localhost:8000/tags

# 获取所有用户
curl http://localhost:8000/users
```

### Python SDK 示例

```python
import requests

API_BASE = "http://localhost:8000"

# 创建用户
response = requests.post(f"{API_BASE}/users", 
                        json={"username": "user1"})
user_data = response.json()
user_id = user_data["data"]["user_id"]

# 添加标签
requests.post(f"{API_BASE}/users/{user_id}/tags", 
              json={"tags": ["摇滚乐迷", "音乐发烧友"]})

# 获取用户标签
response = requests.get(f"{API_BASE}/users/{user_id}/tags")
user_tags = response.json()["data"]["tags"]

# 查找用户
response = requests.get(f"{API_BASE}/tags/摇滚乐迷/users")
users = response.json()["data"]["users"]
```

## 前端管理界面

项目包含一个完整的 HTML 管理界面 (`tag-manager.html`)，提供以下功能：

- **用户管理**：创建用户、查看用户列表
- **标签管理**：添加标签、删除标签、查看标签
- **查询功能**：按用户查询标签、按标签查询用户
- **系统信息**：查看所有用户和标签统计

### 使用方法

1. 在浏览器中打开 `tag-manager.html`
2. 确保 API 服务在 `http://localhost:8000` 运行
3. 使用界面进行各种管理操作

## 数据持久化

- **数据库文件**：`./data/user_tags.db` (SQLite)
- **自动创建**：首次运行时会自动创建数据库和表结构
- **数据迁移**：支持使用 Alembic 进行数据库版本管理

## 开发和扩展

### 项目结构

```
├── main.py              # FastAPI 应用主文件
├── database.py          # 数据库模型和配置
├── repository.py        # 数据访问层
├── schemas.py           # Pydantic 数据模型
├── errors.py            # 错误处理和错误码定义
├── requirements.txt     # 项目依赖
├── create-tables-sql.sql # 数据库建表脚本
├── tag-manager.html     # 前端管理界面
├── data/                # 数据库文件目录
└── README.md           # 项目文档
```

### 扩展功能建议

1. **用户认证**：添加 JWT 认证机制
2. **权限管理**：实现用户角色和权限控制
3. **标签分类**：支持标签分类和层级结构
4. **批量操作**：支持批量用户和标签操作
5. **数据分析**：添加标签使用统计和分析功能
6. **缓存优化**：使用 Redis 缓存提升查询性能

## 许可证

本项目仅用于学习和研究目的。

---

**网易云音乐用户标签服务** &copy; 2025