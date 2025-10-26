# Flask 应用：用户注册与登录
# 使用 SQLite 存储用户信息，密码加密
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# 使用固定的SECRET_KEY以保持会话持续性
app.config['SECRET_KEY'] = 'your-secret-key-for-session-management-change-in-production'
# 改进会话配置
app.config['SESSION_COOKIE_SECURE'] = False  # 开发环境允许HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止XSS攻击
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 允许同站点请求
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 会话1小时过期
db = SQLAlchemy(app)

# 验证函数
def validate_email(email):
    """验证邮箱格式"""
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def validate_username(username):
    """验证用户名格式：只允许字母、数字、下划线和点号，3-20位"""
    username_regex = r'^[a-zA-Z0-9._]{3,20}$'
    return re.match(username_regex, username) is not None

def validate_password(password):
    """验证密码强度：至少8位，包含大小写字母和数字"""
    if len(password) < 8:
        return False, "密码长度至少需要8位"
    if not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母"
    if not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母"
    if not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    return True, "密码格式正确"

def is_email_format(input_str):
    """判断输入是否为邮箱格式"""
    return '@' in input_str

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    full_name = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关联关系
    activities = db.relationship('UserActivity', backref='user', lazy=True)
    courses = db.relationship('UserCourse', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    max_participants = db.Column(db.Integer, default=50)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    activity_id = db.Column(db.Integer, db.ForeignKey('activity.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='registered')  # registered, attended, cancelled
    
    activity = db.relationship('Activity', backref='participants')

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    instructor = db.Column(db.String(100), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.Column(db.Integer, default=0)  # 进度百分比
    status = db.Column(db.String(20), default='enrolled')  # enrolled, completed, dropped
    
    course = db.relationship('Course', backref='students')

@app.route('/')
def index():
    return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    # POST 请求处理注册逻辑
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'message': '用户名/邮箱和密码不能为空'}), 400

    # 验证用户名/邮箱格式
    if is_email_format(username):
        if not validate_email(username):
            return jsonify({'message': '请输入有效的邮箱地址'}), 400
    else:
        if not validate_username(username):
            return jsonify({'message': '用户名只能包含字母、数字、下划线和点号，长度3-20位'}), 400

    # 验证密码强度
    is_valid_password, password_message = validate_password(password)
    if not is_valid_password:
        return jsonify({'message': password_message}), 400

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': '用户名/邮箱已存在'}), 400

    # 使用pbkdf2:sha256方法来避免scrypt兼容性问题
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(username=username, password=hashed_password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': '注册失败，请重试'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    # POST 请求处理登录逻辑
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'message': '用户名/邮箱和密码不能为空'}), 400

    # 验证输入格式
    if is_email_format(username):
        if not validate_email(username):
            return jsonify({'message': '请输入有效的邮箱地址'}), 400
    else:
        if not validate_username(username):
            return jsonify({'message': '用户名格式不正确'}), 400

    if len(password) < 6:
        return jsonify({'message': '密码长度不能少于6位'}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session.permanent = True  # 使会话持久化
        session['user_id'] = user.id
        session['username'] = user.username
        print(f"用户 {username} 登录成功，用户ID: {user.id}, 会话ID: {session.get('user_id')}")
        return jsonify({'message': '登录成功', 'redirect': '/dashboard'}), 200
    return jsonify({'message': '用户名或密码错误'}), 401

@app.route('/dashboard')
def dashboard():
    from flask import request
    print(f"Dashboard访问 - 会话内容: {dict(session)}")
    print(f"Dashboard访问 - Cookie: {request.cookies}")
    print(f"Dashboard访问 - User-Agent: {request.headers.get('User-Agent')}")
    if 'user_id' not in session:
        print("未找到user_id，重定向到登录页面")
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        print(f"未找到用户ID: {session['user_id']}")
        session.clear()
        return redirect(url_for('login'))
    
    print(f"Dashboard - 用户: {user.username}")    
    
    # 获取用户的活动和课程
    user_activities = UserActivity.query.filter_by(user_id=user.id).all()
    user_courses = UserCourse.query.filter_by(user_id=user.id).all()
    
    return render_template('dashboard.html', 
                         user=user, 
                         activities=user_activities,
                         courses=user_courses)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return jsonify({'message': '未登录'}), 401
    
    data = request.get_json()
    user = User.query.get(session['user_id'])
    
    if user:
        user.full_name = data.get('full_name', user.full_name)
        user.email = data.get('email', user.email)
        user.phone = data.get('phone', user.phone)
        
        try:
            db.session.commit()
            return jsonify({'message': '个人信息更新成功'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'message': '更新失败，请重试'}), 500
    
    return jsonify({'message': '用户不存在'}), 404

# 初始化一些示例数据
def init_sample_data():
    # 检查是否已有数据
    if Activity.query.first() is None:
        # 添加示例活动
        activities = [
            Activity(title='技术分享会', description='分享最新的技术趋势和开发经验', 
                    date=datetime(2024, 11, 15, 14, 0), location='会议室A', max_participants=30),
            Activity(title='团建活动', description='户外拓展训练，增强团队协作能力', 
                    date=datetime(2024, 11, 20, 9, 0), location='郊外基地', max_participants=50),
            Activity(title='产品发布会', description='新产品功能介绍和演示', 
                    date=datetime(2024, 12, 1, 10, 0), location='大会议厅', max_participants=100)
        ]
        
        # 添加示例课程
        courses = [
            Course(title='Python编程基础', description='从零开始学习Python编程', 
                  instructor='张老师', duration='8周', price=299.0,
                  start_date=datetime(2024, 11, 1), end_date=datetime(2024, 12, 26)),
            Course(title='Web前端开发', description='HTML、CSS、JavaScript全栈开发', 
                  instructor='李老师', duration='12周', price=499.0,
                  start_date=datetime(2024, 11, 15), end_date=datetime(2025, 2, 7)),
            Course(title='数据分析入门', description='使用Python进行数据分析和可视化', 
                  instructor='王老师', duration='6周', price=399.0,
                  start_date=datetime(2024, 12, 1), end_date=datetime(2025, 1, 12))
        ]
        
        for activity in activities:
            db.session.add(activity)
        
        for course in courses:
            db.session.add(course)
        
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_sample_data()
    app.run(debug=True, port=5001)