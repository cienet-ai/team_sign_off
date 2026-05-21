# Team Sign-Off

审批签字系统（Team Sign-Off Approval System）。基于 FastAPI + Vue 3 的团队审批流程管理平台。

## 技术栈

| 层    | 技术                                                                 |
| ----- | -------------------------------------------------------------------- |
| 后端  | Python 3.12, FastAPI, SQLAlchemy (async), SQLite (aiosqlite), Alembic |
| 前端  | Vue 3, TypeScript, Pinia, Vue Router, Element Plus, Vite             |
| 认证  | Keycloak OIDC (RS256 JWT), oidc-client-ts (前端), jose (后端)         |
| 部署  | Docker Compose, uv (Python 包管理), Nginx (静态资源)                  |

## 快速开始

### 前置条件

- Python >= 3.12 + [uv](https://docs.astral.sh/uv/)
- Node.js >= 20 + npm
- Keycloak 实例（使用 `team-sign-off` realm）

### 后端

```bash
# 安装依赖
uv sync

# 启动开发服务器（热重载）
uv run uvicorn backend.app.main:app --reload
```

服务运行在 `http://localhost:8000`。

### 前端

```bash
cd frontend

# 安装依赖
npm ci

# 启动开发服务器
npm run dev
```

服务运行在 `http://localhost:5173`，自动代理 `/api` → `:8000`。

### 环境变量

后端使用 `.env`（`APP_` 前缀），前端使用 `frontend/.env`（`VITE_` 前缀）。参考 `.env.sample` 和 `frontend/.env.sample`。

```bash
cp .env.sample .env
cp frontend/.env.sample frontend/.env
```

| 变量                          | 说明                     | 默认值                                            |
| ----------------------------- | ------------------------ | ------------------------------------------------- |
| `APP_DATABASE_URL`            | 数据库连接串             | `sqlite+aiosqlite:///./data.db`                   |
| `APP_OIDC_ISSUER`             | Keycloak OIDC issuer     | `http://localhost:8080/realms/team-sign-off`       |
| `APP_OIDC_CLIENT_ID`          | OIDC 客户端 ID           | `team-sign-off-frontend`                           |
| `APP_OIDC_CLIENT_SECRET`      | OIDC 客户端密钥          |                                                   |
| `APP_CORS_ORIGINS`            | 前端 CORS 允许源         | `["http://localhost:5173"]`                       |
| `VITE_OIDC_AUTHORITY`         | 前端 OIDC authority      | `http://localhost:8080/realms/team-sign-off`       |
| `VITE_OIDC_CLIENT_ID`         | 前端 OIDC 客户端 ID      | `team-sign-off-frontend`                           |
| `VITE_OIDC_CLIENT_SECRET`     | 前端 OIDC 客户端密钥     |                                                   |

### 完整构建

```bash
cd frontend
npm run build   # vue-tsc -b && vite build
```

## Docker 部署

```bash
docker compose --env-file .env.docker up -d
```

- 后端：`localhost:8000`
- 前端：`localhost:80`

## 项目结构

```
.
├── backend/                   # Python 后端
│   ├── app/
│   │   ├── main.py            # FastAPI 应用入口
│   │   ├── config.py          # 配置（pydantic-settings）
│   │   ├── database.py        # 数据库引擎 & Session
│   │   ├── api/               # 路由（auth, applications, users, audit）
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── schemas/           # Pydantic 请求/响应
│   │   ├── services/          # 业务逻辑
│   │   └── middleware/        # JWT 认证 & 用户自动创建
│   ├── alembic/               # Alembic 迁移（未使用）
│   └── Dockerfile
├── frontend/                  # Vue 3 前端
│   ├── src/
│   │   ├── main.ts            # 应用入口
│   │   ├── App.vue
│   │   ├── router/            # 路由定义
│   │   ├── stores/            # Pinia 状态管理
│   │   ├── api/               # API 客户端 (axios)
│   │   ├── views/             # 页面组件
│   │   ├── types/             # TypeScript 类型定义
│   │   └── components/        # 通用组件
│   ├── Dockerfile
│   └── nginx.conf.template
├── .env.sample                # 后端环境变量模板
├── docker-compose.yml
├── pyproject.toml
└── uv.lock
```

## API

| 方法   | 路径                               | 说明               |
| ------ | ---------------------------------- | ------------------ |
| GET    | `/api/health`                      | 健康检查           |
| GET    | `/api/auth/me`                     | 当前用户信息       |
| GET    | `/api/users`                       | 用户列表           |
| POST   | `/api/applications`                | 创建申请           |
| GET    | `/api/applications`                | 我的申请列表       |
| GET    | `/api/applications/pending`        | 待审批列表         |
| GET    | `/api/applications/{id}`           | 申请详情           |
| PUT    | `/api/applications/{id}`           | 修改并重新提交     |
| POST   | `/api/applications/{id}/approve`   | 通过申请           |
| POST   | `/api/applications/{id}/reject`    | 驳回申请           |
| POST   | `/api/applications/{id}/void`      | 作废申请           |
| GET    | `/api/audit`                       | 审计日志（支持过滤）|

所有 API （除健康检查外）需要 Bearer Token 认证。
