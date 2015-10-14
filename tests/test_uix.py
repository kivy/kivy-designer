'''
This file is responsible for testing custom UIX from designer/uix/*
'''

import unittest
from nose.tools import assert_equal
from nose.tools import assert_not_equal
from designer.uix.actioncheckbutton import ActionCheckButton
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
