import waitress

from web import flask


def main():
    waitress.serve(flask.app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
