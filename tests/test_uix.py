'''
This file is responsible for testing custom UIX from designer/uix/*
'''

import unittest

from nose.tools import assert_equal
from nose.tools import assert_not_equal

from designer.components.kivy_console import KivyConsole
from designer.uix.action_items import ActionCheckButton
from designer.uix.settings import SettingListCheckItem


class UIXTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_ActionCheckButton(self):
        btn = ActionCheckButton(
            text='TestCase',
            desc='Testing',
            checkbox_active=False,
            allow_no_selection=False,
            group='Test')

        assert_equal(btn.text, 'TestCase')
        assert_equal(btn.desc, 'Testing')
        assert_equal(btn.checkbox_active, False)
        assert_equal(btn.allow_no_selection, False)
        assert_equal(btn.group, 'Test')

    def test_SettingSettingListCheckItem(self):
        check1 = SettingListCheckItem(
            item_text='TestCase 1',
            active=True,
            group='Test')
        check2 = SettingListCheckItem(
            item_text='TestCase 2',
            active=False,
            group='Test')

        assert_equal(check1.item_text, 'TestCase 1')
        assert_equal(check1.active, True)
        assert_equal(check2.active, False)
        assert_equal(check1.group, 'Test')

        assert_not_equal(check1.active, check2.active)
        check2.item_check._toggle_active()
        assert_not_equal(check1.active, check2.active)

    def test_KivyConsole(self):
        kc = KivyConsole()
        h = kc.txtinput_history_box
        i = kc.txtinput_command_line

        # check the kc initialization
        assert_equal(h.text, '')
        assert_equal(i.text, '')
        assert_equal(kc.command_status, 'closed')
        assert_not_equal(kc.prompt(), '')

        # running commands
        kc.run_command('echo 1')
        kc.run_command(['echo 1', 'echo 2', 'echo 3'])
