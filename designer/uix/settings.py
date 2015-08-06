from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import ObjectProperty, ListProperty, BooleanProperty, \
    StringProperty, DictProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.settings import SettingItem, SettingSpacer
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget

Builder.load_string('''
<SettingDict>:
    Label:
        text: root.options[root.value] if root.value and root.value \
            in root.options else ''
        pos: root.pos
        font_size: '15sp'

<SettingList>:
    Label:
        text: root.value if root.value else 'Click to select'
        pos: root.pos
        font_size: '15sp'
        shorten: True
        shorten_from: 'right'
        text_size: self.size
        halign: 'center'
        valign: 'middle'


<SettingListCheckItem>:
    item_check: item_check
    orientation: 'horizontal'
    size_hint_y: None
    height: 50
    canvas.before:
        Color:
            rgba: 1, 1, 1, 0.2
        Rectangle:
            pos: self.x, self.top - 1
            size: self.width, 1
    CheckBox:
        id: item_check
        size_hint_x: 0.1
        active: root.active
        on_active: root.on_active(self)
        group: root.group
    Button:
        text: root.item_text
        background_normal: 'atlas://data/images/defaulttheme/action_item'
        background_down: 'atlas://data/images/defaulttheme/action_item'
        size_hint_x: 0.9
        text_size: self.size
        shorten: True
        valign: 'middle'
        on_press: root.item_check._toggle_active()

<SettingListContent>:
    item_list: item_list
    custom_item_layout: custom_item_layout
    txt_custom_item: txt_custom_item
    orientation: 'vertical'
    spacing: '10dp'
    Label:
        text: root.setting.desc
        text_size: self.size
        font_size: '11pt'
        halign: 'center'
        valign: 'middle'
        size_hint_y: None
        height: '30pt'
    ScrollView:
        id: i_scroll
        GridLayout:
            id: item_list
            cols: 1
            size_hint_y: None
            height: max(i_scroll.height, self.minimum_height)
    BoxLayout:
        id: custom_item_layout
        orientation: 'vertical'
        size_hint_y: None
        height: dp(30) + pt(15)
        Label:
            text: 'Custom item:'
            size_hint_y: None
            height: '15pt'
            text_size: self.size
            font_size: '11pt'
            valign: 'middle'
        BoxLayout:
            size_hint_y: None
            height: '30dp'
            orientation: 'horizontal'
            TextInput:
                id: txt_custom_item
                size_hint_x: 0.7
                multiline: False
                on_text_validate: root.add_custom_item()
            Button:
                text: 'Add'
                size_hint_x: 0.3
                on_press: root.add_custom_item()
    BoxLayout:
        size_hint_y: None
        height: '40dp'
        Button:
            text: 'Apply'
            on_press: root.on_apply_pressed()
        Button:
            text: 'Cancel'
            on_press: root.dispatch('on_cancel')
''')


class SettingDict(SettingItem):
    '''Implementation of an option list on top of a :class:`SettingItem`.
    Based on SettingOptions, but implemented to use DictProperty.
    It is visualized with a :class:`~kivy.uix.label.Label` widget that, when
    clicked, will open a :class:`~kivy.uix.popup.Popup` with a
    list of options from which the user can select.
    '''

    options = DictProperty({})
    '''Dict with keys to be saved and visible values to the user

    :attr:`options` is a :class:`~kivy.properties.DictProperty` and defaults
    to {}.
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it is shown.

    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _set_option(self, instance):
        self.value = instance.key
        self.popup.dismiss()

    def _create_popup(self, instance):
        # create the popup
        content = BoxLayout(orientation='vertical', spacing='5dp')
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, '400dp'))
        popup.height = len(self.options) * dp(55) + dp(150)

        # add all the options
        content.add_widget(Widget(size_hint_y=None, height=1))
        uid = str(self.uid)
        for key in self.options:
            state = 'down' if key == self.value else 'normal'
            btn = ToggleButton(text=self.options[key], state=state, group=uid)
            btn.key = key
            btn.bind(on_release=self._set_option)
            content.add_widget(btn)

        # finally, add a cancel button to return on the previous panel
        content.add_widget(SettingSpacer())
        btn = Button(text='Cancel', size_hint_y=None, height=dp(50))
        btn.bind(on_release=popup.dismiss)
        content.add_widget(btn)

        # and open the popup !
        popup.open()


class SettingListCheckItem(BoxLayout):
    '''Widget with a check button and a label to display each item of list
    '''
    item_text = StringProperty('')
    '''Item text. :attr:`item_text` is a
    :class:`~kivy.properties.ObjectProperty` and defaults to ''
    '''

    active = BooleanProperty(False)
    '''Alias to the checkbox active state.
    :attr:`checked` is a :class:`~kivy.properties.BooleanProperty` and
    defaults to False
    '''

    group = StringProperty(None)
    '''CheckBox group name. If the CheckBox is in a Group,
    it becomes a Radio button.
    :attr:`group` is a :class:`~kivy.properties.StringProperty` and
    defaults to ''
    '''

    def __init__(self, **kwargs):
        super(SettingListCheckItem, self).__init__(**kwargs)

    def on_active(self, instance, *args):
        '''Callback to update the active value
        '''
        self.active = instance.active


class SettingListContent(BoxLayout):
    '''Widget to display SettingList
    '''
    setting = ObjectProperty(None)
    '''(internal) Reference to the setting SettingList.
    :attr:`setting` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    custom_item_layout = ObjectProperty(None)
    '''(internal) Widget that allows enter a custom item to the list.
    :attr:`custom_item` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    txt_custom_item = ObjectProperty(None)
    '''(internal) TextInput with the custom item name.
    :attr:`txt_custom_item` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    item_list = ObjectProperty(None)
    '''(internal) Widget that shows all items in a list.
    :attr:`item_list` is a :class:`~kivy.properties.ObjectProperty` and
    defaults to None
    '''

    selected_items = ListProperty([])
    '''List of selected items names. Updated only after clicking on Apply button
    :attr:`selected_item` is a :class:`~kivy.properties.ListProperty` and
    defaults to []
    '''

    __events__ = ('on_apply', 'on_cancel', )

    def __init__(self, **kwargs):
        super(SettingListContent, self).__init__(**kwargs)
        if not self.setting.allow_custom:
            self.remove_widget(self.custom_item_layout)

    def show_items(self, *args):
        '''Update the list of items
        '''
        self.clear_items()
        self.setting.items.sort()
        for item in self.setting.items:
            i = SettingListCheckItem(item_text=item, group=self.setting.group)
            if item in self.selected_items:
                i.active = True
            self.item_list.add_widget(i)

    def clear_items(self, *args):
        '''Remove all items from the item_list
        '''
        self.item_list.clear_widgets()

    def on_apply_pressed(self, *args):
        '''Event handler to Apply button.
        Get selected items and update the selected_items.
        '''
        self.update_selected_list()
        self.dispatch('on_apply', self.selected_items)

    def update_selected_list(self, *args):
        '''Update selected_items with the selected items
        '''
        self.selected_items = []
        for child in self.item_list.children:
            if child.active:
                self.selected_items.append(str(child.item_text))

    def add_custom_item(self, *args):
        '''Add a custom item to the list
        '''
        txt = self.txt_custom_item.text.strip()
        self.txt_custom_item.text = ''
        if txt and txt not in self.setting.items:
            self.setting.items.append(txt)
        self.update_selected_list()
        self.show_items()

    def on_cancel(self, *args):
        '''Event handler to Cancel button.
        '''
        pass

    def on_apply(self, *args):
        '''Event handler to Apply button
        '''
        pass


class SettingList(SettingItem):
    '''Implementation of an multi selection list on top of :class:`SettingItem`.
    '''

    items = ListProperty([])
    '''List with default visible items
    :attr:`items` is a :class:`~kivy.properties.ListProperty` and defaults
    to [].
    '''

    allow_custom = BooleanProperty(False)
    '''Allow/disallow a custom item to the list
    :attr:`allow_custom` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''

    group = StringProperty(None)
    '''CheckBox group name. If the CheckBox is in a Group,
    it becomes a Radio button.
    :attr:`group` is a :class:`~kivy.properties.StringProperty` and
    defaults to ''
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it is shown.

    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _create_popup(self, instance):
        # create the popup
        content = SettingListContent(setting=self)
        popup_width = min(0.95 * Window.width, 500)
        popup_height = min(0.95 * Window.height, 500)
        self.popup = popup = Popup(
            content=content, title=self.title, size_hint=(None, None),
            size=(popup_width, popup_height), auto_dismiss=False)

        content.bind(on_apply=self._set_values, on_cancel=self.popup.dismiss)
        selected_items = self.value.split(',')
        # update the item list with custom values
        for item in selected_items:
            item = item.strip()
            if item and not item in self.items:
                self.items.append(item)
        # list of items saved in the property
        content.selected_items = selected_items

        content.show_items()
        popup.open()

    def _set_values(self, *args):
        '''Read items and save them
        '''
        selected_items = args[1]
        self.value = ','.join(selected_items)
        self.popup.dismiss()
