# Business Insighter 部署到 Render 指南

## 项目概述
这是一个基于 FastAPI 的商业分析服务，提供市场分析和客户分析功能。

## 部署步骤

### 1. 准备 GitHub 仓库
确保您的代码已推送到 GitHub 仓库：`https://github.com/kuntu-tech/business_insighter.git`

### 2. 在 Render 上创建服务

1. 访问 [Render 官网](https://render.com/)
2. 使用 GitHub 账号登录
3. 点击 "New" -> "Web Service"
4. 连接您的 GitHub 仓库：`https://github.com/kuntu-tech/business_insighter.git`

### 3. 配置服务设置

**基本设置：**
- **Name**: `business-insighter`
- **Runtime**: `Python 3`
- **Branch**: `main`

**构建和启动命令：**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn demo4_service:app --host 0.0.0.0 --port $PORT`

### 4. 设置环境变量

在 Render 控制台的 "Environment" 部分添加以下环境变量：

| 变量名 | 描述 | 示例值 |
|--------|------|--------|
| `SUPABASE_PROJECT_ID` | Supabase 项目 ID | `your_project_id` |
| `SUPABASE_ACCESS_TOKEN` | Supabase 访问令牌 | `your_access_token` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | `sk-...` |
| `PORT` | 服务端口（Render 自动设置） | `8000` |

### 5. 部署

1. 确认所有设置无误
2. 点击 "Create Web Service"
3. Render 将自动构建和部署您的应用

### 6. 访问应用

部署完成后，您将获得一个类似 `https://business-insighter.onrender.com` 的 URL。

## API 端点

- **健康检查**: `GET /`
- **运行分析**: `POST /api/v1/run-analysis`

### 示例请求

```bash
curl -X POST "https://your-app.onrender.com/api/v1/run-analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "supabase_project_id": "your_project_id",
    "supabase_access_token": "your_access_token",
    "user_feedback": "分析短期度假租赁市场"
  }'
```

## 注意事项

1. **免费计划限制**: Render 免费计划有资源限制，应用可能会在无活动时休眠
2. **环境变量**: 确保所有必需的环境变量都已正确设置
3. **日志监控**: 在 Render 控制台查看部署日志以排查问题
4. **数据库**: 项目使用 Supabase 作为数据库，确保 Supabase 配置正确

## 故障排除

如果部署失败，请检查：
1. 环境变量是否正确设置
2. 构建日志中的错误信息
3. 确保所有依赖都在 `requirements.txt` 中
4. 检查 Python 版本兼容性
