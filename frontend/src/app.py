import os
import time
from datetime import timedelta, datetime

from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha512_crypt

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['JWT_ACCESS_COOKIE_NAME'] = 'access_token'
app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # For simplicity in this example, CSRF protection is disabled. Consider enabling it for production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://' + os.getenv("USERS_FILE", "/users.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
print("DB URI : " + app.config['SQLALCHEMY_DATABASE_URI'])
db = SQLAlchemy(app)

jwt = JWTManager(app)

class User(db.Model):
    """User model for the database
    """
    __tablename__ = 'users'
    id = db.Column('ID', db.Integer, primary_key=True)
    username = db.Column('username', db.String, unique=True, nullable=False)
    password = db.Column('password', db.String, nullable=False)
    last_failed_auth = db.Column('last_failed_auth', db.Integer)

    def __repr__(self):
        return '<User %r>' % self.username

shared_dir_path = os.getenv("SHARED_DIR_PATH", "/mnt/avm-shared")

def read_file(filename: str):
    """Generic function to read the content of a file in the shared directory

    Args:
        filename (str): Name of the file

    Returns:
        str: Content of the file
    """
    filename = f"{shared_dir_path}/{filename}"
    if os.path.exists(filename):
        with open(filename, 'r', encoding="UTF-8") as file:
            return file.read().strip()
    return None

def write_file(filename: str, content: str):
    """Generic function to write content to a file in the shared directory

    Args:
        filename (str): Name of the file
        content (str): Content to write to the file
    """
    filename = f"{shared_dir_path}/{filename}"
    with open(filename, 'w', encoding="UTF-8") as file:
        file.write(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page
    """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user:
            current_time = int(time.time())
            last_failed_auth = user.last_failed_auth or 0
            delay_since_last_fail = current_time - last_failed_auth

            if delay_since_last_fail < 60:
                return 'A failed attempt for this user appened less than a minute ago. Please try again in a few seconds.', 401
            else:
                if sha512_crypt.verify(password, user.password):
                    user.last_failed_auth = None  # reset the counter on successful login
                    db.session.commit()
                    access_token = create_access_token(identity=username, expires_delta=timedelta(hours=2))
                    resp = make_response(redirect(url_for('index')))
                    resp.set_cookie('access_token', access_token)
                    print("REDIRECTING")
                    return resp
                else:
                    user.last_failed_auth = current_time
                    db.session.commit()
                    return 'Invalid username or password', 401
    return render_template('login.html')

@app.route('/')
@jwt_required(optional=True)
def index():
    """Main page
    """
    current_user = get_jwt_identity()
    if current_user:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))

@app.route('/api/status')
@jwt_required()
def get_status():
    """Get status API endpoint
    """
    status = read_file('state')
    ip_address = read_file('ip_address') if status == 'running' else None
    remaining_time = None

    if status == 'running':
        shutdown_time = read_file('spindown_scheduled')
        if shutdown_time:
            remaining_time = datetime.strptime(shutdown_time, '%Y-%m-%d %H:%M:%S') - datetime.now()
            remaining_time = str(remaining_time).split('.')[0]  # Remove microseconds

    return jsonify(status=status, ip_address=ip_address, remaining_time=remaining_time)

@app.route('/api/start', methods=['POST'])
@jwt_required()
def start_server():
    """Start server request API endpoint
    """
    duration = request.form['duration']
    shutdown_time = datetime.now() + timedelta(hours=int(duration))

    write_file('spinup_requested', 'true')
    write_file('spindown_scheduled', shutdown_time.strftime('%Y-%m-%d %H:%M:%S'))


    return jsonify({'message': 'Server starting'})

@app.route('/api/extend', methods=['POST'])
@jwt_required()
def extend_time():
    """Extend sertver runtime API endpoint
    """
    duration = request.form['duration']
    current_shutdown = read_file('spindown_scheduled')
    if current_shutdown:
        new_shutdown = datetime.strptime(current_shutdown, '%Y-%m-%d %H:%M:%S') + timedelta(hours=int(duration))
        write_file('spindown_scheduled', new_shutdown.strftime('%Y-%m-%d %H:%M:%S'))

    return jsonify({'message': 'Time extended'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False)
