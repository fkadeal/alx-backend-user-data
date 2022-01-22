#!/usr/bin/env python3
""" Appy flask navigator module """
from flask import Flask, jsonify, request, abort, redirect, url_for
from auth import Auth


AUTH = Auth()
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index() -> str:
    """ GET home dir
    Return:
      - welcome message
    """
    return jsonify({"message": "Bienvenue"})


@app.route('/users', methods=['POST'], strict_slashes=False)
def users():
    """ POST users
    Return:
      - returns json with new email or already registered message
    """
    pw = request.form.get('password')
    email = request.form.get('email')

    try:
        AUTH.register_user(email, pw)
        return jsonify({'email': email, 'message': 'user created'})
    except ValueError:
        return jsonify({'message': 'email already registered'}), 400


@app.route('/sessions', methods=['POST'], strict_slashes=False)
def login():
    """ POST sessions
    Return:
      - returns json with email and logging confirmation
    """
    pw = request.form.get('password')
    email = request.form.get('email')
    if email and AUTH.valid_login(email, pw):
        sesh_id = AUTH.create_session(email)
        resp = jsonify({'email': email, 'message': 'logged in'})
        resp.set_cookie('session_id', sesh_id)
        return resp
    else:
        abort(401)


@app.route('/profile', methods=['GET'], strict_slashes=False)
def get_profile():
    """ GET profile
    Return:
      - return with the user email
    """
    sesh_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(sesh_id)
    if not user:
        abort(403)
    return jsonify({'email': user.email}), 200


@app.route('/sessions', methods=['DELETE'], strict_slashes=False)
def logout():
    """ DELETE sessions
    Return:
      - returns redirection to welcome message
    """
    sesh_id = request.cookies.get('session_id')
    user = AUTH.get_user_from_session_id(sesh_id)
    if not user:
        abort(403)
    AUTH.destroy_session(user.id)
    return redirect(url_for('index'))


@app.route('/reset_password', methods=['POST'], strict_slashes=False)
def get_reset_password_token():
    """ POST reset password
    Return:
      - returns json with email and reset token
    """
    email = request.form.get('email')
    try:
        token = AUTH.get_reset_password_token(email)
        return jsonify({'email': email, 'reset_token': token}), 200
    except Exception:
        abort(403)


@app.route('/reset_password', methods=['PUT'], strict_slashes=False)
def update_password():
    """ PUT update password
    Return:
      - returns json with email and password updated notification
    """
    email = request.form.get('email')
    rt = request.form.get('reset_token')
    np = request.form.get('new_password')
    try:
        AUTH.update_password(rt, np)
        return jsonify({'email': email, 'message': 'Password updated'}), 200
    except Exception as e:
        abort(403)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port="5000")
