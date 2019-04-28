import configparser
import pymysql

ADMIN_USER_ID = 1


def get_db_config():
    config = configparser.ConfigParser()
    config.read('.env')

    db = {}
    section = 'database'

    options = config.options(section)
    for option in options:
        db[option] = config.get(section, option)

    return db


def init_db():
    config = get_db_config()
    db = pymysql.connect(config['address'], config['user'],
                         config['password'], config['db'])
    return db


def insert_report_row(db, earnings, date):
    user_id = get_user_id(db, earnings['ad_unit_code'])
    if (user_id == None):
        user_id = ADMIN_USER_ID

    del earnings['ad_unit_name']
    earnings['user_id'] = user_id
    earnings['year'] = date.split('-')[0]
    earnings['month'] = date.split('-')[1]

    update_user_earnings(db, earnings)

    return True


def get_user_id(db, ad_unit_code):
    with db:
        cur = db.cursor()

        cur.execute(
            "SELECT user_id FROM adsense_units_user WHERE ad_id=%s", ad_unit_code)

        result = cur.fetchone()
        if result is not None:
            return result[0]

    return None


def update_user_earnings(db, earnings):
    if find_record(db, earnings):
        update_record(db, earnings)
    else:
        insert_record(db, earnings)

    return True


def find_record(db, where):
    with db:
        cur = db.cursor()

        cur.execute(
            "SELECT * FROM adsense_users_earning WHERE user_id=%s and year=%s and month=%s and ad_unit_code=%s",
            (where['user_id'], where['year'], where['month'], where['ad_unit_code']))

        result = cur.fetchone()
        if result is not None:
            return True

    return False


def update_record(db, record):
    with db:
        cur = db.cursor()

        sql = """UPDATE adsense_users_earning SET earnings = %s, page_views = %s, clicks = %s, ad_requests = %s, ad_requests_ctr = %s, cost_per_click = %s, ad_requests_rpm = %s
                  WHERE user_id=%s and month = %s and year = %s and ad_unit_code=%s"""
        values = (record['earnings'], record['page_views'], record['clicks'], record['ad_requests'],
                  record['ad_requests_ctr'], record['cost_per_click'], record['ad_requests_rpm'],
                  record['user_id'], record['month'], record['year'], record['ad_unit_code'])

        cur.execute(sql, values)

        db.commit()

    return True


def insert_record(db, record):
    with db:
        cur = db.cursor()

        sql = """INSERT INTO adsense_users_earning (user_id, month, year, earnings, ad_unit_code, page_views, clicks, ad_requests, ad_requests_ctr, cost_per_click, ad_requests_rpm)
                  VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (record['user_id'], record['month'], record['year'], record['earnings'], record['ad_unit_code'], record['page_views'],
                  record['clicks'], record['ad_requests'], record['ad_requests_ctr'], record['cost_per_click'], record['ad_requests_rpm'])

        cur.execute(sql, values)

        db.commit()

    return True
