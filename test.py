import datetime
import unittest
import cycle
from mock import MagicMock


class TestCycle(unittest.TestCase):
    def setUp(self):
        cards_def = [
            {
                'name': 'XXX [cyclic {35 22 * * *}] asd',
                'description': 'XXX desc'
            },
            {
                'name': 'YYY [cyclic {35 23 * * *}] asd',
                'description': 'yyy desc'
            },
            {
                'name': 'ABC asd',
                'description': 'abc desc'
            }
        ]

        self.cards = []
        for cd in cards_def:
            m = MagicMock()
            m.name = cd['name']
            m.description = cd['description']
            self.cards.append(m)

    def test_match_cronline(self):
        m = cycle._match_cronline("[cyclic {* * * * *}]")
        self.assertEqual(m, '* * * * *')

    def test_not_match(self):
        m = cycle._match_cronline("dupa zbita")
        self.assertEqual(m, None)

    def test_extract_cronlines(self):
        cronlines = cycle.extract_cronlines(self.cards)
        self.assertListEqual(cronlines, ["35 22 * * *", "35 23 * * *", None])

    def test_handle_cards(self):
        cc_mock = MagicMock()
        tmp_cc = cycle.__dict__['copy_card_to_dstlist']
        cycle.__dict__['copy_card_to_dstlist'] = cc_mock
        mock_list = MagicMock()
        try:
            cronlines = cycle.extract_cronlines(self.cards)
            cycle.handle_cards(
                zip(cronlines, self.cards),
                last_run=datetime.datetime(2013, 10, 11, 23, 0),
                handling_time=datetime.datetime(2013, 10, 12, 0, 0),
                dstlist=mock_list
            )
            cc_mock.assert_called_once_with(self.cards[1], mock_list)
        finally:
            cycle.__dict__['copy_card_to_dstlist'] = tmp_cc
