import unittest
import requests
from . import utils
from .. import db_helper


# these tests should be run when the stack is created without owl
class TestApp(unittest.TestCase):

    def setUp(self):
        self.db_helper = db_helper.DbHelper(host=utils.HOST)
        self.content = '<xml>some content</xml>'
        self.scan_name = 'Xmas'
        self.base_url = f'http://{utils.HOST}:6001/'

    def test_health(self):
        r = requests.get(self.base_url + 'health')
        self.assertEqual(r.text, 'Thank you, I am healthy')

    def test_add_entry_fail(self):
        r = requests.post(self.base_url + 'add', data='just a string')
        self.assertEqual(r.text, 'no data provided')

    def test_add_entry(self):

        def callback(ch, method, properties, body):
            print('inside the callback')
            self.assertEqual(body.decode('utf-8'), self.content)
            ch.stop_consuming()
            ch.close()

        # setup rabbitmq channel
        channel = utils.setup_rabbit_channel(self)
        channel.basic_consume(callback, queue=db_helper.RABBIT_QUEUE, no_ack=True)

        redis_db = self.db_helper._redis_conn
        pg_db = self.db_helper._postgres_conn

        utils.clean_up_redis(redis_db)
        utils.clean_up_postgres(pg_db)

        # trigger request
        r = requests.post(self.base_url + 'add',
                          json={'content': self.content, 'key': 'test', 'scan_name': self.scan_name})
        self.assertEqual(r.text, 'record added')
        self.assertEqual(r.status_code, 200)

        # trigger consumer to check rabbitmq
        channel.start_consuming()

        # check redis
        self.assertEqual(redis_db.get('test').decode('utf-8'), self.content)
        # check postgres
        results = pg_db.query('select * from scans').getresult()
        self.assertEqual(results[0][1], self.scan_name)
        self.assertEqual(results[0][2], self.content)

        utils.clean_up_redis(redis_db)
        utils.clean_up_postgres(pg_db)


if __name__ == '__main__':
    unittest.main()
