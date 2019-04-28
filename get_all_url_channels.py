#!/usr/bin/python
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This example gets all URL channels in an ad client.

To get ad clients, run get_all_ad_clients.py.

Tags: urlchannels.list
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import argparse
import sys

from apiclient import sample_tools
from oauth2client import client
from adsense_util import get_account_id

MAX_PAGE_SIZE = 50

# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)
argparser.add_argument('ad_client_id',
                       help='The ad client ID for which to get URL channels')


def main(argv):
  # Authenticate and construct service.
  service, flags = sample_tools.init(
      argv, 'adsense', 'v1.4', __doc__, __file__, parents=[argparser],
      scope='https://www.googleapis.com/auth/adsense.readonly')

  ad_client_id = flags.ad_client_id

  try:
    # Let the user pick account if more than one.
    account_id = get_account_id(service)

    # Retrieve URL channel list in pages and display data as we receive it.
    request = service.accounts().urlchannels().list(accountId=account_id,
                                                    adClientId=ad_client_id,
                                                    maxResults=MAX_PAGE_SIZE)

    while request is not None:
      result = request.execute()
      if 'items' in result:
        url_channels = result['items']
        for url_channel in url_channels:
          print ('URL channel with URL pattern "%s" was found.'
                 % url_channel['urlPattern'])

      request = service.customchannels().list_next(request, result)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
