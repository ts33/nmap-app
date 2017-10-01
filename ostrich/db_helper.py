import redis
import pika
import pg
import time
import os


POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_PORT = int(os.environ['POSTGRES_PORT'])
POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_USERNAME = os.environ['POSTGRES_USERNAME']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']

RABBIT_HOST = os.environ['RABBIT_HOST']
RABBIT_PORT = int(os.environ['RABBIT_PORT'])
RABBIT_QUEUE = os.environ['RABBIT_QUEUE']
RABBIT_USERNAME = os.environ['RABBIT_USERNAME']
RABBIT_PASSWORD = os.environ['RABBIT_PASSWORD']

REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = int(os.environ['REDIS_PORT'])
REDIS_DB = int(os.environ['REDIS_DB'])
REDIS_PASSWORD = os.environ['REDIS_PASSWORD']


class DbHelper:

    def __init__(self, host=None):
        if host is not None:
            self._POSTGRES_HOST = host
            self._RABBIT_HOST = host
            self._REDIS_HOST = host
            self._RABBIT_CREDENTIALS = None
        else:
            self._POSTGRES_HOST = POSTGRES_HOST
            self._RABBIT_HOST = RABBIT_HOST
            self._REDIS_HOST = REDIS_HOST
            self._RABBIT_CREDENTIALS = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)

        self._postgres_conn = self._connect_to_postgres()
        self._rabbit_conn = self._connect_to_rabbit()
        self._redis_conn = self._connect_to_redis()
        self._setup_postgres_db()
        self._setup_rabbit_queue()

    def _connect_to_postgres(self):
        db = pg.DB(dbname=POSTGRES_DB, host=self._POSTGRES_HOST, port=POSTGRES_PORT,
                   user=POSTGRES_USERNAME, passwd=POSTGRES_PASSWORD)
        return db

    def _connect_to_rabbit(self):
        if self._RABBIT_CREDENTIALS is None:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=self._RABBIT_HOST))
        else:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self._RABBIT_HOST, credentials=self._RABBIT_CREDENTIALS))
        return connection.channel()

    def _connect_to_redis(self):
        r = redis.StrictRedis(host=self._REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
        return r

    def _setup_postgres_db(self):
        self._postgres_conn.query('CREATE TABLE IF NOT EXISTS scans (id serial primary key, content varchar)')

    def _setup_rabbit_queue(self):
        self._rabbit_conn.queue_declare(queue=RABBIT_QUEUE)

    # http://www.pygresql.org/contents/tutorial.html
    def _save_to_postgres(self, content):
        print('saving to postgres')
        self._postgres_conn.insert('scans', content=content)

    # https://www.rabbitmq.com/tutorials/tutorial-one-python.html
    def _save_to_rabbit(self, content):
        print('saving to rabbit')
        self._rabbit_conn.basic_publish(exchange='', routing_key=RABBIT_QUEUE, body=content,
                                        properties=pika.BasicProperties(delivery_mode=2))

    # https://github.com/andymccurdy/redis-py
    def _save_to_redis(self, content, key=None):
        print('saving to redis')
        if key is None:
            key = self._unix_timestamp()
        self._redis_conn.set(key, content)

    @staticmethod
    def _unix_timestamp():
        return str(int(time.time()))

    def save_to_db(self, content, key=''):
        self._save_to_postgres(content)
        self._save_to_rabbit(content)
        self._save_to_redis(content, key)

    def teardown_all_db(self):
        self._postgres_conn.close()
        self._rabbit_conn.close()
        self._redis_conn.connection_pool.disconnect()
