import os
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DateTime, REAL
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.base import Engine
from typing import Dict, Text, List, Union, Optional

from random import choice, randrange, sample, randint
from numpy import arange
from datetime import datetime, timedelta
import pytz

utc = pytz.UTC
Base = declarative_base()
class Photo(Base):
    """photo table.
    `session_id` is only meaningful for accounts generated by conversation sessions,
    when it is equal to `tracker.sender_id`.
    Since `id` autoincrements, it is used to generate unique account numbers by
    adding leading zeros to it.
    """

    __tablename__ = "photo"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255))
    photo_thing = Column(String(255))
    photo_position = Column(String(255))

class Fetch(Base):
    """Credit cards table. `account_id` is an `Account.id`"""

    __tablename__ = "fetch"
    id = Column(Integer, primary_key=True)
    session_id = Column(String(255))
    fetch_thing = Column(String(255))
    fetch_position = Column(String(255))

def create_database(database_engine: Engine, database_name: Text):
    """Try to connect to the database. Create it if it does not exist"""
    try:
        database_engine.connect()
    except sa.exc.OperationalError:
        default_db_url = f"sqlite:///{database_name}.db"
        default_engine = sa.create_engine(default_db_url)
        conn = default_engine.connect()
        conn.execute("commit")
        conn.execute(f"CREATE DATABASE {database_name}")
        conn.close()


class chatbotDB:
    def __init__(self, db_engine: Engine):
        self.engine = db_engine
        self.create_tables()
        self.session = self.get_session()

    def get_session(self) -> Session:
        return sessionmaker(bind=self.engine, autoflush=True)()

    def create_tables(self):
        Photo.__table__.create(self.engine, checkfirst=True)
        Fetch.__table__.create(self.engine, checkfirst=True)
        
    def add_session_photo(self, session_id: Text, photo_position: Optional[Text] = "", photo_thing: Optional[Text] = ""):
        """Add a new account for a new session_id. Assumes no such account exists yet."""
        self.session.add(
            Photo(session_id=session_id, photo_position=photo_position, photo_thing= photo_thing)
        )

    def add_session_fetch(self, session_id: Text, fetch_position: Optional[Text] = "", fetch_thing: Optional[Text] = ""):
        """Add a new account for a new session_id. Assumes no such account exists yet."""
        self.session.add(
            Photo(session_id=session_id, fetch_position=photo_position, fetch_thing= photo_thing)
        )





