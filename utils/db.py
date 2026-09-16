# import pymongo
# import pymongo.collection
import logging

# local imports
from utils.user import User, Base

from sqlalchemy import create_engine, insert, select, Sequence
from sqlalchemy.orm import Session

from pymongo import MongoClient
import config


logger = logging.getLogger(__name__)

engine = create_engine("sqlite:///nanobot.db",pool_pre_ping=True)

Base.metadata.create_all(engine)

# temp function to get all the mongodb stuff.
def mongo_migrate():
    client = MongoClient(config.db_URL)
    result = client['db']['users'].find({},{'_id': False})

    all_users = result.to_list()

    with Session(engine) as session:
        for user in all_users:
            temp = User(user['name'])
            temp.level = user['level']
            temp.xp_total = user['xp_total']
            temp.xp_current = user['xp_current']
            temp.total_messages = user['total_messages']
            temp.cooldown = user['cooldown']

            session.add(temp)

        session.commit()

# tests connection to database.
def test_connection() -> bool:
    try:
        with engine.connect():
            return True
    except:
        return False

def add_new_server(server_id: int) -> None:
    pass


def get_users() -> list[User]:
    with Session(engine) as session:
       return list[User](session.scalars(select(User)).all())


def get_user_by_name(name: str) -> User | None:
    with Session(engine) as session:
       return session.scalar(select(User).where(User.name == name))

def gain_xp(name: str) -> bool:
    this_user = get_user_by_name(name)
    is_levelup = False
    with Session(engine) as session:
        if this_user == None:
            this_user = User(name)
            is_levelup = this_user.gain_xp()
            session.add(this_user)

        else:
            this_user = session.query(User).filter(User.name == name).first()
            is_levelup = this_user.gain_xp()

        session.commit()

    return is_levelup