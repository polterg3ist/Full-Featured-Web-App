from flaskblog.users.utils import save_picture, delete_picture, send_reset_email
from flaskblog.users.forms import (
    RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm)
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


users = Blueprint('users', __name__)


@users.route("/users")
def user_list():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template('user_list.html', users=users)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():   # if we got POST request and form is valid
        # hashing password to secure user's password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)

        # add user to database and commit changes
        with current_app.app_context():
            db.session.add(user)
            db.session.commit()

        # flash message on top of the site
        flash('Your account has been created! You are now able to log in.', 'success')

        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).where(User.email == form.email.data)).scalar()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            # next_page is page that user was trying to open while he wasn't logged in
            next_page = request.args.get('next')
            if next_page:
                # redirect() function accept routes only without slash
                next_page = next_page.replace('/', '')
                # if there is a next page we would like to open that page instead of just redirect on home route
                return redirect(url_for(next_page))
            return redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if form.validate_on_submit():
        if form.picture.data:
            delete_picture()    # delete user's previous profile picture
            picture_file = save_picture(form.picture.data)  # save new profile picture in storage
            current_user.image_file = picture_file          # save new profile picture in database

        # there we save new values from form in the database
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()     # commit changes

        flash('Your account has been updated!', 'success')

        return redirect(url_for('users.account'))

    elif request.method == 'GET':
        # substitute values into form if we received a GET request
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)  # relative path to user's PP
    return render_template('account.html', title='Account', user=current_user, image_file=image_file, form=form)


@users.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = db.first_or_404(db.select(User).filter_by(username=username))
    user_posts = db.select(Post).filter_by(author=user).order_by(Post.date_posted.desc())
    user_posts_paginated = db.paginate(select=user_posts, page=page, per_page=5)
    return render_template('user_posts.html', posts=user_posts_paginated, user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = db.session.execute(db.select(User).filter_by(email=form.email.data)).scalar_one()
        print(user.username)
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.(Please check spam section!)', 'info')
        return redirect(url_for('users.login'))

    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)

    if not user:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():   # if we got POST request and form is valid
        # hashing password to secure user's password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        with current_app.app_context():
            user.password = hashed_password
            db.session.commit()

        # flash message on top of the site
        flash('Your password has been updated! You are now able to log in.', 'success')

        return redirect(url_for('users.login'))
    return render_template('reset_password.html', title='Reset Password', form=form)