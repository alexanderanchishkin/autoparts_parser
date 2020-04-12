from config import settings


def load():
    try:
        with open(settings.PROXY_FILE, 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        print('Проверьте лист прокси!')
        return []


def prepare_proxy(proxy):
    return {
          "http": f'http://{proxy}',
          "https": f'https://{proxy}',
    }
