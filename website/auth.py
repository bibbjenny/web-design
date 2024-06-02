from flask import Blueprint, render_template, request, flash, redirect, url_for, session

import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash 
# hash = secures password, by changing and storing the password not in plain text but something else


auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # get user info(0 id, 1 email, 2 username, 3 password, 4 profile pic)
        db = sqlite3.connect('web.db')
        cursor = db.cursor()
        sql = f'''SELECT * FROM user;'''
        cursor.execute(sql)
        userdata = cursor.fetchall()
        db.close()
        session['userdata'] = userdata # store userdata
        
        for data in userdata:
            if username == data[2]: #check username
                if check_password_hash(data[3], password):#check password
                    flash('Logged in successfully', category='success')
                    return redirect(url_for('views.home'))
                else: # invalid login
                    flash('Invalid username and/or password', category='error')
            else: # invalid login
                flash('Invalid username and/or password', category='error')

    return render_template("login.html")

@auth.route('/logout')
def logout():
    return '<p>Logout</p>'

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
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
        result = cursor.fetchall()
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
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))
            
    return render_template("signup.html")
