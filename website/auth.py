from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash 
# hash = secures password, by changing and storing the password not in plain text but something else


auth = Blueprint('auth', __name__)

# def login_required(f):
#     @wraps(f)
#     def decorated_function(*args, **kwargs):
#         if 'user' not in session:
#             session['next_url'] = request.url
#             return redirect(url_for('auth.login'))
#         return f(*args, **kwargs)
#     return decorated_function

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        db = sqlite3.connect('web.db')
        cursor = db.cursor()
        sql = f'SELECT * FROM user where username = ?;'
        cursor.execute(sql, (username,))
        userdata = cursor.fetchall()
        db.close()
        
        # get user info(0 id, 1 email, 2 username, 3 password, 4 profile pic)
        user = userdata[0]
        if user: 
            # got a user
            # check password
            if check_password_hash(user[3], password):
                flash('Logged in successfully', category='success')
                # store userdata
                session['user'] = user
                return redirect(url_for('views.index'))
            else: 
                flash('Invalid username and/or password', category='error')
        else:
            flash('Invalid username and/or password', category='error')

    return render_template("login.html")

@auth.route('/logout')
def logout():
    if 'user' in session:
        session.pop('user', None)
        flash('Logged out successfully')
        return redirect(request.referrer or url_for('views.index'))
    else:
        flash('You are not logged in', category='error')
        return redirect(url_for('auth.login'))
        
@auth.route('/sign-up', methods=['GET', 'POST'])
def signup():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        email = str(request.form.get('email')) # near "@gmail": syntax error
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        db = sqlite3.connect('web.db')
        cursor = db.cursor()
        sql = f'''SELECT CASE WHEN EXISTS (SELECT username FROM user WHERE username = '{username}')
        THEN 'TRUE'
        ELSE 'FALSE'
        END'''
        cursor.execute(sql)
        results = cursor.fetchone()
        result = results[0]
        db.close()
        if result == 'TRUE':
            flash('Username already exist', category='error')
        elif len(username) < 2:
            flash('Username must be longer than 1 character', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters long', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match', category='error')
        else:
            # add user to the database
            password = generate_password_hash(password1, method='pbkdf2:sha256')
            db = sqlite3.connect('web.db')
            cursor = db.cursor()
            sql = f"INSERT INTO user (email, username, password) VALUES ('{email}', '{username}', '{password}');"
            cursor.execute(sql)
            db.commit()
            db.close()
            flash('Account created! Please login to continue', category='success')
            return redirect(url_for(request.referrer or 'auth.login'))
            
    return render_template("signup.html")
