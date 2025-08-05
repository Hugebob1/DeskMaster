from datetime import date
import os
import werkzeug
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, select, ForeignKey
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
# Import your forms from the forms.py
from typing import List
from dotenv import load_dotenv
load_dotenv()



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_KEY")

# CREATE DATABASE
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///users.db")
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# CONFIGURE TABLES
class User(UserMixin, db.Model):
    __tablename__ = "desk_users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)


with app.app_context():
    db.create_all()


def is_permitted(email: str) -> bool:
    try:
        with open("instance/permitted_users_emails.txt", "r") as f:
            permitted = {line.strip().lower() for line in f}
        return email.lower() in permitted
    except FileNotFoundError:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def log_in():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('desks'))
            else:
                print('Incorrect password, please try again.')
                flash('Incorrect password, please try again.')
                return redirect(url_for('log_in'))
        else:
            flash('This email hasn\'t been registered.')
            print('This email hasn\'t been registered.')
            return redirect(url_for('register'))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        user_name = request.form.get("username")
        password = request.form.get("password")

        #check for perm in admin file of users
        if not is_permitted(email):
            print("This email is not allowed to register.")
            flash("This email is not allowed to register.", "error")
            return redirect(url_for("index"))

        #check if user already exists
        test_user = User.query.filter_by(email=email).first()
        if test_user:
            flash('Email already registered, please log in!')
            print('Email already registered, please log in!')
            return redirect(url_for('log_in'))

        password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        new_user = User(name=user_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return redirect(url_for('desks'))
    return render_template("register.html")


@app.route("/desks")
@login_required
def desks():
    return render_template("desk.html")


if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run(debug=True, port=5002)
