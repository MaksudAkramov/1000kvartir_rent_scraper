import os
import pymongo

from dotenv import load_dotenv


load_dotenv()


client = pymongo.MongoClient(os.environ['MONGODB_URI'])
mydb = client[os.environ['DB_CLIENT_NAME']]
collection = mydb[os.environ['DB_COLLECTION']]


