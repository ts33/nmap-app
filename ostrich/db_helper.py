from functools import partial
from flask import g
import redis
import pika
import pg


RABBIT_HOST = "localhost"
RABBIT_QUEUE = "queue"
RABBIT_PORT = 5672
RABBIT_USERNAME = "rabbituser"
RABBIT_PASSWORD = "rabbitpassword"
RABBIT_ERLANG_COOKIE = "erlangcookie"
REDIS_HOST = "Name"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = 0
POSTGRES_HOST = "Name"
POSTGRES_PORT = 5432
POSTGRES_DB = "Name"
POSTGRES_USERNAME = "Name"
POSTGRES_PASSWORD = "Name"


def __cache_decor(func, tag):
    def ret_func(*args, **kwargs):
        db = getattr(g, f'_{tag}_db', None)
        if db is None:
            db = func(*args, **kwargs)
            setattr(g, f'_{tag}_db', db)
        return db
    return ret_func


cache_db = partial(__cache_decor, argument="")


# https://github.com/andymccurdy/redis-py
def __save_to_redis(content):
    print('saving to redis')
    __connect_to_redis().set('foo', content)


def __save_to_rabbit(content):
    print('saving to rabbit')
    __connect_to_rabbit().basic_publish(exchange='', routing_key=RABBIT_QUEUE, body=content)


# http://www.pygresql.org/contents/tutorial.html
def __save_to_postgres(content):
    print('saving to postgres')
    __connect_tp_postgres().insert('fruits', name='apple')


@cache_db('redis')
def __connect_to_redis():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
    return r


@cache_db('rabbit')
def __connect_to_rabbit():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_QUEUE)
    return channel


@cache_db('postgres')
def __connect_tp_postgres():
    db = pg.DB(dbname=POSTGRES_DB, host=POSTGRES_HOST, port=POSTGRES_PORT,
            user=POSTGRES_USERNAME, passwd=POSTGRES_PASSWORD)
    return db


def setup_all_db():
    __connect_tp_postgres()
    __connect_to_rabbit()
    __connect_to_redis()


def save_to_db(content):
    __save_to_redis(content)
    __save_to_rabbit(content)
    __save_to_postgres(content)


def teardown_all_db():
    __connect_tp_postgres().close()
    __connect_to_rabbit().close()
    __connect_to_redis().connection_pool.disconnect()
