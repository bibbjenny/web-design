from flask import Blueprint, render_template, request, flash, redirect, url_for, session
import sqlite3

views = Blueprint('views', __name__)


def query_db(sql, args=(), one=False):
    '''connect and query- will retun one item if one=true and can accept arguments as tuple'''
    db = sqlite3.connect('web.db')
    cursor = db.cursor()
    cursor.execute(sql, args)
    results = cursor.fetchall()
    db.commit()
    db.close()
    return (results[0] if results else None) if one else results


@views.route('/')
def index():
    return render_template("index.html")


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
            quiz_item = query_db(sql, (id,), one=True)
        
            if not quiz_item:
                flash('No more questions availaible', category='error')
                return redirect(url_for('views.index'))
            
            # Render the template with the question
            return render_template('quiz.html', question=quiz_item[1], id=id)
            
        elif request.method == 'POST':
            # get quiz data, store in quiz_item
            sql = 'SELECT * FROM quiz WHERE quizID = ?;'
            quiz_item = query_db(sql, (id,), one=True)
            
            if not quiz_item:
                flash('No more questions availaible', category='error')
                return redirect(url_for('views.index'))
                
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
                return render_template('quiz.html', question=quiz_item[1], id=id)


@views.route('/resources/')
def resources():
    return render_template('resources.html')


@views.route('/forum/<id>/', methods=['GET', 'POST'])
def forum(id):
    # if action_comment and commentID is None: #not adjusting comments
    if id == 'home':
        # shows list of posts with their titles
        sql = 'SELECT * FROM forum_posts;'
        posts = query_db(sql)
        # 0=id, 1=userID, 2=title, 3=content, 4=date
        if posts:
            # check if any posts exsist
            return render_template('forumHome.html', posts=posts)
        else:
            return render_template('forumHome.html', posts='No posts are currently available')

    else:
        # id = forum_posts.postID
        id = int(id)

        # GRAB POST
        sql_post = '''SELECT f.title, f.content, f.post_date, u.username, u.userID, u.profile_pic
        FROM user u
        LEFT JOIN forum_posts f on u.userID = f.userID
        WHERE f.postID = ?;'''
        post_data = query_db(sql_post, (id,), one=True)
        # title 0, content 1, date 2, username 3, userID 4, profile_pic 5
        if not post_data: # post doesn't exist
            flash('Post not available.', category='error')
            return redirect(url_for('views.forum', id = 'home'))

        # GRAB COMMENTS
        sql_comment = '''SELECT c.*, u.username
        FROM comments c
        LEFT JOIN user u ON c.userID = u.userID
        WHERE c.postID = ?;'''
        comment_data = query_db(sql_comment, (id,))
        # comID 0, userID 1, postID 2, content 3, date 4, username 5
        return render_template('forum.html', postID = id,
        title = post_data[0],
        content = post_data[1],
        date = post_data[2],
        username = post_data[3],
        userID = post_data[4],
        profile_pic = post_data[5], comments = comment_data)

@views.route('/<action>/<subject>', methods=['GET', 'POST'])
def createANDedit(action, subject):
    if action == 'create':
        # 1. create post/comment
        # CREATE POST
        if subject == 'post':
            if request.method == 'GET':
                user = session.get('user')
                if user:
                    # check if user is logged in
                    return render_template('forumCreate.html')
                else:
                    flash('Login is required', category='error')
                    return redirect(url_for('auth.login'))
            elif request.method == 'POST':
                user = session.get('user')
                # 0 id, 1 email, 2 username, 3 password, 4 profile pic
                if user:
                    # check if user is logged in
                    userID = user[0]
                    title = request.form.get('title')
                    content = request.form.get('content')
                    if not title: # needs title
                        flash('Title can\'t be empty', category='error')
                        return render_template('forumCreate.html', content=content)
                    if not content: # needs content
                        flash('Content can\'t be empty', category='error')
                        return render_template('forumCreate.html', title=title)
                    
                    sql= 'INSERT INTO forum_posts (userID, title, content) VALUES (?, ?, ?);'
                    query_db(sql, (userID, title, content), one=True)
                    flash('Post successfully created!', category="success")
                    # sql = 'SELECT postID'
                    # How to view the written post right after without specifying the ID when creating post?
                    return redirect(url_for('views.forum', id='home' )) 
            
                else:
                    flash('Login is required', category='error')
                    return redirect(url_for('auth.login'))
            
        # CREATE COMMENT
        elif subject == 'comment':
            if request.method == 'POST':
                if 'user' in session: 
                        # double check if user is logged in
                        user = session.get('user')
                        # 0 id, 1 email, 2 username, 3 password, 4 profile pic
                        comment = request.form.get('comment')
                        postID = request.form.get('postID')
                        sql = 'INSERT INTO comments (userID, postID, content) VALUES (?, ?, ?);'
                        query_db(sql, (user[0], postID, comment))
                        return redirect(url_for('views.forum', id=postID))
                else:
                    flash('Login is required', category='error')
                    return redirect(url_for('auth.login'))

    elif action == 'edit':
        # 2. edit post/comment
        # EDIT POST
        if subject == 'post':
            if request.method == 'GET':
                if 'user' in session:
                    # double check if user is logged in
                    postID = request.args.get('postID', type=int)
                    # fetch query parameter
                    userID = session['user'][0]
                    # 0 id, 1 email, 2 username, 3 password, 4 profile pic
                    sql = 'SELECT * FROM forum_posts WHERE postID = ?;'
                    post_data = query_db(sql, (postID,), one=True)
                    # 0 postID, 1 userID, 2 title, 3 content, 4 date  
                    if post_data != None: 
                        # check if post exsits
                        if post_data[1] == userID:
                            # check if user wrote this post
                            return render_template('forumCreate.html', postID=postID, title=post_data[2], content=post_data[3])
                        else:
                            flash("Access denied", category='error')
                            return redirect(url_for('views.forum', id=postID))
                    else:
                        flash("Post not available", category='error')
                        return redirect(url_for('views.forum', id='home'))   
                else:
                    flash('Login requered', category='error')
                    return redirect(url_for('auth.login'))          
            elif request.method == "POST":
                postID = request.form.get('postID', type=int)
                sql = 'SELECT * FROM forum_posts WHERE postID = ?;'
                post_data = query_db(sql, (postID,), one=True)
                # 0 postID, 1 userID, 2 title, 3 content, 4 date 
                if post_data != None:
                    if 'user' in session: # double check if user is logged in
                        userID = session['user'][0]
                        # 0 id, 1 email, 2 username, 3 password, 4 profile pic
                        if userID == post_data[1]: # check if the user wrote this post
                            title = request.form.get('title')
                            content = request.form.get('content')
                            if not title: # needs title
                                flash('Title can\'t be empty', category='error')
                                return render_template('forumCreate.html', content=content)
                            if not content: # needs content
                                flash('Content can\'t be empty', category='error')
                                return render_template('forumCreate.html', title=title)
                            sql = 'UPDATE forum_posts SET title = ?, content = ? WHERE postID = ?;'
                            query_db(sql, (title, content, postID,))
                            flash('Post updated', category='success')
                            return redirect(url_for('views.forum', id=postID))
                        else:
                            flash('Access denied', category='error')
                            return redirect(url_for('views.forum', id=postID))
                    else:
                        flash('Login required', category='error')
                        return redirect(url_for('auth.login'))
                else:
                    flash("Post not available", category='error')
                    return redirect(url_for('views.forum', id='home'))
        
        # EDIT COMMENT
        elif subject == 'comment':
            if request.method == 'GET':
                if 'user' in session: 
                    # double check if user is logged in
                    userID = session['user'][0]
                    postID = request.args.get('postID', type=int)
                    sql1 = 'SELECT * FROM forum_posts where postID = ?;'
                    post_exist = query_db(sql1, (postID,))
                    if post_exist:
                        commentID = request.args.get('commentID', type=int)
                        sql2 = 'SELECT * FROM comments where comID = ?;'
                        comment_data = query_db(sql2, (commentID,), one=True)
                        com_userID = comment_data[1]
                        if userID == com_userID:
                            content = comment_data[3]
                            return render_template('forumCreate.html', postID = postID, commentID=commentID, edit_comment=True, content=content)
                        else:
                            flash('Access denied', category='error')
                            return redirect(url_for('views.forum', id=postID))
                    else:
                        flash("Post not available", category='error')
                        return redirect(url_for('views.forum', id='home'))
                else:
                    flash('Login required', category='error')
                    return redirect(url_for('auth.login'))
            if request.method == 'POST':
                if 'user' in session: 
                    # double check if user is logged in
                    userID = session['user'][0]
                    # 0 id, 1 email, 2 username, 3 password, 4 profile pic
                    postID = request.form.get('postID')
                    sql1 = 'SELECT * FROM forum_posts where postID = ?;'
                    post_exist = query_db(sql1, (postID,))
                    if post_exist:
                        commentID = request.form.get('commentID')
                        sql = 'SELECT * FROM COMMENTS WHERE comID = ?;'
                        comment_data = query_db(sql, (commentID,), one=True)
                        # 0 ID, 1 userID, 2 postID, 3 content, 4 com_date
                        comment_userID = comment_data[1]
                        if userID == comment_userID:
                            # check if current user wrote this comment
                            new_content = request.form.get('content')
                            sql2 = 'UPDATE comments SET content = ? WHERE comID = ?;'
                            query_db(sql2, (new_content, commentID,))
                            flash('Comment saved!', category='success')
                            return redirect(url_for('views.forum', id=postID))
                        else:
                            flash('Access denied', category='error')
                            return redirect(url_for('views.forum', id=postID))
                    else:
                        flash("Post not available", category='error')
                        return redirect(url_for('views.forum', id='home'))
                else:
                    flash('Login required', category='error')
                    return redirect(url_for('auth.login'))

@views.route('/delete/<subject>/<id>', methods = ['POST'])
def delete(subject, id):
    if subject == 'post':
        # deleting post
        postID = int(id)
        # fetch query parameter
        sql = 'SELECT * FROM forum_posts WHERE postID = ?;'
        post_data = query_db(sql, (postID,), one=True)
        # 0 postID, 1 userID, 2 title, 3 content, 4 date
        if post_data: 
            # check if post exists
            if 'user' in session: 
                # check if user is logged in
                userID = session['user'][0]
                # 0 id, 1 email, 2 username, 3 password, 4 profile pic
                if userID == post_data[1]:
                    # check if user wrote this post
                    sql = 'DELETE FROM forum_posts WHERE postID = ?;'
                    query_db(sql, (postID,))
                    flash('Post deleted', category='success')
                    return redirect(url_for('views.forum', id='home'))
                else:
                    flash('Access denied', category='error')
                    return redirect(url_for('views.forum', id=postID))
            else:
                flash('Login required', category='error')
                return redirect(url_for('auth.login'))
        else:
            flash("Post not available", category='error')
            return redirect(url_for('views.forum', id='home'))
        
    elif subject == 'comment':
        # deleting comment
        if 'user' in session: # double check if user is logged in
            userID = session['user'][0]
            # 0 id, 1 email, 2 username, 3 password, 4 profile pic
            commentID = int(id)
            sql = 'SELECT * FROM COMMENTS WHERE comID = ?;'
            comment_data = query_db(sql, (commentID,), one=True)
            # 0=comID, 1=userID, 2=postID, 3=content ,4=date
            com_userID = comment_data[1]
            postID = comment_data[2]
            if userID == com_userID: # check if the user wrote the comment
                sql = 'DELETE FROM comments WHERE comID = ?;'
                query_db(sql, (commentID,))
                flash('Comment deleted', category='success')
                return redirect(url_for('views.forum', id=postID))
            else:
                flash('Access denied', category='error')
                return redirect(url_for('views.forum', id=postID))