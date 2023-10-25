import pytz
from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config


# app configuration
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'

mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    # set app cfg
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    @app.route('/set_timezone', methods=['POST'])
    def set_timezone():
        """Get timezone from the browser and store it in the session object."""
        timezone = request.data.decode('utf-8')
        session['timezone'] = timezone
        return ""

    @app.template_filter('localtime')
    def localtime_filter(value):
        """Use timezone from the session object, if available, to localize datetimes from UTC."""
        if 'timezone' not in session:
            return value

        format = '%d-%m-%Y %H:%M'
        # https://stackoverflow.com/a/34832184
        utc_dt = pytz.utc.localize(value)
        local_tz = pytz.timezone(session['timezone'])
        local_dt = utc_dt.astimezone(local_tz)
        return local_dt.strftime(format)

    # import routes
    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors

    # register blueprints
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app