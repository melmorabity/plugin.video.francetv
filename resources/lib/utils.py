# coding: utf-8
#
# Copyright © 2020 melmorabity
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from __future__ import unicode_literals

import json

try:
    from urllib.parse import parse_qsl
    from urllib.parse import urlencode
    from urllib.parse import urlparse
    from urllib.parse import urlunparse
except ImportError:
    from urlparse import parse_qsl
    from urllib import urlencode
    from urlparse import urlparse
    from urlparse import urlunparse

try:
    from typing import Optional
    from typing import Text
    from typing import Union
except ImportError:
    pass

from bs4 import BeautifulSoup
import xbmc


# Only capitalize the first letter
def capitalize(label):
    # type: (Optional[Text]) -> Optional[Text]

    if not label:
        return label

    return label[0].upper() + label[1:]


def html_to_text(html):
    # type: (Optional[Text]) -> Optional[Text]

    if not html:
        return html

    return BeautifulSoup(html, features="html.parser").get_text()


def update_url_params(url, **params):
    # type: (Text, Union[None, int, Text]) -> Text

    clean_params = {k: v for k, v in list(params.items()) if v is not None}

    parsed_url = list(urlparse(url))
    parsed_url_params = dict(parse_qsl(parsed_url[4]))
    parsed_url_params.update(clean_params)
    parsed_url[4] = urlencode(clean_params)

    return urlunparse(parsed_url)


def jsonrpc(method, **params):
    data = {
        'jsonrpc': '2.0',
        'id': 1,
        'method': method,
        'params': params,
        }
    data = json.dumps(data)
    request = xbmc.executeJSONRPC(data)
    return json.loads(request)


def get_setting(key):
    result = jsonrpc('Settings.GetSettingValue', setting=key)
    return result.get('result', {}).get('value')


def get_proxies():
    proxy_active = get_setting('network.usehttpproxy')
    proxy_type = get_setting('network.httpproxytype')
    if not proxy_active:
        return

    proxy_types = ['http', 'socks4', 'socks4a', 'socks5', 'socks5h']

    proxy = {
        'scheme': proxy_types[proxy_type],
        'server': get_setting('network.httpproxyserver'),
        'port': get_setting('network.httpproxyport'),
        'username': get_setting('network.httpproxyusername'),
        'password': get_setting('network.httpproxypassword'),
        }
    if (proxy['username'] and proxy['password']
            and proxy['server'] and proxy['port']):
        proxy_address = (
            '{scheme}://{username}:{password}@{server}:{port}'.format(**proxy))
    elif proxy['username'] and proxy['server'] and proxy['port']:
        proxy_address = '{scheme}://{username}@{server}:{port}'.format(**proxy)
    elif proxy['server'] and proxy['port']:
        proxy_address = '{scheme}://{server}:{port}'.format(**proxy)
    elif proxy['server']:
        proxy_address = '{scheme}://{server}'.format(**proxy)
    else:
        return
    return {'http': proxy_address, 'https': proxy_address}
