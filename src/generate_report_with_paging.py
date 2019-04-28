#!/usr/bin/python

"""This example retrieves a report for the specified ad client.

Please only use pagination if your application requires it due to memory or
storage constraints.
If you need to retrieve more than 5000 rows, please check generate_report.py,
as due to current limitations you will not be able to use paging for large
reports. To get ad clients, run get_all_ad_clients.py.

Tags: reports.generate
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import argparse
import sys
from apiclient import sample_tools
from oauth2client import client
# from adsense_util import fill_date_gaps
from adsense_util import get_account_id

MAX_PAGE_SIZE = 10
# This is the maximum number of obtainable rows for paged reports.
ROW_LIMIT = 5000

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument(
    'ad_client_id',
    help='The ID of the ad client for which to generate a report')


def main(argv):
    # Authenticate and construct service.
    service, flags = sample_tools.init(
        argv, 'adsense', 'v1.4', __doc__, __file__, parents=[argparser],
        scope='https://www.googleapis.com/auth/adsense.readonly')

    ad_client_id = flags.ad_client_id

    try:
        # Let the user pick account if more than one.
        account_id = get_account_id(service)

        # Retrieve report in pages and display data as we receive it.
        start_index = 0
        rows_to_obtain = MAX_PAGE_SIZE
        result_all_pages = None
        while True:
            result = service.reports().generate(
                accountId='pub-3136901199458158',
                startDate='today-1w', endDate='today',
                filter=['AD_CLIENT_ID==ca-pub-3136901199458158'],
                metric=['PAGE_VIEWS', 'AD_REQUESTS', 'AD_REQUESTS_COVERAGE',
                        'CLICKS', 'AD_REQUESTS_CTR', 'COST_PER_CLICK',
                        'AD_REQUESTS_RPM', 'EARNINGS'],
                dimension=['DATE'],
                sort=['+DATE'],
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

    # Display results for this page.
    if 'rows' in result:
        for row in result['rows']:
            for column in row:
                print('%25s' % column)
            print


if __name__ == '__main__':
    main(sys.argv)
