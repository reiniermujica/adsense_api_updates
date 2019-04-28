#!/usr/bin/python


import argparse
import sys
from apiclient import sample_tools
from oauth2client import client

from adsense_util import get_account_id

from datetime import datetime

MAX_PAGE_SIZE = 10
# This is the maximum number of obtainable rows for paged reports.
ROW_LIMIT = 5000


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
                metric=['PAGE_VIEWS', 'AD_REQUESTS',
                        'CLICKS', 'AD_REQUESTS_CTR', 'COST_PER_CLICK',
                        'AD_REQUESTS_RPM', 'EARNINGS'],
                dimension=['AD_UNIT_CODE', 'AD_UNIT_NAME'],
                useTimezoneReporting=True,
                startIndex=start_index,
                maxResults=rows_to_obtain).execute()

            if result_all_pages is None:
                result_all_pages = result
            else:
                result_all_pages['rows'].extend(result['rows'])

            start_index += len(result['rows'])

            # Check to see if we're going to go above the limit and get as many
            # results as we can.
            if start_index + MAX_PAGE_SIZE > ROW_LIMIT:
                rows_to_obtain = ROW_LIMIT - start_index
                if rows_to_obtain <= 0:
                    break

            if start_index >= int(result['totalMatchedRows']):
                break

        print_result(result_all_pages)

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the '
              'application to re-authorize')


def print_result(result):
    for header in result['headers']:
        print('%25s' % header['name'])
    print

    if 'rows' in result:
        for row in result['rows']:
            for column in row:
                print('%25s' % column)
            print


if __name__ == '__main__':
    main(sys.argv)
