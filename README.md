# 安全生产视频生产平台

AI驱动的安全生产视频自动化生产平台。

## 功能

- **脚本生成** - 6大安全主题，3种时长
- **画面构想** - 写实/3D/动画3种风格
- **文案创作** - 6种类型，5大平台
- **视频二创** - YouTube/B站/抖音链接导入
- **视频生成** - 语音/画面/合成
- **分发文案** - 多平台一键生成

## 一键部署（3分钟上线）

### 方案A：Vercel部署（推荐，支持AI功能）

1. 访问 https://vercel.com/new
2. 导入 GitHub 仓库 `liufugui11/-1`
3. 在 Environment Variables 中添加：
   - `DASHSCOPE_API_KEY` = 你的阿里云API密钥
   - 或 `OPENAI_API_KEY` = 你的OpenAI密钥
4. 点击 Deploy

部署完成后获得公网地址，直接可用。

### 方案B：Netlify部署

1. 访问 https://app.netlify.com/start
2. 连接 GitHub 仓库 `liufugui11/-1`
3. 添加环境变量：`DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`
4. 部署

### 方案C：GitHub Pages（静态演示模式）

1. 访问 https://github.com/liufugui11/-1/settings/pages
2. Source 选择 "GitHub Actions"
3. 保存后自动部署到 https://liufugui11.github.io/-1/

注意：GitHub Pages 仅支持静态展示（使用模拟数据），AI功能需配置后端。

### 方案D：本地运行（完整功能）

```bash
cd safety-video-studio
source .venv/bin/activate
# 配置 .env 文件中的 API 密钥
uvicorn app:app --host 0.0.0.0 --port 7860
```

访问 http://localhost:7860

## 配置大模型API

### DashScope（阿里云，推荐）

1. 访问 https://dashscope.console.aliyun.com/
2. 获取 API-KEY
3. 设置环境变量：`DASHSCOPE_API_KEY`

### OpenAI

1. 访问 https://platform.openai.com/
2. 获取 API-KEY
3. 设置环境变量：`OPENAI_API_KEY`

## 技术栈

- 前端：HTML/CSS/JavaScript（单页应用）
- 后端：FastAPI / Vercel Python Functions / Netlify Python Functions
- AI：DashScope (qwen-turbo) / OpenAI (gpt-4o-mini)
- 部署：Vercel / Netlify / GitHub Pages / Docker
