#!/usr/bin/python

import sys

from apiclient import sample_tools
from oauth2client import client

MAX_PAGE_SIZE = 50


def main(argv):
    # Authenticate and construct service.
    service, unused_flags = sample_tools.init(
        argv, 'adsense', 'v1.4', __doc__, __file__, parents=[],
        scope='https://www.googleapis.com/auth/adsense.readonly')

    try:
        # Retrieve account list in pages and display data as we receive it.
        request = service.accounts().list(maxResults=MAX_PAGE_SIZE)

        while request is not None:
            result = request.execute()
            accounts = result['items']
            for account in accounts:
                print('Account with ID "%s" and name "%s" was found. '
                      % (account['id'], account['name']))

            request = service.accounts().list_next(request, result)

    except client.AccessTokenRefreshError:
        print('The credentials have been revoked or expired, please re-run the '
              'application to re-authorize')


if __name__ == '__main__':
    main(sys.argv)
