import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
class Mongo_Client:
    def __init__(self):
        self.username, self.password, self.port = self.get_database_info()
        self.client = self.connect_to_client()
        self.db = self.connect_to_database()
        self.collection = self.connect_to_collection()

    def get_database_info(self):
        try:
            username = os.getenv('MONGO_INITDB_ROOT_USERNAME')
            password = os.getenv('MONGO_INITDB_ROOT_PASSWORD')
            port = os.getenv('MONGO_PORT')
            
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return None
        return username, password, port


    def connect_to_client(self):
        client = MongoClient(f'mongodb://{self.username}:{self.password}@mongodb:27017/?authSource=admin')
        return client
    
    def connect_to_database(self, db_name=os.getenv('DB_NAME')):
        dblist = self.client.list_database_names()
        if db_name not in dblist:
            print(f'{db_name} Will be created!')
        return self.client[db_name]
    
    def connect_to_collection(self, collection_name = os.getenv('COLLECTION_NAME')):
        return self.db[collection_name]
    
    def insert_document(self, document):
        inserted = self.collection.insert_one(document)
        print(inserted.inserted_id)


if __name__ == '__main__':
    mongoc = Mongo_Client()
    