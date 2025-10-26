# Flask 用户登录系统

一个基于Flask的现代化用户注册和登录系统，具有完整的用户管理、个人资料功能和全响应式设计。

## ✨ 功能特性

### � 用户认证系统
- **安全注册**: 邮箱/用户名注册，实时密码强度验证
- **智能登录**: 支持邮箱或用户名登录
- **密码安全**: pbkdf2:sha256加密存储
- **会话管理**: 安全的用户会话控制

### 👤 个人管理
- **个人资料**: 完整的用户信息编辑
- **活动管理**: 个人活动记录和管理
- **课程系统**: 课程注册和进度跟踪
- **数据统计**: 个人数据可视化展示

### 📱 响应式设计
- **多设备适配**: 完美支持桌面、平板、手机
- **现代UI**: Material Design风格界面
- **触摸优化**: 移动设备友好的交互体验
- **自适应布局**: 智能响应不同屏幕尺寸

### 🛡️ 安全验证
- **邮箱验证**: 实时邮箱格式校验
- **密码强度**: 动态密码强度指示器
- **输入验证**: 前后端双重数据验证
- **XSS防护**: 完整的安全输入处理

## 🔧 技术栈

- **后端框架**: Flask 3.0.0
- **数据库**: SQLite + SQLAlchemy 3.1.1 ORM
- **前端技术**: HTML5, CSS3, JavaScript (ES6+)
- **认证系统**: Flask Session + Werkzeug Security
- **UI设计**: 响应式CSS Grid + Flexbox布局

## 🚀 快速开始

### 📋 环境要求

- **Python**: 3.7+ (推荐3.11+)
- **pip**: Python包管理器
- **Git**: 版本控制工具

### ⚡ 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/sunshinerao/login-app.git
cd login-app
```

2. **创建虚拟环境** (推荐)
```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate
```

3. **安装依赖**
```bash
pip install -r requirements.txt
```

4. **运行应用**
```bash
python app.py
```

5. **访问应用**
- 浏览器访问: `http://127.0.0.1:5001`
- 注册新账户或使用测试账户登录

### 📱 响应式测试

- **桌面端**: 直接浏览器访问
- **移动端**: 手机浏览器访问 `http://你的IP:5001`
- **开发工具**: F12 → 设备模拟器测试不同屏幕尺寸

## 📁 项目结构

```
login-app/
├── 📄 app.py                 # Flask主应用 (路由+模型+验证)
├── 📄 requirements.txt       # Python依赖包列表
├── 📄 README.md             # 项目文档 (本文件)
├── 📄 .gitignore            # Git忽略配置
├── 📂 templates/            # Jinja2 HTML模板
│   ├── 🏠 login.html        # 登录页面 (响应式)
│   ├── ✍️ register.html      # 注册页面 (密码验证)
│   ├── 📊 dashboard.html     # 用户仪表板 (数据管理)
│   └── 👤 profile.html       # 个人资料 (信息编辑)
├── 📂 instance/             # SQLite数据库文件 (自动生成)
└── 📂 __pycache__/          # Python缓存 (自动生成)
```

## 🗃️ 数据库设计

### 核心模型关系
```
User (用户)
├── 1:N → Activity (活动记录)
├── N:N → Course (课程系统)
└── Session (会话管理)
```

### 详细字段说明

**User 用户表**
- `id`: 主键，自增ID
- `username`: 用户名 (唯一，非空)
- `email`: 邮箱地址 (唯一，非空)
- `password_hash`: 密码哈希值
- `full_name`: 真实姓名
- `created_at`: 注册时间

**Activity 活动表**
- `id`: 活动ID
- `user_id`: 用户外键
- `title`: 活动标题
- `description`: 活动描述
- `created_at`: 创建时间

**Course 课程表**
- `id`: 课程ID
- `title`: 课程名称
- `description`: 课程描述
- `instructor`: 讲师信息

## 🔗 API接口文档

### 认证相关
| 方法 | 路径 | 功能 | 参数 |
|------|------|------|------|
| `GET` | `/` | 首页重定向 | - |
| `GET` | `/login` | 登录页面 | - |
| `POST` | `/login` | 执行登录 | `username/email`, `password` |
| `GET` | `/register` | 注册页面 | - |
| `POST` | `/register` | 执行注册 | `username`, `email`, `password`, `full_name` |
| `GET` | `/logout` | 用户登出 | - |

### 用户管理
| 方法 | 路径 | 功能 | 权限 |
|------|------|------|------|
| `GET` | `/dashboard` | 用户仪表板 | 需登录 |
| `GET` | `/profile` | 个人资料页 | 需登录 |
| `POST` | `/profile` | 更新资料 | 需登录 |

### 响应格式
```json
{
  "success": true,
  "message": "操作成功",
  "data": { /* 响应数据 */ }
}
```

## 🛡️ 安全特性

- **密码加密**: pbkdf2:sha256 + 随机盐值
- **会话安全**: Flask-Session + 安全配置
- **输入验证**: 前后端双重验证
- **XSS防护**: Jinja2自动转义
- **CSRF保护**: Flask内置CSRF令牌
- **邮箱验证**: 正则表达式格式校验

## 🎨 UI/UX设计

### 响应式断点
- **大屏桌面**: ≥1200px (宽敞布局)
- **普通桌面**: 1024-1199px (标准布局)  
- **平板横屏**: 769-1023px (适中布局)
- **平板竖屏**: 481-768px (紧凑布局)
- **手机设备**: ≤480px (垂直布局)

### 设计系统
- **主色调**: #667eea (现代蓝紫)
- **辅助色**: #764ba2 (深紫渐变)
- **字体**: 系统字体栈 (最佳性能)
- **动效**: CSS3 transitions (流畅体验)

## 🔨 开发指南

### 本地开发
```bash
# 开发模式运行 (自动重载)
export FLASK_ENV=development
python app.py

# 数据库重置
rm -rf instance/
python app.py  # 自动创建新数据库
```

### 代码规范
- **Python**: PEP 8 代码规范
- **HTML**: 语义化标签使用
- **CSS**: BEM命名规范
- **Git**: 约定式提交信息

### 扩展建议
- 邮箱验证功能
- 密码重置机制
- 用户头像上传
- 管理员后台
- API接口扩展

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

**作者**: [sunshinerao](https://github.com/sunshinerao)  
**项目**: Flask现代化登录系统  
**版本**: 2.0.0 (响应式设计版本)

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