import os


class Config:
    SECRET_KEY = '209a95d89e17faeb245479499776f6d6'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    #SECRET_KEY = os.environ.get('SECRET_KEY')
    #SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    #MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    #MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_USERNAME = 'flaskproj997@gmail.com'
    MAIL_PASSWORD = 'aiguozgldoeeyccd'

    