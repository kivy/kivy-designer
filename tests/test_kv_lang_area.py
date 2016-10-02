import unittest

from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from nose.tools import assert_equal

from designer.components.kv_lang_area import KVLangArea
from designer.components.playground import Playground
from designer.core.project_manager import Project
from designer.uix.sandbox import DesignerSandbox


class KVLangAreaTest(unittest.TestCase):

    def setUp(self):
        self.play = Playground()
        self.play.sandbox = DesignerSandbox()
        self.project = Project()
        self.kv = KVLangArea(playground=self.play)

    def test_get_widget_path(self):
        p = self.kv.get_widget_path
        # level 0
        float_layout = FloatLayout()
        assert_equal(p(float_layout), [])

        # level 1
        btn1 = Button()
        float_layout.add_widget(btn1)
        assert_equal(p(float_layout), [])
        assert_equal(p(btn1), [0])

        btn2 = Button()
        float_layout.add_widget(btn2)
        assert_equal(p(float_layout), [])
        assert_equal(p(btn1), [0])
        assert_equal(p(btn2), [1])

        # level 2
        btn1_btn1 = Button()
        btn1.add_widget(btn1_btn1)
        assert_equal(p(btn1_btn1), [0, 0])

        btn2_btn1 = Button()
        btn2.add_widget(btn2_btn1)
        assert_equal(p(btn2_btn1), [0, 1])

        btn2_btn2 = Button()
        btn2.add_widget(btn2_btn2)
        assert_equal(p(btn2_btn2), [1, 1])

        btn2_btn3 = Button()
        btn2.add_widget(btn2_btn3)
        assert_equal(p(btn2_btn3), [2, 1])

        # level 3

        btn2_btn3_btn1 = Button()
        btn2_btn3.add_widget(btn2_btn3_btn1)
        assert_equal(p(btn2_btn3_btn1), [0, 2, 1])
