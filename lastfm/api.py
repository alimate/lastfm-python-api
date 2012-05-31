# -*- coding: utf-8 -*- 
import hashlib
import urllib
import urllib2
import simplejson as json
import webbrowser
from os import environ

API_KEY = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
ROOT_URL = 'http://ws.audioscrobbler.com/2.0/'
SECRET = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

def create_session():
    """Get username and session key.

    Request a token from lastfm api.
    Open browser, so user could authorize your app.
    Create lastfm session.
    Save user name and session key to `~/.lastfmsession`.

    If session key and user name are already in `~/.lastfmsession`,
    return them without sending any requests.
    """
    try:
        with open(environ['HOME'] + '/.lastfmsession', 'r') as session_file:

            # session is already opened
            username = session_file.readline()[:-1]
            key_str = session_file.readline()[:-1]
            if username and key_str:
                return username, key_str
    except IOError: # file doesn't exist
        pass

    with open(environ['HOME'] + '/.lastfmsession', 'w') as session_file:

        # session is not opened -> open
        token_url = _make_request_url(method='auth.gettoken', api_key=API_KEY)
        token_response = urllib.urlopen(token_url)
        token = json.loads(token_response.read())['token']

        webbrowser.open('http://www.last.fm/api/auth/?api_key={}&token={}'
                        .format(API_KEY, token))
        print('Authorize request in your browser, then press Enter')
        raw_input()

        session_req_url = _make_signed_request_url(
                                                method='auth.getsession',
                                                token=token,
                                                api_key=API_KEY)
        
        session_response = urllib2.urlopen(session_req_url)

        response_dict = json.loads(session_response.read())

        key = response_dict['session']['key']
        name = response_dict['session']['name']
        session_file.write(name + '\n')
        session_file.write(key + '\n')
        return name, key

def get_top_artists_for_user(username):
    """Call *user.getTopArtists* method.

    Description: http://www.last.fm/api/show/user.getTopArtists
    """
    return _call_lastfm_api('user.getTopArtists', user=username)

def get_artist_info(artist_name):
    """Call *artist.getInfo* method.
    
    Description: http://www.last.fm/api/show/artist.getInfo
    """
    return _call_lastfm_api(
            'artist.getInfo',
            # non-ascii chars not supported..
            artist=artist_name.encode('utf-8'))

def _call_lastfm_api(method_name, **method_args):
    """Call lastfm method with given parameters, return result JSON"""
    method_args['api_key'] = API_KEY
    method_args['method'] = method_name
    url = _make_request_url(**method_args)
    response_str = urllib2.urlopen(url).read()
    return json.loads(response_str)


def _make_request_url(**kwargs):
    """Create URL for regular GET request"""
    url = ROOT_URL + '?'
    kwargs['format'] = 'json'
    url += urllib.urlencode(kwargs)
    return url

    
def _make_signed_request_url(**kwargs):
    """Create URL for signed GET request
    
    More on this: http://www.last.fm/api/authspec
    (see `8. Signing Calls`)

    """
    md5 = hashlib.md5()
    for key in sorted(kwargs):
        md5.update('{}{}'.format(key, kwargs[key]))
    md5.update(SECRET)
    kwargs['api_sig'] = md5.hexdigest()
    return _make_request_url(**kwargs)
    

if __name__ == '__main__':
    # username, session_key = create_session()
    # top_artists_dict = get_top_artists_for_user(username)
    # print(top_artists_dict['topartists']['artist'][0])
    print(get_artist_info(u'Emilíana Torrini'))
