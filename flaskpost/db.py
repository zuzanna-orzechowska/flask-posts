import redis
import json
import os
from flask import current_app

class RedisDB:
    def __init__(self):
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        self.r = redis.Redis(host='redis-service', port=6379, decode_responses=True)

    def lrange(self, key, start, end):
        return self.r.lrange(key, start, end)
    
    def exists(self, key):
        return self.r.exists(key)

    def incr(self, key):
        return self.r.incr(key)

    def llen(self, key):
        return self.r.llen(key)

    def hset(self, key, mapping):
        return self.r.hset(key, mapping=mapping)

    def rpush(self, key, *values):
        return self.r.rpush(key, *values)

    def set(self, key, value):
        return self.r.set(key, value)

    def get(self, key):
        return self.r.get(key)
    
    def hgetall(self, key):
        return self.r.hgetall(key)

    def delete(self, key):
        return self.r.delete(key)
    
    def lrem(self, name, count, value):
        return self.r.lrem(name, count, value)

    def add_post(self, post_data):
        post_id = self.r.incr('post:id')
        key = f'post:{post_id}'
        self.r.set(key, json.dumps(post_data))
        self.r.lpush('post_ids', post_id)
        return post_id


    def get_post(self, post_id):
        key = f'post:{post_id}'
        post_json = self.r.get(key)
        if post_json:
            return json.loads(post_json)
        return None

    def get_all_posts(self):
        keys = self.r.keys('post:*')
        return [json.loads(self.r.get(k)) for k in keys if k != 'post:id']
    

def init_app(app):
    app.redis_db = RedisDB()

def get_db():
    return current_app.redis_db