from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

from app.models.models import User
from config import db

auth_bp = Blueprint('auth', __name__)
admin_bp = Blueprint('admin', __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("User does not exist", "danger")
            return render_template("login.html")

        # Check if the user's password is empty or None
        if not user.password or user.is_new:
            flash("You must change your password before proceeding.", "warning")
            login_user(user)  # Log in the user first
            return redirect(url_for("auth.change_password", show_modal=True))  # Redirect with a flag

        # Validate the provided password
        if user.check_password(password):
            login_user(user)
            return redirect(url_for("auth.dashboard"))

        else:
            flash("Invalid credentials", "danger")

    return render_template("login.html")


@auth_bp.route('/admin/dashboard')
@login_required
def admin_dashboard():
    return render_template('admin_dashboard.html')


@auth_bp.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html')


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        new_password = request.form['password']
        current_user.set_password(new_password)  # Set the new password
        current_user.is_new = False
        db.session.commit()  # Save changes to the database
        flash('Your password has been updated!', 'success')
        return redirect(url_for('auth.login'))  # Redirect to user dashboard or another page

    show_modal = request.args.get('show_modal', 'false') == 'true'  # Check for show_modal parameter
    return render_template('change_password.html', show_modal=show_modal)


# Logout Route
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# Admin Dashboard Route
@auth_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        users = User.query.all()
        return render_template("admin_dashboard.html", users=users)
    return render_template("user_dashboard.html")


# Admin User Creation Route
@auth_bp.route("/admin/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.is_admin:
        return redirect(url_for("auth.dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        is_admin = request.form.get("is_admin") == "on"

        # If no password is provided, create the user without a password
        new_user = User(username=username, email=email, is_admin=is_admin, is_new=True)
        if password:
            new_user.set_password(password)

        new_user.create_uid = current_user.id
        new_user.write_uid = current_user.id

        db.session.add(new_user)
        db.session.commit()

        flash("User created successfully", "success")
        return redirect(url_for("auth.dashboard"))

    return render_template("create_user.html")


# Admin User Deletion Route
@auth_bp.route("/admin/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return redirect(url_for("auth.dashboard"))

    user_to_delete = User.query.get(user_id)
    if user_to_delete:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User deleted successfully", "success")
    else:
        flash("User not found", "danger")

    return redirect(url_for("auth.dashboard"))


