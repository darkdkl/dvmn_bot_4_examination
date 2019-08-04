import redis
import os

def redis_connect():
    return redis.Redis(host=os.getenv('REDIS_HOST'), port=12412, db=0, password=os.getenv('REDIS_BASE_PASSWORD'))



if __name__ == "__main__":
    redis_connect()
    