import pika
from .. import db_helper


def clean_up_redis(redis_conn):
    for key in redis_conn.scan_iter('test*'):
        redis_conn.delete(key)


def clean_up_postgres(pg_conn):
    pg_conn.query('DELETE FROM scans')


def setup_rabbit_channel(unittest):
    def timeout():
        unittest.fail('consumer timed out while waiting for message')

    # setup new connection and consumer
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=db_helper.RABBIT_HOST))
    connection.add_timeout(5, timeout)
    channel = connection.channel()
    channel.queue_declare(queue=db_helper.RABBIT_QUEUE)

    return channel
