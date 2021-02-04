import urllib3


def init_warnings():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
