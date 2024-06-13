from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import sqlite3

views = Blueprint('views', __name__)

def query_db(sql,args=(),one=False):
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

@views.route('/quiz/<id>/', methods=['GET', 'POST'])
def quiz(id):
    if id == 'home':
        return render_template('quizHome.html')
    if id == 'finish':
        # how to make user not able to access this page unless finished quiz?
        # get rid of this route and make it only accessable by return render_template?
        return render_template('quizFinish.html')
    else:   
        id = int(id)
        if request.method == "GET":
            # get quiz data, store in quiz_item
            sql = 'SELECT * FROM quiz WHERE quizID = ?;'
            quiz_item = query_db(sql, (id,), one = True)
        
            if not quiz_item:
                    flash('No more questions availaible', category='error')
                    return redirect(url_for('views.home'))
            
            # Render the template with the question
            return render_template('quiz.html', question=quiz_item[1], id=id)
            
        elif request.method == 'POST':
            # get quiz data, store in quiz_item
            sql = 'SELECT * FROM quiz WHERE quizID = ?;'
            quiz_item = query_db(sql, (id,), one = True)
            
            if not quiz_item:
                flash('No more questions availaible', category='error')
                return redirect(url_for('views.home'))
                
            user_answer = request.form.get('user_answer')
            answer = quiz_item[3]
            # Check if the user's answer matches the correct answer
            if user_answer.lower() == answer.lower():
                next_id = id + 1
                sql = 'SELECT * FROM quiz WHERE quizID = ?'
                next_quiz_item = query_db(sql, (next_id,))
                if next_quiz_item:
                    return redirect(url_for('views.quiz', id=next_id))
                else:
                    flash('Congratulations, you have completed the quiz!')
                    return redirect(url_for('views.quiz', id='finish'))
            else:
                flash('Incorrect answer. Please try again.', category='error')
                return render_template('quiz.html', question = quiz_item[1], id = id)

@views.route('/resources/')
def resources():
    return render_template('resources.html')

@views.route('/forum/<id>/', methods=['GET', 'POST']) # 1.
def forum(id):
    if id == 'home': # shows list of posts with their titles
       sql = 'SELECT * FROM forum_posts;'
       posts = query_db(sql)
       # 0=id, 1=userID, 2=title, 3=content, 4=date
       if posts: #check if any posts exsist
           return render_template('forumHome.html', posts=posts)
       else:
           return render_template('forumHome.html', posts='No posts are currently available')
    elif id == 'create':
        if request.method == 'GET':
            user = session.get('user')
            if user: # check if user is logged in
                return render_template('forumCreate.html')
            else:
                flash('Login is required', category='error')
                return redirect(url_for('auth.login'))
        elif request.method == 'POST':
            user = session.get('user')
            # 0 id, 1 email, 2 username, 3 password, 4 profile pic
            if user: # check if user is logged in
                userID = user[0]
                title = request.form.get('title')
                content = request.form.get('content')
                if not title: # needs title
                    flash('Title can\'t be empty', category='error')
                    return render_template('forumCreate.html', content=content)
                if not content: # needs content
                    flash('Content can\'t be empty', category='error')
                    return render_template('forumCreate.html', title=title)
                sql2 = 'SELECT postID FROM forum_posts ORDER BY postID DESC Limit 1;'
                id = query_db(sql2, (), one=True)
                if id: # id has to be the next number of the last post
                    new_id = 1+ int(id[0])
                else: # if no posts exist, id has to be 1
                    new_id = 1  
                sql = 'INSERT INTO forum_posts (postID, userID, title, content) VALUES (?, ?, ?, ?);'
                query_db(sql, (new_id, userID, title, content), one=True)
                flash('Post successfully created!', category="success")
                return redirect(url_for('views.forum', id = new_id ))
            else:
                flash('Login is required', category='error')
                return redirect(url_for('auth.login'))
    else:
        # id = forum_posts.postID
        id = int(id)
        sql = 'SELECT * FROM forum_posts WHERE postID = ?;'
        post_data = query_db(sql, (id,), one = True)
        # postID = 0, userID = 1, title = 2, content = 3, date = 4

        if not post_data: # post doesn't exist
            flash('Post not available.', category='error')
            return redirect(url_for('views.forum', id = 'home'))
        
        sql = '''
        SELECT user.username, user.profile_pic, forum_posts.userID
        FROM user
        LEFT JOIN forum_posts on user.userID = forum_posts.userID
        WHERE forum_posts.postID = ?;
        '''
        user = query_db(sql, (id,), one=True)
        # username = 0, profile pic = 1, userID = 2
        return render_template('forum.html', title = post_data[2], content = post_data[3], date = post_data[4], username = user[0], profile_pic = user[1])
    
# @views.route('/comments/<id>', methods=['GET', 'POST'])
# def comments(id):
