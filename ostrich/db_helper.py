import redis
import pika
import pg
import time


POSTGRES_HOST = "127.0.0.1"
POSTGRES_PORT = 5432
POSTGRES_DB = "nmap_scan"
POSTGRES_USERNAME = "nmap_app"
POSTGRES_PASSWORD = "pg_password"

RABBIT_HOST = "127.0.0.1"
RABBIT_QUEUE = "nmap_scan_queue"
RABBIT_PORT = 5672
RABBIT_USERNAME = "rabbituser"
RABBIT_PASSWORD = "rabbitpassword"
RABBIT_ERLANG_COOKIE = "erlangcookie"

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_PASSWORD = "redis"


class DbHelper:

    def __init__(self):
        self._postgres_conn = self._connect_to_postgres()
        self._rabbit_conn = self._connect_to_rabbit()
        self._redis_conn = self._connect_to_redis()
        self._setup_postgres_db()
        self._setup_rabbit_queue()

    @staticmethod
    def _connect_to_postgres():
        db = pg.DB(dbname=POSTGRES_DB, host=POSTGRES_HOST, port=POSTGRES_PORT,
                   user=POSTGRES_USERNAME, passwd=POSTGRES_PASSWORD)
        return db

    @staticmethod
    def _connect_to_rabbit():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBIT_HOST))
        return connection.channel()

    @staticmethod
    def _connect_to_redis():
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD)
        return r

    def _setup_postgres_db(self):
        self._postgres_conn.query("CREATE TABLE IF NOT EXISTS scans (id serial primary key, content varchar)")

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
