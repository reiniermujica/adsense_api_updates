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

"""Gets all the saved ad styles for the user's default account.

Tags: savedadstyles.list
"""

__author__ = 'jalc@google.com (Jose Alcerreca)'

import sys

from apiclient import sample_tools
from oauth2client import client
from adsense_util import get_account_id

MAX_PAGE_SIZE = 50


def main(argv):
  # Authenticate and construct service.
  service, unused_flags = sample_tools.init(
      argv, 'adsense', 'v1.4', __doc__, __file__, parents=[],
      scope='https://www.googleapis.com/auth/adsense.readonly')

  try:
    # Let the user pick account if more than one.
    account_id = get_account_id(service)

    # Retrieve ad client list in pages and display data as we receive it.
    request = service.accounts().savedadstyles().list(accountId=account_id,
                                                      maxResults=MAX_PAGE_SIZE)

    while request is not None:
      result = request.execute()
      if 'items' in result:
        saved_ad_styles = result['items']
        for saved_ad_style in saved_ad_styles:
          print ('Saved ad style with ID "%s" and background color "#%s" was '
                 'found.'
                 % (saved_ad_style['id'],
                    saved_ad_style['adStyle']['colors']['background']))
          if ('corners' in saved_ad_style['adStyle']
                  and 'font' in saved_ad_style['adStyle']):
            print ('It has "%s" corners and a "%s" size font.' %
                   (saved_ad_style['adStyle']['corners'],
                    saved_ad_style['adStyle']['font']['size']))

      request = service.savedadstyles().list_next(request, result)

  except client.AccessTokenRefreshError:
    print ('The credentials have been revoked or expired, please re-run the '
           'application to re-authorize')

if __name__ == '__main__':
  main(sys.argv)
