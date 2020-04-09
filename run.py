import sys

from runs import cron
from runs import test
from runs import waitress_server


def main():
    if len(sys.argv) < 2:
        print('Incorrect parameter')
        return

    run = sys.argv[1]
    if run == 'cron':
        cron.main()
    elif run == 'test':
        test.main()
    elif run == 'web':
        waitress_server.main()
    else:
        print('Run not found')


if __name__ == '__main__':
    main()
