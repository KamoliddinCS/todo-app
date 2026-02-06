from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from werkzeug.utils import secure_filename
import os
from config import SECRET_KEY, DEBUG, ADMIN_PASSWORD


app = Flask(__name__)
app.secret_key = SECRET_KEY


UPLOAD_FOLDER = os.path.join(app.root_path, "static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


class Users:
    def __init__(self):
        self.all = {}

    def count(self):
        return len([key for key, value in self.all.items()])

    # def add_user(self, user):
    #     self.all[self.count() + 1] = user

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def __str__(self):
        return f"User <username: {self.username}; email: {self.email}>"


# INITIALIZING A FAKE DATABASE
users = Users()


@app.route("/")
def home():
    if session.get("user"):
        return render_template("index.html", user=session.get("user"), avatar=f"avatars/{session.get('avatar')}")
    return render_template("index.html", user=None, avatar="avatars/default.png")


# AUTHENTICATION LOGIC
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if not session.get("user"):
        if request.method == "POST":
            username = request.form["username"]
            email = request.form["email"]
            password = request.form["password"]
            re_password = request.form["re-password"]

            usernames, emails = [i.username for i in users.all.values()], [i.email for i in users.all.values()]
            print(usernames, emails)
            if username in usernames or email in emails:
                flash("This username or email already exists. Please, try again.", "errors")
                return render_template("signup.html")
            else:
                if password != re_password:
                    flash("Both passwords must be the same.", "errors")
                    return render_template("signup.html")
                new_user = User(username, email, password)
                print("creating a user works")
                users.all[users.count()+1] = new_user
                print("adding a user to the users works")
                session["user"] = {
                    "username": username,
                    "email": email
                }
                return redirect(url_for("home"))
        return render_template("signup.html")
    return redirect(url_for("home"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if not session.get("user"):
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")

            if email == "steamkama@gmail.com":
                if password == ADMIN_PASSWORD:
                    flash("Welcome, Admin!", "messages")
                    admin_user = [user for user in users.all.values() if user.email == email][0]
                    session["user"] = {
                        "username": admin_user.username,
                        "email": admin_user.email
                    }
                    return redirect(url_for("home"))
                else:
                    flash("Invalid admin credentials!", "errors")
                    return render_template("login.html")
            else:
                emails = [user.email for user in users.all.values()]
                if email not in emails:
                    flash("A user with this email does not exist. Please, sign up.", "errors")
                    return render_template("login.html")
                else:
                    user = [user for user in users.all.values() if email == user.email][0]
                    if password != user.password:
                        flash("Incorrect password! Try again.", "errors")
                        return render_template("login.html", email=email)
                    else:
                        flash("Welcome, bitch!", "messages")
                        session["user"] = {
                            "username": user.username,
                            "email": email
                        }
                        return redirect(url_for('home'))
        return render_template("login.html")
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    print(session.get("user"))
    if session.get("user")["email"] == "steamkama@gmail.com":
        flash("Good bye, sir!", "messages")
    else:
        flash("Nigga bye!", "messages")
    session.pop("user", None)
    return redirect(url_for("home"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "email" in session:
        if request.method == "POST":
            file = request.files["avatar"]
            file.save(os.path.join(UPLOAD_FOLDER, secure_filename(file.filename)))
            session["avatar"] = file.filename
            return redirect(url_for("home"))
        return render_template("profile.html", image=f"avatars/{session.get('avatar')}", email=session.get("email"))
    return redirect(url_for("home"))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=DEBUG, host="0.0.0.0", port=6002)


