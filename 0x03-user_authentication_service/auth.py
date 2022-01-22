#!/usr/bin/env python3
""" This module hashes a password and returns it in bytes """
import bcrypt
from sqlalchemy.orm.exc import NoResultFound
from db import DB
from user import User
import uuid


class Auth:
    """Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """ Verifies new user to be stored in database prior to auth """
        try:
            self._db.find_user_by(email=email)
            raise ValueError(f'User <{email}> already exists')
        except NoResultFound:
            hp = _hash_password(password)
            return self._db.add_user(email, hp)

    def valid_login(self, email: str, password: str) -> bool:
        """ Validates hashed password and returns true or false """
        try:
            user = self._db.find_user_by(email=email)
            if bcrypt.checkpw(bytes(password, 'utf-8'), user.hashed_password):
                return True
            return False
        except Exception:
            return False

    def create_session(self, email: str) -> str:
        """ Attach session id to user and return it as a string """
        try:
            user = self._db.find_user_by(email=email)
            sesh_id = _generate_uuid()
            user.session_id = sesh_id
            return sesh_id
        except Exception:
            return ""

    def get_user_from_session_id(self, session_id: str) -> User:
        """ return user based on session id """
        if not session_id:
            return None
        try:
            return self._db.find_user_by(session_id=session_id)
        except Exception:
            return None

    def destroy_session(self, user_id: int) -> None:
        """ Destroys user session """
        try:
            user = self._db.find_user_by(id=user_id)
            user.session_id = None
        except Exception:
            return None

    def get_reset_password_token(self, email: str) -> str:
        """ If user exists creates token for passowrd reset returns token """
        try:
            user = self._db.find_user_by(email=email)
            res_toke = _generate_uuid()
            user.reset_token = res_toke
            return res_toke
        except Exception:
            raise ValueError

    def update_password(self, reset_token: str, password: str) -> None:
        """ Updates and stores User password """
        try:
            user = self._db.find_user_by(reset_token=reset_token)
            hashpw = _hash_password(password)
            self._db.update_user(user.id,
                                 reset_token=None,
                                 hashed_password=hashpw)
        except Exception:
            raise ValueError


def _hash_password(password: str) -> bytes:
    """ salt & pepper the hash browns """
    pdub = bytes(password, 'utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pdub, salt)


def _generate_uuid() -> str:
    """ Generate unique user id for session and return it as string """
    return str(uuid.uuid4())
