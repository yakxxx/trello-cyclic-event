#!/bin/python
"""Naval Fate.

Usage:
  cycle.py --key=<key> --secret=<secret> --token=<token> --board=<board> --cfglist=<cfglist> --dstlist=<dstlist>
  cycle.py (-h | --help)
  cycle.py --version

Options:
  -h --help              Show this screen.
  --version              Show version.
  --key=<key>            Developer key.
  --secret=<secret>      Developer Secret.
  --token=<token>        User token.
  --board=<board>        Board name.
  --cfglist=<cfg_list>   Config list.
  --dstlist=<dst_list>   Destination list

"""
import logging
import re
import sys

from croniter import croniter

from docopt import docopt
from trello import TrelloClient


def get_board(key, token):
    trello = TrelloClient(key, token)
    boards = trello.list_boards()
    resp = filter(lambda b: b.name == board_name, boards)

    if len(resp) == 0:
        logging.error('Wrong board name!')
        sys.exit(1)

    board = resp[0]
    return board


def get_config_cards(board, cfglist):
    lists = board.all_lists()
    resp = filter(lambda l: l.name == cfglist, lists)
    if len(resp) == 0:
        logging.error('Wrong config list name')
        sys.exit(1)

    config_list = resp[0]

    return config_list.list_cards()


def extract_meta(cards):
    print cards[0].__dict__

def _match_meta(txt):


if __name__ == '__main__':
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    token = arguments.get('--token')
    key = arguments.get('--key')
    board_name = arguments.get('--board')
    cfglist = arguments.get('--cfglist')

    board = get_board(key, token)
    cards = get_config_cards(board, cfglist)
    extract_meta(cards)


