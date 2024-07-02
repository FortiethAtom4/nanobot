# module for database access/handling.

import pymongo
import os
from dotenv import load_dotenv
import entities

# for converting JSON payloads to Python objects.
import json
from json import JSONEncoder

# get username and password of user to connect to cluster.
load_dotenv()
USER = os.getenv("MONGODB_USER")
PASS = os.getenv("MONGODB_PASS")

# tests connection to database.
def test_connection():
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{USER}:{PASS}@nanobot.lab1zmc.mongodb.net/")
        return client
    except:
        return -1
    

# Add a new user to the user_stats collection.
# returns a subclass of Entity matching the class the player chose on success. 
# Returns -1 on failure.
def insert_new_user(name,pclass: str):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{USER}:{PASS}@nanobot.lab1zmc.mongodb.net/")
        db = client["db"]
        users = db["users"]
        isnewplayer = list(users.find({"name":name}))
        if len(isnewplayer) != 0:
            return -1

        return_entity = entities.Entity(name)
        match(pclass.lower()):
            case "warrior":
                return_entity.init_warrior()

            case "mage":
                return_entity.init_mage()

            case "ranger":
                return_entity.init_ranger()

            case "general":
                return_entity.init_general()

            case "trickster":
                return_entity.init_trickster()

            case _:
                print("fail")
                return -1

        ret = users.insert_one(vars(return_entity))
        # quick print to see if it worked
        print(ret)
        return return_entity
    except:
        return -1

# get stats of a specific user from the cluster.
def find_user(name):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{USER}:{PASS}@nanobot.lab1zmc.mongodb.net/")
        db = client["db"]
        users = db["users"]
        isnewplayer = users.find_one({"name":name})
        if not isnewplayer:
            return -1
        
        isnewplayer = dict(isnewplayer)
        del isnewplayer["_id"]
        return_entity = entities.Entity(isnewplayer.get("name"))
        del isnewplayer["name"]

        return_entity.init_from_dict(**isnewplayer)
        return return_entity

    except Exception as e:
        print(e)
        return -1
    
# Update a user's stats in the cluster with their local stats.
def update_stats(entity: entities.Entity):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{USER}:{PASS}@nanobot.lab1zmc.mongodb.net/")
        db = client["db"]
        users = db["users"]
        updatedstats = entity.__dict__
        users.update_one({"name":entity.name},{"$set":updatedstats})
        return "Stats successfully updated."
    except Exception as e:
        print(e)
        return "Stat update failure"
    
def delete_user(name: str):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{USER}:{PASS}@nanobot.lab1zmc.mongodb.net/")
        db = client["db"]
        users = db["users"]
        users.delete_one({"name":name})
        return "Stats successfully deleted."
    except Exception as e:
        print(e)
        return -1
    
def insert_enemy(enemy: entities.Enemy):
    try:
        client = pymongo.MongoClient(f"mongodb+srv://{USER}:{PASS}@nanobot.lab1zmc.mongodb.net/")
        db = client["db"]
        enemies = db["enemies"]
        if not enemies.find_one({"name":enemy.name}):
            enemies.insert_one(enemy.__dict__)
            print(f"Enemy \"{enemy.name}\" successfully inserted.")
        else:
            raise Exception(f"Enemy \"{enemy.name}\" already exists.")
    except Exception as e:
        print(e)
        return -1