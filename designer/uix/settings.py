from designer.utils.utils import get_designer
from kivy.core.window import Keyboard, Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    ObjectProperty,
    StringProperty,
)
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

<SettingShortcut>:
    Label:
        text: root.hint or ''
        pos: root.pos
        font_size: '15sp'

<SettingShortcutContent>:
    orientation: 'vertical'
    BoxLayout:
        GridLayout:
            cols: 2
            canvas.after:
                Color:
                    rgb: .3, .3, .3
                Rectangle:
                    pos: self.right - 1, self.y
                    size: 1, self.height - 30
            Label:
                size_hint: None, None
                size: 0, 0
            Label:
                size_hint_y: None
                height: 30
                text: 'Modifiers'
                text_size: self.size
                halign: 'center'
            CheckBox:
                active: root.has_ctrl
                on_active: root.has_ctrl = self.active
                size_hint_x: 0.2
            Label:
                text: 'Ctrl'
                text_size: self.size
                valign: 'middle'
            CheckBox:
                active: root.has_shift
                on_active: root.has_shift = self.active
                size_hint_x: 0.2
            Label:
                text: 'Shift'
                text_size: self.size
                valign: 'middle'
            CheckBox:
                active: root.has_alt
                on_active: root.has_alt = self.active
                size_hint_x: 0.2
            Label:
                text: 'Alt'
                text_size: self.size
                valign: 'middle'

        BoxLayout:
            orientation: 'vertical'
            Label:
                size_hint_y: None
                height: 30
                text: 'Key'
                text_size: self.size
                halign: 'center'
            Label:
                text: root.key
                font_size: '20pt'
                text_size: self.size
                valign: 'middle'
                halign: 'center'
    Label:
        text: root.error
        size_hint_y: None
        height: 30
        color: [1, 0, 0, 1]
        opacity: 1 if self.text else 0
    BoxLayout:
        size_hint_y: None
        height: '24pt'
        Button:
            text: 'Cancel'
            on_press: root.dispatch('on_cancel')
        Button:
            text: 'Disable'
            on_press: root.dispatch('on_disable')
        Button:
            text: 'Confirm'
            on_press: root.dispatch('on_confirm', root.value)
            disabled: not root.valid
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
    :class:`~kivy.properties.StringProperty` and defaults to ''
    '''

    item_check = ObjectProperty(None)
    '''Instance of checkbox. :attr:`item_check` is a
        :class:`~kivy.properties.ObjectProperty` and defaults to None
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
        if self.group:
            self.item_check.allow_no_selection = False

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

    __events__ = ('on_apply', 'on_cancel',)

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


class SettingShortcutContent(BoxLayout):

    has_ctrl = BooleanProperty(False)
    '''Indicates if should listen the Ctrl key
    :attr:`has_ctrl` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''

    has_shift = BooleanProperty(False)
    '''Indicates if should listen the Shift key
    :attr:`has_shift` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''

    has_alt = BooleanProperty(False)
    '''Indicates if should listen the Alt key
    :attr:`has_alt` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''

    listen_key = BooleanProperty(False)
    '''Indicates if should listen the keyboard
    :attr:`listen_key` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to False
    '''

    valid = BooleanProperty(True)
    '''(internal) Indicates if the shortcut is valid
    :attr:`valid` is a :class:`~kivy.properties.BooleanProperty`
    and defaults to True
    '''

    key = StringProperty('')
    '''Indicates the shortcut key
    :attr:`key` is a :class:`~kivy.properties.StringProperty`
    and defaults to ''
    '''

    config_name = StringProperty('')
    '''Indicates the field key on shortcuts.json
    :attr:`config_name` is a :class:`~kivy.properties.StringProperty`
    and defaults to ''
    '''

    value = StringProperty('')
    '''Indicates the shortcut in the String format
    :attr:`value` is a :class:`~kivy.properties.StringProperty`
    and defaults to ''
    '''

    error = StringProperty('')
    '''Error message
    :attr:`error` is a :class:`~kivy.properties.StringProperty`
    and defaults to ''
    '''

    __events__ = ('on_confirm', 'on_disable', 'on_cancel',)

    def __init__(self, **kwargs):
        super(SettingShortcutContent, self).__init__(**kwargs)
        self.bind(has_ctrl=self.validate_shortcut)
        self.bind(has_shift=self.validate_shortcut)
        self.bind(has_alt=self.validate_shortcut)
        self.bind(key=self.validate_shortcut)

    def validate_shortcut(self, *args):
        '''Check if it's a valid shortcut and if it's being used somewhere else
        Updates the error label and return a boolean
        '''
        # restore default values
        self.valid = True
        self.error = ''

        valid = False
        if (self.has_ctrl or self.has_shift or self.has_alt) and self.key:
            valid = True

        if self.key in ['f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9'
                        'f10', 'f11', 'f12']:
            valid = True

        modifier = []
        if self.has_ctrl:
            modifier.append('ctrl')
        if self.has_shift:
            modifier.append('shift')
        if self.has_alt:
            modifier.append('alt')
        modifier.sort()
        value = str(modifier) + ' + ' + self.key
        # check if shortcut exist
        d = get_designer()
        if value and value in d.shortcuts.map:
            shortcut = d.shortcuts.map[value]
            if shortcut[1] != self.config_name:
                valid = False
                self.error = 'Shortcut already being used at ' + shortcut[1]

        if valid:
            self.value = value
            self.error = ''
        else:
            self.value = ''
            if not self.error:
                self.error = 'This shortcut is not valid'

        self.valid = valid
        return valid

    def on_listen_key(self, instance, value, *args):
        '''Enable/disable keyboard listener
        '''
        if value:
            Window.bind(on_key_down=self._on_key_down)
        else:
            Window.unbind(on_key_down=self._on_key_down)

    def _on_key_down(self, keyboard, key, codepoint, text, modifier, **kwargs):
        '''Listen keyboard to create shortcuts. Update class properties
        '''
        self.key = Keyboard.keycode_to_string(Window._system_keyboard, key)
        if self.key in ['ctrl', 'shift', 'alt']:
            self.key = ''
        if modifier is None:
            modifier = []
        self.has_ctrl = 'ctrl' in modifier
        self.has_shift = 'shift' in modifier
        self.has_alt = 'alt' in modifier

        return True

    def parse_value(self, value, *args):
        '''Parse the value string and update shortcut parameters.
        If value is invalid, returns False and set a clean shortcut
        :param value: string with formatted shortcut
        '''
        try:
            mod, key = value.split('+')
            key = key.strip()
            self.key = key
            modifier = eval(mod)
            self.has_ctrl = 'ctrl' in modifier
            self.has_shift = 'shift' in modifier
            self.has_alt = 'alt' in modifier
            self.value = value
            return True
        except:
            return False

    def on_cancel(self, *args):
        '''Event handler to cancel button
        '''
        pass

    def on_disable(self, *args):
        '''Event handler to disable button
        '''
        self.key = ''
        self.has_alt = False
        self.has_shift = False
        self.has_ctrl = False
        self.value = ''
        self.error = ''
        self.valid = True

    def on_confirm(self, *args):
        '''Event handler to confirm button
        '''
        pass


class SettingShortcut(SettingItem):
    '''Implementation of a shortcut listener.
    Setting will be stored in the format:
        [Modifiers, ...] + keycode(string)
    The modifiers are in alphabetical order and separated with a space
    All chars is in lowercase
    eg
        ['ctrl'] + q
        ['ctrl', 'shift'] + a
        [] + f1
    '''

    popup = ObjectProperty(None, allownone=True)
    '''(internal) Used to store the current popup when it's shown.

    :attr:`popup` is an :class:`~kivy.properties.ObjectProperty` and defaults
    to None.
    '''

    hint = StringProperty('')
    '''Readable shortcut. Parses value to display on settings panel
    :attr:`hint` is an :class:`~kivy.properties.StringProperty` and defaults
    to ''.
     '''

    def on_panel(self, instance, value):
        if value is None:
            return
        self.bind(on_release=self._create_popup)

    def _dismiss(self, *largs):
        if self.popup:
            self.popup.dismiss()
        self.popup = None

    def _create_popup(self, instance):
        # create popup layout
        content = SettingShortcutContent()
        content.listen_key = True
        content.config_name = self.key
        if self.value:
            content.parse_value(self.value)
        content.bind(on_confirm=self.on_confirm)
        content.bind(on_cancel=self._dismiss)
        popup_width = min(0.95 * Window.width, dp(500))
        self.popup = popup = Popup(
                title='Shortcut - ' + self.title,
                content=content,
                size_hint=(None, None),
                size=(popup_width, '250dp'))

        popup.open()

    def on_confirm(self, instance, value, *args):
        '''Callback to shortcut editor confirm
        :param instance: instance of shortcut editor(content)
        :param value: string with the formatted shortcut
        '''
        instance.listen_key = False
        self.value = value
        self._dismiss()

    def on_cancel(self, instance, *args):
        '''Callback to shortcut editor cancel
        :param instance: instance of shortcut editor(content)
        '''
        instance.listen_key = False
        self._dismiss()

    def on_value(self, instance, value):
        super(SettingShortcut, self).on_value(instance, value)
        mod, key = self.value.split('+')
        key = key.strip()
        modifier = eval(mod)
        hint = ' + '.join(modifier) + ' + ' + key
        self.hint = hint.title()
