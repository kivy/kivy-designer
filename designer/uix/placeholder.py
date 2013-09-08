from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen
from kivy.uix.actionbar import ActionItem

class Placeholder(Widget):
    pass

class ScreenPlaceholder(Screen, Placeholder):
    pass

class ActionItemPlaceholder(ActionItem, Placeholder):
    pass