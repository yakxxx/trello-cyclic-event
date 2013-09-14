#!/bin/python
"""Handle Trello cyclic events.

Usage:
  cycle.py --key=<key> --token=<token> --board=<board> --cfglist=<cfglist> --dstlist=<dstlist>
  cycle.py (-h | --help)
  cycle.py --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --key=<key>            Developer key.
  --token=<token>        User token.
  --board=<board>        Board name.
  --cfglist=<cfg_list>   Config list.
  --dstlist=<dst_list>   Destination list

"""
import datetime
import logging
import re
import sys

from croniter import croniter

from docopt import docopt
from trello import TrelloClient

logging.basicConfig(level=logging.DEBUG)
LOG = logging.getLogger('cycle')

LAST_RUN_PATH = '/run/lock/trello_cycle_last_run'
__version = "0.1b"


def get_board(trello_client):
    boards = trello_client.list_boards()
    resp = filter(lambda b: b.name == board_name, boards)

    if len(resp) == 0:
        LOG.error('Wrong board name!')
        sys.exit(1)

    board = resp[0]
    return board


def get_config_cards(board, cfglist_name):
    config_list = _get_list_by_name(board.all_lists(), cfglist_name)
    if not config_list:
        LOG.error('Wrong config list name')
        sys.exit(1)

    return config_list.list_cards()


def _get_list_by_name(lists, name):
    lists = board.all_lists()
    resp = filter(lambda l: l.name == name, lists)
    if len(resp) == 0:
        return None
    else:
        return resp[0]


def extract_cronlines(cards):
    metas = []
    for c in cards:
        metas.append(_match_cronline(c.name) or _match_cronline(c.description))
    return metas


def _match_cronline(txt):
    m = re.search(r"\[cyclic\s* {\s*(.+)\s*}\s*\]", txt)
    if m is None:
        return None

    try:
        return m.group(1)
    except IndexError:
        return None


def handle_cards(cronlines_with_cards, last_run, handling_time, dstlist):
    with_cronline = filter(lambda c: c[0] is not None, cronlines_with_cards)
    LOG.info("Handling cards with cronline: {0}".format(repr(with_cronline)))

    for cronline, card in with_cronline:
        cr = croniter(cronline, handling_time)
        if cr.get_prev(datetime.datetime) > last_run:
            copy_card_to_dstlist(card, dstlist)


def copy_card_to_dstlist(card, dstlist):
    LOG.info('Copying card {0} to list {1}'.format(repr(card), repr(dstlist)))
    dstlist.add_card(card.name, card.description)


def get_last_run():
    try:
        with open(LAST_RUN_PATH, 'r') as f:
            last_run = datetime.datetime.fromtimestamp(float(f.read()))
    except (IOError, ValueError):
        return datetime.datetime.fromtimestamp(0.0)  # last run loooong ago

    return last_run


def set_last_run(last_run):
    secs = (last_run - datetime.datetime.fromtimestamp(0)).total_seconds()
    with open(LAST_RUN_PATH, 'w') as f:
        f.write(str(secs))

if __name__ == '__main__':
    arguments = docopt(__doc__, version=__version)
    token = arguments.get('--token')
    key = arguments.get('--key')
    board_name = arguments.get('--board')
    cfglist_name = arguments.get('--cfglist')
    dstlist_name = arguments.get('--dstlist')

    run_time = datetime.datetime.now()
    last_run = get_last_run()

    trello_client = TrelloClient(key, token)

    board = get_board(trello_client)
    cards = get_config_cards(board, cfglist_name)
    cronlines = extract_cronlines(cards)

    handle_cards(
        zip(cronlines, cards),
        last_run=last_run,
        handling_time=run_time,
        dstlist=_get_list_by_name(board.all_lists(), dstlist_name)
    )

    set_last_run(run_time)