import unittest

from nose.tools import assert_equal

from designer.components.playground import Playground


class PlaygroundTest(unittest.TestCase):

    def setUp(self):
        self.play = Playground()

    def test_generate_kv_from_args(self):
        g = self.play.generate_kv_from_args
        tests = [
            ['Test', {'text': 'Test'}, 'Test:\n    text: \'Test\''],
            ['Test', {'size': [1, 1]}, 'Test:\n    size: [1, 1]'],
            ['Test', {'size': [0.1, 0]}, 'Test:\n    size: [0.1, 0]'],
            ['Test', {}, 'Test:'],
            ['Test', {'pos_hint': {'center_x': 0}},
             'Test:\n    pos_hint: {\'center_x\': 0}'],
            ['Test', {'active': True}, 'Test:\n    active: True'],
        ]
        for t in tests:
            assert_equal(g(t[0], t[1]), t[2])
