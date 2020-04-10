def load():
    try:
        with open('proxies.txt', 'r') as f:
            return f.read().splitlines()
    except FileNotFoundError:
        print('Проверьте лист прокси!')
        return []
