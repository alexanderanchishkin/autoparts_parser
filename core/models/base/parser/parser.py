import requests

from core.utilities import stopwatch


class Parser:
    def __init__(self, parser_id=0, table_prefix=None):
        self.table_prefix = table_prefix
        self.table_name = table_prefix + self.OUTPUT_FILE.split('.')[0]
        self.id = parser_id
        self.current_proxies = None
        self.proxy_index = 0

        self.session = requests.Session()
        self.amount = 0
        self.done = 0

    def prepare_proxy(self, proxy):
        return {
              "http": f'http://{proxy}',
              "https": f'https://{proxy}',
        }

    def get_next_proxies(self):
        proxy = self.prepare_proxy(self.proxies[self.proxy_index])
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    @stopwatch.time('Parser')
    def execute(self, parts):
        if not parts:
            return False

        self.amount = len(parts)
        self.done = 0

        ready_parts = self.find_parts(parts)
        return ready_parts

    def find_parts(self, parts):
        raise NotImplementedError()
