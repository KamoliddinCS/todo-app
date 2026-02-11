from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash, Response
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from wtforms import StringField, EmailField, PasswordField, BooleanField, TextAreaField, SelectField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Regexp, EqualTo, ValidationError, Length, Optional
from werkzeug.utils import secure_filename

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Integer, String, select, or_, desc
from flask_migrate import Migrate
from init_db import db

from flask_login import LoginManager, login_required, login_user, current_user, logout_user

import os
import re
from config import SECRET_KEY, DEBUG, ADMIN_PASSWORD, SQLALCHEMY_DATABASE_URI, FLASK_APP


######### CONFIGURATIONS ###########
app = Flask(__name__)
app.secret_key = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


######### FORMS #########
class LoginForm(FlaskForm):
    identifier = StringField("Username or email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember me")


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

    def validate_username(self, field):
        stmt = select(User.id).where(User.username == field.data)
        if db.session.execute(stmt).first() is not None:
            raise ValidationError("That username is already taken.")

    def validate_email(self, field):
        stmt = select(User.id).where(User.email == field.data)
        if db.session.execute(stmt).first() is not None:
            raise ValidationError("That email is already registered.")


class AvatarForm(FlaskForm):
    avatar = FileField("Change avatar", validators=[FileRequired()])


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    status = SelectField("Status",
                         choices=[("todo", "To do"), ("doing", "Doing"), ("done", "Done")],
                         default="todo",
                         validators=[DataRequired()])
    priority = SelectField("Priority",
                           choices=[("1", "Low"), ("2", "Medium"), ("3", "High")],
                           default="1",
                           validators=[DataRequired()])
    due_at = DateTimeLocalField("Due", format="%Y-%m-%dT%H:%M", validators=[Optional()])
######### FORMS #########


######### DATABASE ##########
# INITIALIZING A DATABASE
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
db.init_app(app)
migrate = Migrate(app, db)

from models import User, Task
print(list(db.metadata.tables.keys()))
######### DATABASE ##########


def get_owned_task(task_id: int) -> Task:
    stmt = select(Task).where(Task.id == task_id, Task.user_id == current_user.id)
    task = db.session.execute(stmt).scalar_one_or_none()
    return task


@app.route("/")
def home():
    if current_user.is_authenticated:
        task_form = TaskForm()

        stmt = (
            select(Task)
            .where(Task.user_id == current_user.id)
            .order_by(desc(Task.priority), Task.due_at.is_(None), Task.due_at)
        )
        tasks = db.session.execute(stmt).scalars().all()
        if not tasks:
            return render_template("index.html", avatar=f"avatars/{current_user.avatar}", tasks=None, form=task_form)
        return render_template("index.html", avatar=f"avatars/{current_user.avatar}", tasks=tasks, form=task_form)
    return render_template("index.html", avatar=f"avatars/default.png")


# AUTHENTICATION LOGIC
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if not current_user.is_authenticated:
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(
                username=form.username.data,
                email=form.email.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
                login_user(user)
            except IntegrityError:
                db.session.rollback()
                form.username.errors.append("Username or email already exists.")
                form.email.errors.append("Username or email already exists.")
            return redirect(url_for("home"))
        return render_template("signup.html", form=form)
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            identifier = form.identifier.data.strip()
            stmt = select(User).where(or_(User.username == identifier, User.email == identifier))
            user = db.session.execute(stmt).scalar_one_or_none()

            if user is None or not user.check_password(form.password.data):
                flash("Invalid credentials.", "error")
                return render_template("login.html", form=form), 401

            login_user(user, remember=form.remember_me.data)

            # redirect back to the page the user originally wanted, if safe
            next_url = request.args.get("next")
            if next_url and next_url.startswith("/"):
                flash("Welcome back!")
                return redirect(next_url)
            flash("Welcome back!")
            return redirect(url_for("home"))
        return render_template("login.html", form=form)
    return redirect(url_for("home"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


# OTHER ROUTES
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    form = AvatarForm()

    if form.validate_on_submit():
        file = form.avatar.data
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))

        current_user.avatar = filename
        db.session.commit()

        flash("Avatar updated successfully!", "messages")
        return render_template("profile.html", form=form, avatar=f"avatars/{current_user.avatar}")
    return render_template("profile.html", form=form, avatar=f"avatars/{current_user.avatar}")


######### TASKS LOGIC ##############
# CREATE A TASK
@app.get("/tasks/new")
@login_required
def tasks_new():
    form = TaskForm()
    return render_template(
        "tasks/_task_modal_form.html",
        form=form,
        action_url=url_for("tasks_create"),
        submit_label="Add",
        target="#todo-list",
        swap="afterbegin",
    )


@app.post("/tasks")
@login_required
def tasks_create():
    form = TaskForm()
    if not form.validate_on_submit():
        return render_template(
            "tasks/_task_modal_form.html",
            form=form,
            action_url=url_for("tasks_create"),
            submit_label="Add",
            target="#todo-list",
            swap="afterbegin",
        ), 400

    task = Task(
        title=form.title.data,
        description=form.description.data,
        status=form.status.data,
        priority=int(form.priority.data),
        due_at=form.due_at.data,
        user_id=current_user.id,
    )
    db.session.add(task)
    db.session.commit()

    resp = Response(render_template("tasks/_task_row.html",
                                    action_url=url_for("tasks_update", task_id=task.id),
                                    task=task))
    resp.headers["HX-Trigger"] = "closeModal"
    return resp


@app.get("/tasks/<int:task_id>/edit")
@login_required
def tasks_edit(task_id: int):
    task = get_owned_task(task_id)

    form = TaskForm(obj=task)
    # SelectField uses strings:
    form.priority.data = str(task.priority)
    form.status.data = task.status

    return render_template(
        "tasks/_task_modal_form.html",
        form=form,
        action_url=url_for("tasks_update", task_id=task.id),
        submit_label="Save",
        target=f"#task-{task.id}",
        swap="outerHTML",
        task=task,
    )


@app.post("/tasks/<int:task_id>")
@login_required
def tasks_update(task_id: int):
    task = get_owned_task(task_id)
    form = TaskForm()

    if not form.validate_on_submit():
        # Return modal content again (with errors)
        return render_template(
            "tasks/_task_modal_form.html",
            form=form,
            action_url=url_for("tasks_update", task_id=task.id),
            submit_label="Save",
            target=f"#task-{task.id}",
            swap="outerHTML",
            task=task,
        ), 400

    task.title = form.title.data
    task.description = form.description.data
    task.status = form.status.data
    task.priority = int(form.priority.data)
    task.due_at = form.due_at.data

    db.session.commit()

    html = render_template("tasks/_task_row.html", task=task)

    resp = Response(html, status=200)
    resp.headers["HX-Trigger"] = "closeModal"   # ✅ close after save
    return resp


@app.post("/tasks/<int:task_id>/update_status")
@login_required
def update_task_status(task_id: int):
    task = get_owned_task(task_id)

    current_status = request.args["current_status"]
    if current_status == "todo" or current_status == "doing":
        task.status = "done"
        db.session.commit()
    else:
        task.status = "todo"
        db.session.commit()

    html = render_template("tasks/_task_row.html", task=task)

    resp = Response(html, status=200)
    # resp.headers["HX-Trigger"] = "closeModal"   # ✅ close after save
    return resp


# DELETE A TASK
@app.post("/tasks/<int:task_id>/delete")
@login_required
def tasks_delete(task_id: int):
    task = get_owned_task(task_id)
    db.session.delete(task)
    db.session.commit()
    return Response("", status=200)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":

    app.run(debug=DEBUG, host="0.0.0.0", port=6002)



