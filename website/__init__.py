from flask import Flask, render_template

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'apple pie'

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app
