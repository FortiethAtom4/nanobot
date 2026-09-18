# import pymongo
# import pymongo.collection
import logging


# local imports
from utils.models import OldUser, User, Base
import datetime

from sqlalchemy import create_engine, insert, select, Sequence, delete
from sqlalchemy.orm import Session

from pymongo import MongoClient
import config


logger = logging.getLogger(__name__)

engine = create_engine("sqlite:///nanobot.db",pool_pre_ping=True)

Base.metadata.create_all(engine)

# tests connection to database.
def test_connection() -> bool:
    try:
        with engine.connect():
            return True
    except:
        return False

def get_all_users() -> list[User]:
    '''Gets ALL users in the db. Could be costly, depending on db size. Use with caution.'''
    with Session(engine) as session:
       return list[User](session.scalars(select(User)))

def get_users(server_id: int) -> list[User]:
    with Session(engine) as session:
       to_return = list[User](session.scalars(select(User).where(User.server_id == server_id)))
       config.sort_users_by_rank(to_return)
       return to_return

def get_user_by_name(server_id: int, name:str):
    with Session(engine) as session:
       return session.scalar(select(User).where(User.name == name and User.server_id == server_id).limit(1))

def get_old_user_by_name(name: str) -> OldUser | None:
    with Session(engine) as session:
       return session.scalar(select(OldUser).where(OldUser.name == name))

def get_user_by_ids(server_id: int, user_id: int):
    with Session(engine) as session:
       return session.scalar(select(User).where(User.user_id == user_id and User.server_id == server_id))


def gain_xp(server_id: int, user_id: int, name: str) -> bool:
    this_user = get_user_by_ids(server_id,user_id)
    is_levelup = False
    with Session(engine) as session:
        if this_user == None:
            this_user = User(server_id,user_id, name)
            old_user = get_old_user_by_name(name)
            if old_user != None and (old_user.found == 0 or old_user.found == None):
                print("transfering data for user " + name + "...")
                this_user.level = old_user.level
                this_user.xp_current = old_user.xp_current
                this_user.xp_total = old_user.xp_total
                this_user.xp_cooldown = old_user.xp_cooldown
                this_user.total_messages = old_user.total_messages

                old_user = session.query(OldUser).filter(OldUser.name == name).first()
                old_user.found = 1
            
            is_levelup = this_user.gain_xp()
            session.add(this_user)

        else:
            this_user = session.query(User).filter(User.user_id == user_id and User.server_id == server_id).first()
            is_levelup = this_user.gain_xp()

        session.commit()

    return is_levelup

def init_from_old_user(server_id: int, user_id: int, other_user: OldUser):
    '''function to port old users to new table.'''
    user: User = User(0,0,other_user.name)

    user.server_id: int = server_id
    user.user_id: int = user_id
    user.level: int = other_user.level
    user.xp_current: int = other_user.xp_current
    user.xp_total: int = other_user.xp_total
    user.total_messages: int = other_user.total_messages
    user.cooldown: datetime.datetime = other_user.cooldown

    return user

def port_user(server_id: int, user_id: int, name: str) -> bool:
    is_already_user = get_user_by_name(server_id,name)
    if is_already_user != None:
        return False

    the_old_user = get_old_user_by_name(name)
    if the_old_user == None:
        return False

    new_user = init_from_old_user(server_id,user_id,the_old_user)
    with Session(engine) as session:
        old_user = session.query(OldUser).filter(OldUser.name == name).first()
        old_user.found = 1
        session.add(new_user)
        session.commit()

    return True

    