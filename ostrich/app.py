from flask import Flask, g, request
from .db_helper import DbHelper

app = Flask(__name__)


@app.route('/health')
def health():
    return 'Thank you, I am healthy'


@app.route('/add', methods=['POST'])
def add_entry():
    json_data = request.get_json()

    if json_data is not None:
        content = json_data['content']
        key = json_data['key']
        get_db().save_to_db(content, key=key)
        return 'record added'
    else:
        return 'no data provided'


@app.teardown_appcontext
def teardown_db(exception):
    if exception:
        print(exception)
    get_db().teardown_all_db()


def get_db():
    db = getattr(g, '_db_helper', None)
    if db is None:
        db = g._db_helper = DbHelper()
    return db
