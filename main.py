from datetime import date, timedelta
import os
import werkzeug
from flask import Flask, abort, render_template, redirect, url_for, flash, request
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, select, ForeignKey, Date
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

    # relations
    reservations = relationship("Reservation", back_populates="user")

class Desk(db.Model):
    __tablename__ = "desks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    open_space_nr: Mapped[str] = mapped_column(Integer, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    image_filename: Mapped[str] = mapped_column(String(100), nullable=True)

    reservations = relationship("Reservation", back_populates="desk")

class Reservation(db.Model):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)

    desk_id: Mapped[int] = mapped_column(ForeignKey("desks.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("desk_users.id"))

    # relations
    desk = relationship("Desk", back_populates="reservations")
    user = relationship("User", back_populates="reservations")

# adding desks
desks = [
    Desk(open_space_nr=1, description="Dual monitors, ergonomic chair, next to window", image_filename="image1.jpg"),
    Desk(open_space_nr=1, description="Single monitor, near kitchen, standing desk", image_filename="image1.jpg"),
    Desk(open_space_nr=1, description="Triple monitors, corner spot, noise-cancelling headphones", image_filename="image1.jpg"),
    Desk(open_space_nr=1, description="Standard desk with lamp, near wall", image_filename="image1.jpg"),
    Desk(open_space_nr=1, description="Dual monitors, high-back chair, under AC", image_filename="image1.jpg"),
    Desk(open_space_nr=1, description="Single monitor, next to team leader", image_filename="image1.jpg"),
    Desk(open_space_nr=1, description="Triple monitors, quiet zone, adjustable chair", image_filename="image1.jpg"),
    Desk(open_space_nr=1, description="Single monitor, whiteboard nearby", image_filename="image1.jpg"),

    Desk(open_space_nr=2, description="Dual monitors, back to window, book shelf nearby", image_filename="image2.jpg"),
    Desk(open_space_nr=2, description="Single monitor, open area, team desk", image_filename="image2.jpg"),
    Desk(open_space_nr=2, description="Corner desk, triple monitors, quiet environment", image_filename="image2.jpg"),
    Desk(open_space_nr=2, description="Height-adjustable desk, ergonomic keyboard", image_filename="image2.jpg"),
    Desk(open_space_nr=2, description="Standard setup, under bright lights", image_filename="image2.jpg"),
    Desk(open_space_nr=2, description="Dual monitors, bean bag next to it", image_filename="image2.jpg"),
    Desk(open_space_nr=2, description="Single monitor, high traffic area", image_filename="image2.jpg"),
    Desk(open_space_nr=2, description="Triple monitors, close to exit", image_filename="image2.jpg"),

    Desk(open_space_nr=3, description="Standing desk, dual monitors, window view", image_filename="image3.jpg"),
    Desk(open_space_nr=3, description="Corner desk, one monitor, quiet side", image_filename="image3.jpg"),
    Desk(open_space_nr=3, description="Dual monitors, near balcony door", image_filename="image3.jpg"),
    Desk(open_space_nr=3, description="Single monitor, center of open space", image_filename="image3.jpg"),
    Desk(open_space_nr=3, description="Triple monitors, storage cabinet nearby", image_filename="image3.jpg"),
    Desk(open_space_nr=3, description="Standard desk, team collaboration area", image_filename="image3.jpg"),
    Desk(open_space_nr=3, description="Dual monitors, by emergency exit", image_filename="image3.jpg"),
    Desk(open_space_nr=3, description="Single monitor, plant decoration nearby", image_filename="image3.jpg"),

    Desk(open_space_nr=4, description="Triple monitors, executive chair, window side", image_filename="image4.jpg"),
    Desk(open_space_nr=4, description="Single monitor, shared table, open space", image_filename="image4.jpg"),
    Desk(open_space_nr=4, description="Dual monitors, creative zone, whiteboard wall", image_filename="image4.jpg"),
    Desk(open_space_nr=4, description="Triple monitors, next to manager desk", image_filename="image4.jpg"),
    Desk(open_space_nr=4, description="Standing desk, ergonomic mat, back to wall", image_filename="image4.jpg"),
    Desk(open_space_nr=4, description="Dual monitors, LED lamp, bookshelf", image_filename="image4.jpg"),
    Desk(open_space_nr=4, description="Standard setup, close to main entrance", image_filename="image4.jpg"),
    Desk(open_space_nr=4, description="Single monitor, couch nearby, relaxed zone", image_filename="image4.jpg"),
]


with app.app_context():
    db.create_all()
    # added all desks to tab
    # db.session.add_all(desks)
    # db.session.commit()


def is_permitted(email: str) -> bool:
    try:
        with open("instance/permitted_users_emails.txt", "r") as f:
            permitted = {line.strip().lower() for line in f}
        return email.lower() in permitted
    except FileNotFoundError:
        return False

@app.route("/", methods=["GET", "POST"])
def index():
    if current_user.is_authenticated:
        user_reservations = Reservation.query.filter_by(user_id=current_user.id).all()
    else:
        user_reservations = None

    return render_template("index.html", reservation=user_reservations)

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

@app.route("/logout", methods=["GET", "POST"])
def log_out():
    logout_user()
    return redirect(url_for('index'))
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

    des = Desk.query.all()
    for d in des:
        for reservation in d.reservations:
            print(reservation.start_date)
        print(f"{d.id}: {d.reservations}")

    return render_template("desk.html")

@app.route("/desk/<int:desk_id>", methods=["GET", "POST"])
@login_required
def desk_detail(desk_id):

    desk = Desk.query.get_or_404(desk_id)

    return render_template("desk_detail.html", desk=desk)

@app.route("/reserve/<int:desk_id>/<int:days>", methods=["POST"])
@login_required
def reserve_desk(desk_id, days):
    desk = Desk.query.get_or_404(desk_id)
    start = date.today() + timedelta(days=1)
    end = start + timedelta(days=days-1)

    overlapping = Reservation.query.filter(
        Reservation.desk_id == desk.id,
        Reservation.start_date <= end,
        Reservation.end_date >= start
    ).first()

    if overlapping:
        flash("Desk already reserved.")
        print('Desk already reserved.')
        return redirect(url_for('desks'))

    new_reserve = Reservation(
        desk_id=desk.id,
        start_date=start,
        end_date=end,
        user_id=current_user.id,
    )
    db.session.add(new_reserve)
    db.session.commit()

    return redirect(url_for('index'))


if __name__ == "__main__":
    app.config['DEBUG'] = True
    app.run(debug=True, port=5002)


# to do:
# add canceling reservations
# add colors to desks buttons which are already reserved
# don't let to reserve to desks at the same day
# reservations expires after 20:00pm each day
# repair the footer
