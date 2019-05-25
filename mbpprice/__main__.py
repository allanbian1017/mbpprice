"""
Utility
"""

import sys
from mbpprice.search import MBPSearch


def search_and_list(channel):
    """
    Search and list results
    """
    search = MBPSearch(channel)
    results = search.list(limit=10)

    for (i, item) in enumerate(results):
        print('{:03d}: {}'.format(i, item['url']))
        print('價格: {}'.format(item['price']))
        print(
            '年份: {} / 螢幕尺寸: {} / 電池循環: {}'.format(item['year'], item['screen'], item['bat_count']))
        print(
            'CPU: {} / RAM: {} / 硬碟容量: {}'.format(item['cpu'], item['ram'], item['hdd']))
        print()


def usage():
    """
    Usage description
    """
    print('Usage: python3 -m mbpprice [action]')
    print()
    print('action list:')
    print('  search [channel]   Search macbook pro price from channel')
    print()
    print('channel list:')
    print('  ptt                PTT')
    print()
    print('default:')
    print('  [channel]          ptt')


def get_cmd_args(index, default=None):
    """
    Get command argument
    """
    if len(sys.argv) > index:
        return sys.argv[index]
    return default


def main():
    """
    main()
    """
    action = get_cmd_args(1)
    if action == 'search':
        channel = get_cmd_args(2, 'ptt')
        search_and_list(channel)
    else:
        if action != 'help':
            print('wrong action type')
            print()
        usage()


if __name__ == '__main__':
    main()
