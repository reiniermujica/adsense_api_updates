#!/usr/bin/python


import argparse
import sys
from apiclient import sample_tools
from oauth2client import client

from adsense_util import get_account_id
from adsense_db import insert_report_row, init_db, update_time_mark

from datetime import datetime

import configparser

MAX_PAGE_SIZE = 10
ROW_LIMIT = 5000

METRICS = ['PAGE_VIEWS', 'AD_REQUESTS',
           'CLICKS', 'AD_REQUESTS_CTR', 'COST_PER_CLICK',
           'AD_REQUESTS_RPM', 'EARNINGS']

DIMENSION = ['AD_UNIT_CODE', 'AD_UNIT_NAME']


def get_month_start():
    now = datetime.today().replace(day=1)

    day = now.day
    month = now.month
    year = now.year

    return "{}-{:02d}-{:02d}".format(year, month, day)


def get_month_end():
    now = datetime.today()

    day = now.day
    month = now.month
    year = now.year

    return "{}-{:02d}-{:02d}".format(year, month, day)


def main(argv):
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'adsense', 'v1.4', __doc__, __file__, parents=[],
        scope='https://www.googleapis.com/auth/adsense.readonly')

    try:
        account_id = get_account_id(service)

        start_date = get_month_start()
        end_date = get_month_end()

        start_index = 0
        rows_to_obtain = MAX_PAGE_SIZE
        result_all_pages = None
        while True:
            result = service.reports().generate(
                accountId=account_id,
                startDate=start_date, endDate=end_date,
                filter=['AD_CLIENT_ID==ca-' + account_id],
                metric=METRICS,
                dimension=DIMENSION,
                useTimezoneReporting=True,
                startIndex=start_index,
                maxResults=rows_to_obtain).execute()

            if result_all_pages is None:
                result_all_pages = result
            else:
                result_all_pages['rows'].extend(result['rows'])

            if 'rows' in result:
                start_index += len(result['rows'])

            # Check to see if we're going to go above the limit and get as many
            # results as we can.
            if start_index + MAX_PAGE_SIZE > ROW_LIMIT:
                rows_to_obtain = ROW_LIMIT - start_index
                if rows_to_obtain <= 0:
                    break

            if start_index >= int(result['totalMatchedRows']):
                break

        store_report_in_db(result_all_pages, start_date)

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the '
              'application to re-authorize')


def store_report_in_db(result, date):
    if 'headers' not in result:
        return False

    if 'rows' not in result:
        return False

    db = init_db()

    headers = []
    for header in result['headers']:
        headers.append(header['name'])

    for row in result['rows']:
        report_row = {}

        it = 0
        for metric in headers:
            report_row[metric.lower()] = row[it]
            it = it + 1

        insert_report_row(db, report_row, date)

    update_time_mark(db)


if __name__ == '__main__':
    main(sys.argv)
