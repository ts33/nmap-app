import unittest
from .. import db_helper
from . import utils


# these tests should be run when the stack is created
class TestDbHelper(unittest.TestCase):

    def setUp(self):
        self.db_helper = db_helper.DbHelper(host=utils.HOST)
        self.content = '<xml>some content</xml>'
        self.open = True

    def tearDown(self):
        if self.open:
            self.db_helper.teardown_all_db()

    def test_connect_to_postgres(self):
        db = self.db_helper._postgres_conn
        self.assertEqual(db.get_tables(), ['public.scans'])

    def test_connect_to_rabbit(self):
        db = self.db_helper._rabbit_conn
        self.assertEqual(db.is_open, True)

    def test_connect_to_redis(self):
        db = self.db_helper._redis_conn
        self.assertEqual(db.ping(), True)

    def test_save_to_postgres(self):
        db = self.db_helper._postgres_conn
        # remove all records first
        utils.clean_up_postgres(db)

        self.db_helper._save_to_postgres(self.content)
        results = db.query('select * from scans').getresult()
        self.assertEqual(results[0][1], self.content)

        # clean up
        utils.clean_up_postgres(db)

    def test_save_to_rabbit(self):

        def callback(ch, method, properties, body):
            self.assertEqual(body.decode('utf-8'), self.content)
            ch.stop_consuming()
            ch.close()

        # setup new connection and consumer
        channel = utils.setup_rabbit_channel(self)
        channel.basic_consume(callback, queue=db_helper.RABBIT_QUEUE, no_ack=True)

        self.db_helper._save_to_rabbit(self.content)
        channel.start_consuming()

    def test_save_to_redis(self):
        db = self.db_helper._redis_conn
        utils.clean_up_redis(db)

        self.db_helper._save_to_redis(self.content, key='test')
        self.assertEqual(db.get('test').decode('utf-8'), self.content)

        utils.clean_up_redis(db)


if __name__ == '__main__':
    unittest.main()
