import sys

from runs import schedule
from runs import test
from runs import web


def main():
    if len(sys.argv) < 2:
        print('Incorrect parameter')
        return

    run = sys.argv[1]
    if run == 'schedule':
        schedule.main()
    elif run == 'test':
        test.main()
    elif run == 'web':
        web.main()
    else:
        print('Run not found')


if __name__ == '__main__':
    main()
