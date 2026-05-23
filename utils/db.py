import pymongo
import pymongo.collection
import logging

# local imports
import config
from utils.user import User

logger = logging.getLogger(__name__)

# tests connection to database.
def test_connection() -> bool:
    try:
        client = pymongo.MongoClient(config.db_URL)
        client.server_info()
        return True
    except:
        return False

def add_new_user(username: str) -> None:
    new_user = User(username)
    config.users.append(new_user)
    config.user_names.append(username)
    config.sort_users_by_rank()
    print(f"new user {username} added to list.")

def add_new_server(server_id: int) -> None:
    pass

    
def get_users() -> None:
    try:
        client = pymongo.MongoClient(config.db_URL)
        db = client[config.DB_NAME]
        users = db[config.COLLECTION]

        all_users = users.find({}).to_list()
        ret_list: list[User] = []

        for user in all_users:
            # convert dicts to User objects
            temp = object.__new__(User)
            temp.__dict__ = user
            ret_list.append(temp)

        config.user_names = [user.name for user in ret_list]
        
        config.users = ret_list

        # add new doc to collection with new user

    except Exception as e:
        print(e)

def persist_updates() -> int:
    try:
        client = pymongo.MongoClient(config.db_URL)
        db = client[config.DB_NAME]
        users = db[config.COLLECTION]

        if len(config.users) > 0:
            users.delete_many({})
            # prepare list of dicts to persist
            users_to_persist: list[dict] = []
            for user in config.users:
                users_to_persist.append(user.__dict__)

            # update all data
            users.insert_many(users_to_persist)

            # OK
            logger.info("DB auto-update completed")
            return 0

    except Exception as e:

        # something went wrong
        logger.warning(f"Something went wrong persisting updates to DB: {e}")
        return 1

    # nothing to do
    logger.info("No DB update, nothing to do")
    return 2