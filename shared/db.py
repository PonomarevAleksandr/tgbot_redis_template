"""MongoDb Custom ORM for simple use collection
    You can use db.collection.method({})"""
from typing import List, Any

import motor.motor_asyncio
import redis

from pydantic import BaseModel

from shared.models.user import User
from shared.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(
    f'mongodb://{settings.MONGO_USERNAME}:'
    f'{settings.MONGO_PASSWORD}@'
    f'{settings.MONGO_HOST}:'
    f'{settings.MONGO_PORT}')
raw_db = client[settings.MONGO_DB_NAME]

external_client = motor.motor_asyncio.AsyncIOMotorClient(
    f'mongodb://{settings.MONGO_USERNAME}:'
    f'{settings.MONGO_PASSWORD}@'
    f'{settings.MONGO_HOST_EXTERNAL}:'
    f'{settings.MONGO_PORT_EXTERNAL}')
external_db = external_client[settings.MONGO_DB_NAME]
rdb = redis.Redis(host=settings.REDIS_HOST, port=int(settings.REDIS_PORT),
                  password=settings.REDIS_PASSWORD)


class Collection:
    """
    Methods MongoDb
    """

    def __init__(self, model, collection_name: str):
        self.collection = client[settings.MONGO_DB_NAME][collection_name]
        self.model = model

    async def find_one(self, f: dict):
        """
        await db.collection.find_one
        :param f:
        :return: an instance of the model (self.model) or None if no document is found.

        """
        data = await self.collection.find_one(f)
        if not data:
            return None
        data['_id'] = str(data['_id'])
        model = self.model(**data)
        return model

    async def find(self, f: dict, count: int = 100000, offset: int = 0) -> List:
        """
        await db.collection.find
        :param f:
        :param count:
        :param offset:
        :return: a list of instances of the model (self.model).
        """
        cursor = self.collection.find(f).skip(offset).limit(count)
        data = await cursor.to_list(length=count)
        list_models = []
        for item in data:
            item['_id'] = str(item['_id'])
            list_models.append(self.model(**item))
        return list_models

    async def update_one(self, f: dict, s: dict, upsert: bool = False):
        """
        await db.collection.update_one
        :param f:
        :param s:
        :param upsert:
        :return: the result of the operation (UpdateResult).
        """
        res = await self.collection.update_one(f, {'$set': s}, upsert=upsert)
        return res

    async def delete_one(self, f: dict, ):
        """
        await db.collection.delete_one
        :param f:
        :return: the result of the operation (DeleteResult).
        """
        res = await self.collection.delete_one(f)
        return res

    async def delete_many(self, f: dict, ):
        """
        await db.collection.delete_many
        :param f:
        :return: the result of the operation (DeleteResult).
        """
        res = await self.collection.delete_many(f)
        return res

    async def update_many(self, f: dict, s: dict):
        """
        await db.collection.update_many
        :param f:
        :param s:
        :return: the result of the operation (UpdateResult).
        """
        res = await self.collection.update_many(f, s)
        return res

    async def count(self, f: dict):
        """
        return count of collection
        :param f:
        :return: the number of documents (int).
        """
        res = await self.collection.count_documents(f)
        return res

    async def insert_one(self, i: dict):
        """
        await db.collection.insert_one
        :param i:
        :return: the result of the operation (InsertOneResult).
        """
        res = await self.collection.insert_one(i)
        return res

    async def push(self, criteria: dict, field: str, values: list, upsert: bool = False):
        """
        Push values into an array field in a document.
        :param criteria: criteria to find the document
        :param field: The array field to push to
        :param values: The values to add to the array
        :param upsert: Whether to insert the document if it does not exist
        :return: The result of the operation (UpdateResult)
        """
        if not isinstance(values, list):
            values = [values]  # Ensure values is always a list

        update_query = {"$push": {field: {"$each": values}}}
        result = await self.collection.update_one(criteria, update_query, upsert=upsert)
        return result

    async def push_many(self, criteria: dict, updates: dict, upsert: bool = False):
        """
        Push multiple values into array fields in a document.
        :param criteria: criteria to find the document
        :param updates: Dictionary where keys are field names and values are lists of values to push
        :param upsert: Whether to insert the document if it does not exist
        :return: The result of the operation (UpdateResult)
        """
        push_query = {"$push": {field: {"$each": values} for field, values in updates.items()}}
        result = await self.collection.update_one(criteria, push_query, upsert=upsert)
        return result

class MongoDbClient(BaseModel):
    """
    MongoDb models initiate
    """
    users: Any


db = MongoDbClient(
    users=Collection(collection_name="users", model=User)
)