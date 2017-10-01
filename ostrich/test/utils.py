import pika
from .. import db_helper


HOST = '127.0.0.1'


def clean_up_redis(redis_conn):
    for key in redis_conn.scan_iter('test*'):
        redis_conn.delete(key)


def clean_up_postgres(pg_conn):
    pg_conn.query('DELETE FROM scans')


def setup_rabbit_channel(unittest):
    def timeout():
        unittest.fail('consumer timed out while waiting for message')

    # setup new connection and consumer
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST))
    connection.add_timeout(3, timeout)
    channel = connection.channel()
    channel.queue_declare(queue=db_helper.RABBIT_QUEUE)

    return channel
