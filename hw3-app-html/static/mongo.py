from pymongo import MongoClient
import os

# dont know if needed
from dotenv import load_dotenv


load_dotenv()
#

# Replace the uri string with your MongoDB deployment's connection string.
uri = os.getenv("URI")
client = MongoClient(uri)

# database and collection code goes here
# insert code goes here
# display the results of your operation

# Close the connection to MongoDB when you're done.
client.close()
