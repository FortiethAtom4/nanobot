import pymongo
import pymongo.collection

# local imports
import config
from utils.user import User

# tests connection to database.
def test_connection() -> pymongo.MongoClient | int:
    try:
        client = pymongo.MongoClient(config.db_URL)
        return client
    except:
        return -1

def add_new_user(username: str) -> None:
    new_user = User(username)
    config.users.append(new_user)
    config.user_names.append(username)
    config.sort_users_by_rank()
    print(f"new user {username} added to list.")

    
def get_users() -> None:
    try:
        client = pymongo.MongoClient(config.db_URL)
        db = client[config.DB_NAME]
        users = db[config.COLLECTION]

        all_users = users.find({}).to_list()
        ret_list: list[User] = []

        for user in all_users:
            # convert dicts to Player objects
            temp = object.__new__(User)
            temp.__dict__ = user
            ret_list.append(temp)

        config.user_names = [user.name for user in ret_list]
        
        config.users = ret_list
    

        # add new doc to collection with new user

    except Exception as e:
        print(e)

def persist_updates():
    try:
        client = pymongo.MongoClient(config.db_URL)
        db = client[config.DB_NAME]
        users = db[config.COLLECTION]

        users.delete_many({})

        if len(config.users) > 0:
            # prepare list of dicts to persist
            users_to_persist: list[dict] = []
            for user in config.users:
                users_to_persist.append(user.__dict__)

            # update all data
            users.insert_many(users_to_persist)

    except Exception as e:
        print(e)