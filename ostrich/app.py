from flask import Flask
from . import db_helper

app = Flask(__name__)


@app.route('/health')
def health():
    return 'Thank you, I am healthy'


@app.route('/add', methods=['POST'])
def add_entry():
    db_helper.save_to_db('hi')
    return 'record added'


@app.teardown_appcontext
def teardown_db(exception):
    if exception:
        print(exception)
    db_helper.teardown_all_db()


with app.app_context():
    db_helper.setup_all_db()
