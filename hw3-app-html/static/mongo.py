import pymongo
from pymongo import MongoClient
import os

# dont know if needed
from dotenv import load_dotenv


load_dotenv()
#

# Replace the uri string with your MongoDB deployment's connection string.
uri = os.getenv("URI")
cluster = MongoClient(uri)
db = cluster["users"]
reg_user_collection = db["regular"]
admin_user_collection = db["admins"]
# database and collection code goes here
# insert code goes here
# display the results of your operation


# test = {
#     "user": "Kyle",
#     "username": "klam36",
#     "pass": "test"
# }
# reg_user_collection.insert_one(test)


def get_user_by_email(email):
    return db["users"].find_one({"email": email})

# Close the connection to MongoDB when you're done.
cluster.close()
