from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from werkzeug.utils import secure_filename
import os
from config import SECRET_KEY, DEBUG, ADMIN_PASSWORD


app = Flask(__name__)
app.secret_key = SECRET_KEY


UPLOAD_FOLDER = os.path.join(app.root_path, "static", "avatars")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    if "email" in session:
        return render_template("index.html", user=session.get("email"), avatar=f"avatars/{session.get('avatar')}")
    return render_template("index.html", user=None, avatar="avatars/default.png")


# AUTHENTICATION LOGIC
@app.route("/login", methods=["GET", "POST"])
def login():
    if "email" not in session:
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            if email == "steamkama@gmail.com":
                if password == ADMIN_PASSWORD:
                    flash("Welcome, Admin!", "messages")
                    session["email"] = email
                else:
                    flash("Invalid admin credentials!", "errors")
                    return render_template("login.html")
            else:
                flash("Welcome, bitch!", "messages")
                session["email"] = email
            return redirect(url_for('home'))
        return render_template("login.html")
    return redirect(url_for("home"))


@app.route("/logout")
def logout():
    session.pop("email", None)
    if session.get("email") == "steamkama@gmail.com":
        flash("Good bye, sir!", "messages")
    else:
        flash("Nigga bye!", "messages")
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


