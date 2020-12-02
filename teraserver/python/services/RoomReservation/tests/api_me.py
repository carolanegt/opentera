from requests import get


class Config:
    hostname = 'localhost'
    port = 40075
    servicename = '/room'

    # User endpoints
    user_login_endpoint = '/api/user/login'


def _make_url(hostname, port, endpoint):
    return 'https://' + hostname + ':' + str(port) + endpoint


def login_user(config: Config):
    url = _make_url(config.hostname, config.port, config.user_login_endpoint)
    response = get(url=url, verify=False, auth=('admin', 'admin'))
    if response.status_code == 200:
        return response.json()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


def who_am_i(config: Config, token: str):
    url = _make_url(config.hostname, config.port, config.servicename + '/api/me?token=' + token)
    response = get(url=url, verify=False, auth=('admin', 'admin'))
    if response.status_code == 200:
        return response.json()
    import inspect
    print('Error in ' + inspect.currentframe().f_code.co_name + ': Code=' + str(response.status_code) + ', Message=' +
          response.content.decode())
    return {}


if __name__ == '__main__':
    base_config = Config()

    # Ignore insecure requests warning
    import urllib3

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # Connect as a user
    user_login = login_user(base_config)
    user_token = user_login['user_token']

    # Get reply from "me" api with user token
    identity = who_am_i(base_config, user_token)
    print(identity)
