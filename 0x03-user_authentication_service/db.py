#!/usr/bin/env python3
"""DB module
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import InvalidRequestError
from user import Base, User


class DB:
    """DB class
    """

    def __init__(self) -> None:
        """Initialize a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """ Add user to database and return user object """
        newUser = User(email=email, hashed_password=hashed_password)
        self._session.add(newUser)
        self._session.commit()
        return newUser

    def find_user_by(self, **kwargs) -> User:
        """ Find user by keyword argument and return user from database """
        try:
            q = self._session.query(User).filter_by(**kwargs).first()
            if not q:
                raise NoResultFound
            return q
        except NoResultFound:
            raise NoResultFound
        except Exception:
            raise InvalidRequestError

    def update_user(self, user_id: int, **kwargs) -> None:
        """ Update user and commit changes to database return none """
        try:
            user = self.find_user_by(id=user_id)
        except NoResultFound:
            raise NoResultFound
        except Exception:
            raise InvalidRequestError
        for k, v in kwargs.items():
            try:
                getattr(user, k)
            except Exception:
                raise ValueError
            setattr(user, k, v)
        self._session.commit()
