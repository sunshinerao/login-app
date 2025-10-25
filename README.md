# Flask 用户注册登录系统

一个基于Flask的简单用户注册和登录系统，具有现代化的响应式Web界面。

## 功能特性

- 📝 **用户注册**: 具有密码强度验证的注册功能
- 🔐 **用户登录**: 安全的用户身份验证
- 🎨 **现代化UI**: 响应式设计，支持桌面和移动设备
- 🔒 **安全性**: 密码哈希存储，使用pbkdf2:sha256算法
- 📱 **用户体验**: 实时表单验证和友好的错误提示

## 技术栈

- **后端**: Flask + SQLAlchemy
- **数据库**: SQLite
- **前端**: HTML5 + CSS3 + JavaScript
- **安全**: Werkzeug 密码哈希

## 安装和运行

### 1. 克隆项目
```bash
git clone <repository-url>
cd login-app
```

### 2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install flask flask-sqlalchemy werkzeug
```

### 4. 运行应用
```bash
python app.py
```

### 5. 访问应用
打开浏览器访问: http://127.0.0.1:5000

## 项目结构

```
login-app/
├── app.py                 # Flask 主应用文件
├── templates/             # HTML 模板文件夹
│   ├── register.html      # 注册页面
│   └── login.html         # 登录页面
├── .gitignore            # Git 忽略文件
├── README.md             # 项目说明
└── requirements.txt      # 项目依赖
```

## API 端点

- `GET /` - 主页（重定向到注册页面）
- `GET /register` - 显示注册页面
- `POST /register` - 处理用户注册
- `GET /login` - 显示登录页面  
- `POST /login` - 处理用户登录

## 密码要求

注册时密码必须满足以下条件：
- 至少8个字符
- 包含大写字母
- 包含小写字母
- 包含数字

## 开发说明

- 数据库文件会自动创建在项目根目录
- 应用运行在调试模式，仅用于开发环境
- 生产环境请使用 WSGI 服务器（如 Gunicorn）

## 贡献

欢迎提交 Issues 和 Pull Requests！

## 许可证

MIT License