from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, EmailField, PasswordField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo
from werkzeug.utils import secure_filename

import os
import re
from config import SECRET_KEY, DEBUG, ADMIN_PASSWORD


app = Flask(__name__)
app.secret_key = SECRET_KEY


UPLOAD_FOLDER = os.path.join(app.root_path, "static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


######### FORMS #########
class LoginForm(FlaskForm):
    email = EmailField("Email", validators=[Email(check_deliverability=True)])
    password = PasswordField("Password", validators=[DataRequired()])


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = EmailField("Email", validators=[Email(check_deliverability=True)])
    password = PasswordField("Password", validators=[
                                                     Regexp(
                                                         regex=r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9])[^\s]{8,}$',
                                                         message="Your password has to be at least 8 characters, "
                                                                 "1 uppercase letter, 1 lowercase letter, 1 digit, "
                                                                 "1 special character, no spaces."
                                                     )])
    confirm = PasswordField("Repeat Password", validators=[EqualTo("password", message="Passwords must match.")])


class AvatarForm(FlaskForm):
    avatar = FileField("✏️", validators=[FileRequired()])
######### FORMS #########


######### DATABASE ##########
class Users:
    def __init__(self):
        self.all = {}

    def count(self):
        return len([key for key, value in self.all.items()])

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return f"User <username: {self.username}; email: {self.email}>"


# INITIALIZING A FAKE DATABASE
users = Users()
######### DATABASE ##########


@app.route("/")
def home():
    if session.get("user"):
        return render_template("index.html", user=session.get("user"), avatar=f"avatars/{session.get('avatar')}")
    return render_template("index.html", user=None, avatar="avatars/default.png")


# AUTHENTICATION LOGIC
@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        return redirect(url_for("home"))
    return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Welcome back!")
        return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    print(session.get("user"))
    if session.get("user")["email"] == "steamkama@gmail.com":
        flash("Good bye, sir!", "messages")
    else:
        flash("Nigga bye!", "messages")
    session.pop("user", None)
    return redirect(url_for("home"))


# OTHER ROUTES
@app.route("/profile", methods=["GET", "POST"])
def profile():
    form = AvatarForm()

    if form.validate_on_submit():
        file = form.avatar.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return render_template("profile.html", form=form)
    return render_template("profile.html", form=form)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=6002)


