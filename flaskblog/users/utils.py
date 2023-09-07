import os
import secrets
from PIL import Image
from flask import url_for, current_app
from flask_mail import Message
from flaskblog import mail
from flask_login import current_user


def save_picture(form_picture):
    """ This function saving picture that user provide through UpdateAccountForm """

    # in this block of code we are creating full path to new picture
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)  # missing variable is file name
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/profile_pics', picture_fn)

    # resizing picture to 125x125 resolution and finally saving it
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn           # returns filename if someone would like to use it


def delete_picture():
    """ This function simply removing user's previous profile-picture """
    # handy way to get full path to user's profile picture
    old_user_picture_path = os.path.join(current_app.root_path, 'static/profile_pics', current_user.image_file)
    os.remove(old_user_picture_path)


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request', sender='flaskproj997@gmail.com', recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for("users.reset_password", token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made'''
    mail.send(msg)