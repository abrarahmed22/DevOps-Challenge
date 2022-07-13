import os
import config
import github_api
from db_sqlite import Sqlite
from flask import Flask, render_template


app = Flask(__name__)
db = Sqlite("devOps_challenge.db")
seconds = config.period['seconds'] + config.period['hours'] * 3600 + config.period['days'] * 3600 * 24
github_api.run_job(seconds)


@app.route("/")
def home():
    """
    displays main page from root path
    :return:
    """
    return render_template('index.html')

@app.route('/users')
def show_user_profile():
    """
    it views list of users from database
    :return:
    """
    db.query("select username from users")
    users = db.fetchAll()
    # show the user profile for that user
    return render_template('users.html', users=users)
    # return f'User {escape(username)}'

@app.route('/user/<username>/gists')
def show_user_gists(username):
    """
    It views list of gists from a specific user
    :param username:
    :return:
    """
    db.query("select id, username from {} where username='{}'".format(db.USERS_TABLE, username))
    user_data = db.fetchOne()
    user_id = user_data[0]
    username = user_data[1]

    db.query("select * from {} where user_id='{}'".format(db.GISTS_TABLE, user_id))
    user_gists = db.fetchAll()

    return render_template("gists.html", user_gists=user_gists, username=username)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, threaded=True)  # run our Flask app
