from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import sqlite3

views = Blueprint('views', __name__)

def query_db(sql,args=(),one=False): # one=False exact meaning
    '''connect and query- will retun one item if one=true and can accept arguments as tuple'''
    db = sqlite3.connect('web.db')
    cursor = db.cursor()
    cursor.execute(sql, args)
    results = cursor.fetchall()
    db.commit()
    db.close()
    return (results[0] if results else None) if one else results

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/quiz/<int:id>/', methods=['GET', 'POST'])
def quiz(id):
    if id == '0':
        return render_template('quizHome.html')
    else:
        sql = 'SELECT quizID FROM quiz;'
        ids = query_db(sql=sql, args=(), one=True)
        for id in ids:
            sql = 'SELECT * FROM quiz where quizID = ?;'
            userdata = query_db(sql=sql, args=(id,), one=True)
            if request.method == 'POST':
                user_answer = request.form.get('user_answer')
                if user_answer == userdata[3]:
                    flash('Correct!', category='success')
                    # how to return to the next quiz with new values?
                else:
                    flash('Incorrect answer. Please try again.', category='error')
                    # how to return here?
                return render_template('quiz.html')
            else:
                return render_template('quiz.html', id = id, question=userdata[1], image=userdata[2], hint=userdata[4])

        # sql = 'SELECT * FROM quiz WHERE quizID = ?;'
        # data = query_db(sql=sql, args=(id,), one=True) # can I just write sql?
        # # from data, id = 0, question = 1, image = 2, answer = 3, hint = 4
        # if request.method == 'POST':
        #     user_answer = request.form.get('user_answer')
        #     if user_answer == data[3]:
        #         flash('Correct!', category='success')
        #         id = int(id) + 1
        #         data = query_db(sql=sql, args=(id,), one=True)
        #         # how to return to the next quiz with new values?
        #         return render_template('quiz.html', id = id, question=data[1], image=data[2], hint=data[4])
        #     else:
        #         flash('Incorrect answer. Please try again.', category='error')
        #         # how to return here?
        # else:
        #     return render_template('quiz.html', id = id, question=data[1], image=data[2], hint=data[4])

@views.route('/resources/')
def resources():
    return render_template('resources.html')