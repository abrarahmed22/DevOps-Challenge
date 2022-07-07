import pytz
import atexit
import config
import logging
import datetime
import requests
from db_sqlite import Sqlite
from importlib import reload
from flask_apscheduler import APScheduler


reload(logging)
logging.basicConfig(filename='logs.log', filemode='a',format='%(asctime)s - %(message)s', level=logging.INFO)

db = Sqlite("devOps_challenge.db")
db.query(db.createUserTable())
db.query(db.createGistsTable())
db.query(db.createActivityTable())


def getDateTimeNow():
    return datetime.datetime.now(pytz.utc).strftime('%d/%m/%Y, %H:%M:%S')

def getUsers():
    """
    It requests to github users api to get list of users
    :return: LIST OF USERS
    """
    results = []
    try:
        url = config.LIST_USERS
        resp = requests.get(url)
        users = resp.json()
        for user in users:
            db.query("select * from {} where username='{}'".format(db.USERS_TABLE, user['login']))
            user_exist = db.fetchOne()
            if not user_exist:
                db.query_insert(db.USERS_TABLE, [user['id'], user['login'], user['html_url'], datetime.datetime.today(), datetime.datetime.today()])
                last_row_id = db.cursor_.lastrowid
            else:
                last_row_id = user_exist[0]
            results.append({'username': user['login'], 'id': last_row_id, "html_url": user['html_url']})
        db.commit()
        logging.warning('Users saved to database.')
    except Exception as e:
        logging.warning('failed to read user list. error: {}'.format(e))
    return results

def getGist(username):
    """
    It fetches list of gist with a specific username
    :param username:
    :return: list of gists
    """
    try:
        url = config.LIST_GISTS.format(username)
        gists = requests.get(url=url).json()
        logging.info("Gists fetched for this user: {}".format(username))
    except Exception as e:
        logging.warning('Failed to get gist through github-API')
        if e:
            logging.warning('Error message: {}'.format(e))
        gists = []
    return gists

def formatGist(user_id, gists):
    """
    It formate gists to a specific order
    :param user_id:
    :param gists:
    :return: formatted_gists
    """
    logging.info("Formatting gists...")
    formatted_gists = []
    print(len(gists))
    for i in range(len(gists)):
        created_at = datetime.datetime.strptime(gists[i]['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        created_at = pytz.timezone(config.period['timezone']).localize(created_at)

        updated_at = datetime.datetime.strptime(gists[i]['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
        updated_at = pytz.timezone(config.period['timezone']).localize(updated_at)
        gistDict = {
            "user_id": user_id,
            "gist_url": config.GIST_WITH_ID.format(gists[i]['id']),
            "created_at": created_at,
            "updated_at": updated_at
        }
        formatted_gists.append(gistDict)
    logging.info("Formatting complete")
    return formatted_gists

def writeGist(user_id, formatted_gists):
    """
    It saves gists to database
    :param user_id:
    :param formatted_gists:
    :return:
    """
    gist_count = 0
    try:
        for gist in formatted_gists:
            db.query("select * from {} where gist_url='{}'".format(db.GISTS_TABLE, gist['gist_url']))
            gist_exists = db.fetchOne()
            if not gist_exists:
                db.query_insert(db.GISTS_TABLE, list(gist.values()))
                gist_count += 1
        db.commit()
    except Exception as e:
        logging.warning('failed to write gist to db. error: {}'.format(e))

    db.query("select username from {} where id={}".format(db.USERS_TABLE, user_id))
    username = db.fetchOne()[0]
    if gist_count == 0 and formatted_gists.__len__() != 0:
        logging.info("Could not find new gists from this user: {}".format(username))
    elif gist_count > 0:
        logging.info("{} New gists found and saved into db for this user: {}".format(gist_count, username))
    else:
        logging.info("Could not find any gists against this user: {}".format(username))

def createActivity(user, formatted_gists):
    """
    It creates activity for each gist using pipedrive api
    :param user:
    :param formatted_gists:
    :return:
    """
    logging.info("Creating acitivity on Pipedrive...")
    activityIds = []
    try:
        for gist in formatted_gists:
            db.query("select * from {} where gist_url='{}'".format(db.ACTIVITY_TABLE, gist['gist_url']))
            activity_exist = db.fetchOne()
            if not activity_exist:
                due_date = datetime.datetime.now(pytz.utc).strftime('%Y-%m-%d')
                due_time = datetime.datetime.now(pytz.utc).strftime('%I:%M %p')

                url = config.pipedrive['url'].format(config.pipedrive['domain'],config.pipedrive['api-key'])
                data = {
                    "subject": "Gist created - User: {0} at {1}".format(user['username'], str(gist['updated_at'])),
                    "type": "Task",
                    "note":  "gist url: " + gist['gist_url'],
                    "due_date": due_date,
                    "due_time": due_time
                }
                resp = requests.post(url, json=data)
                response = resp.json()
                if response['data']['id']:
                    db.query("update {} set activity_id='{}' where gist_url='{}'".format(db.ACTIVITY_TABLE, response['data']['id'], gist['gist_url']))
                    activityIds.append(response['data']['id'])
                else:
                    logging.warning('Pipedrive-API: failed to add activity to pipedrive. Response: {}'.format(resp))
    except Exception as e:
        import traceback
        traceback.print_exc()
        logging.exception('Pipedrive-API: failed to add activity to pipedrive. Error: {}'.format(e))

    if activityIds.__len__() > 0:
        logging.info('Pipedrive-API: Created {} activities successfully for user : {}'.format(len(activityIds), user['username']))


def fetch_users_gists():
    """
    It is a main function which is calling all required methods inside it
    :return:
    """
    logging.info('------------------------------Start Fetching------------------------------')
    users = getUsers()
    for user in users:
        user_id = user['id']
        username = user['username']
        gists = getGist(username)
        formatted_gists = formatGist(user_id, gists)
        if len(gists)>0:
            writeGist(user_id, formatted_gists)
            createActivity(user, formatted_gists)
        else:
            logging.info('No new gist created by user {} was found.'.format(str(username)))
    logging.info('------------------------------Done!------------------------------')


def run_job(seconds):
    """
    scheduling job for a specific time interval

    :param seconds:
    :return:
    """
    scheduler = APScheduler()
    scheduler.add_job(func=fetch_users_gists, trigger="interval", seconds=seconds, id="Schedular",
                      next_run_time=datetime.datetime.now() + datetime.timedelta(minutes=5))
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())