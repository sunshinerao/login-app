# Flask 应用：用户注册与登录
# 使用 SQLite 存储用户信息，密码加密
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)  # 用于会话管理
db = SQLAlchemy(app)

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
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    # 检查用户名是否已存在
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'message': '用户名已存在'}), 400

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
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '用户名和密码不能为空'}), 400

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        session['user_id'] = user.id
        session['username'] = user.username
        return jsonify({'message': '登录成功', 'redirect': '/dashboard'}), 200
    return jsonify({'message': '用户名或密码错误'}), 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
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
    app.run(debug=True)