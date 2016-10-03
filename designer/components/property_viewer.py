from designer.core.undo_manager import PropOperation
from designer.uix.settings import SettingListContent
from designer.utils.utils import FakeSettingList, get_designer
from kivy.core.window import Window
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    OptionProperty,
    StringProperty,
)
from kivy.uix.checkbox import CheckBox
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput


class PropertyLabel(Label):
    '''This class represents the :class:`~kivy.label.Label` for showing
       Property Names in
       :class:`~designer.components.property_viewer.PropertyViewer`.
    '''
    pass


class PropertyBase(object):
    '''This class represents Abstract Class for Property showing classes i.e.
       PropertyTextInput and PropertyBoolean
    '''

    propwidget = ObjectProperty()
    '''It is an instance to the Widget whose property value is displayed.
       :data:`propwidget` is a :class:`~kivy.properties.ObjectProperty`
    '''

    propname = StringProperty()
    '''It is the name of the property.
       :data:`propname` is a :class:`~kivy.properties.StringProperty`
    '''

    propvalue = ObjectProperty(allownone=True)
    '''It is the value of the property.
       :data:`propvalue` is a :class:`~kivy.properties.ObjectProperty`
    '''

    oldvalue = ObjectProperty(allownone=True)
    '''It is the old value of the property
       :data:`oldvalue` is a :class:`~kivy.properties.ObjectProperty`
    '''

    have_error = BooleanProperty(False)
    '''It specifies whether there have been an error in setting new value
       to property
       :data:`have_error` is a :class:`~kivy.properties.BooleanProperty`
    '''

    proptype = StringProperty()
    '''It is the type of property.
       :data:`proptype` is a :class:`~kivy.properties.StringProperty`
    '''

    record_to_undo = BooleanProperty(False)
    '''It specifies whether the property change has to be recorded to undo.
       It is used when :class:`~designer.core.undo_manager.UndoManager` undoes
       or redoes the property change.
       :data:`record_to_undo` is a :class:`~kivy.properties.BooleanProperty`
    '''

    kv_code_input = ObjectProperty()
    '''It is a reference to the
       :class:`~designer.uix.kv_code_input.KVLangArea`.
       :data:`kv_code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def set_value(self, value):
        '''This function first converts the value of the propwidget, then sets
           the new value. If there is some error in setting new value, then it
           sets the property value back to oldvalue
        '''

        self.have_error = False
        conversion_err = False
        oldvalue = getattr(self.propwidget, self.propname)
        try:
            if isinstance(self.propwidget.property(self.propname),
                          NumericProperty):

                if value == 'None' or value == '':
                    value = None
                else:
                    value = float(value)

        except Exception:
            conversion_err = True

        designer = get_designer()
        if not conversion_err:
            try:
                setattr(self.propwidget, self.propname, value)
                self.kv_code_input.set_property_value(self.propwidget,
                                                      self.propname, value,
                                                      self.proptype)
                if self.record_to_undo:
                    designer.undo_manager.push_operation(
                        PropOperation(self, oldvalue, value))
                self.record_to_undo = True
            except Exception:
                self.have_error = True
                setattr(self.propwidget, self.propname, oldvalue)


class PropertyOptions(PropertyBase, Label):
    '''PropertyOptions to show/set/get options for an OptionProperty
    '''

    def __init__(self, prop, **kwargs):
        super(PropertyOptions, self).__init__(**kwargs)
        self._chooser = None
        self._original_options = prop.options
        self._options = prop.options
        if self._options and isinstance(self._options[0], list):
            # handler to list option properties
            opts = []
            for op in self._options:
                opts.append(str(op))
            self._options = opts

    def on_propvalue(self, *args):
        '''Default handler for 'on_propvalue'.
        '''

        if self.propvalue:
            if isinstance(self.propvalue, list):
                self.text = str(self.propvalue)
            else:
                self.text = self.propvalue
        else:
            self.text = ''

    def on_touch_down(self, touch):
        '''Display the option chooser
        '''
        d = get_designer()
        if d.popup:
            return False
        if self.collide_point(*touch.pos):
            if self._chooser is None:
                fake_setting = FakeSettingList()
                fake_setting.allow_custom = False
                fake_setting.items = self._options
                fake_setting.desc = 'Property Options'
                fake_setting.group = 'property_options'
                content = SettingListContent(setting=fake_setting)
                self._chooser = content

            self._chooser.parent = None
            self._chooser.selected_items = [self.text]
            self._chooser.show_items()

            popup_width = min(0.95 * Window.width, 500)
            popup_height = min(0.95 * Window.height, 500)
            d.popup = Popup(
                content=self._chooser,
                title='Property Options - ' + self.propname,
                size_hint=(None, None),
                size=(popup_width, popup_height),
                auto_dismiss=False
            )

            self._chooser.bind(
                    on_apply=self._on_options,
                    on_cancel=d.close_popup)

            d.popup.open()
            return True

        return False

    def _on_options(self, instance, selected_items):
        if isinstance(self._original_options[0], list):
            new_value = eval(selected_items[0])
        else:
            new_value = selected_items[0]
        self.propvalue = new_value
        self.set_value(new_value)
        get_designer().close_popup()


class PropertyTextInput(PropertyBase, TextInput):
    '''PropertyTextInput is used as widget to display
       :class:`~kivy.properties.StringProperty` and
       :class:`~kivy.properties.NumericProperty`.
    '''

    def value_changed(self, value, *args):
        if value != str(getattr(self.propwidget, self.propname)):
            self.set_value(value)

    def insert_text(self, substring, from_undo=False):
        '''Override of :class:`~kivy.uix.textinput.TextInput`.insert_text,
           it first checks whether the value being entered is valid or not.
           If yes, then it enters that value otherwise it doesn't.
           For Example, if Property is NumericProperty then it will
           first checks if value being entered should be a number
           or decimal only.
        '''
        if self.proptype == 'NumericProperty' and \
           substring.isdigit() is False and\
           (substring != '.' or '.' in self.text)\
           and substring not in 'None':
                return

        super(PropertyTextInput, self).insert_text(substring)


class PropertyBoolean(PropertyBase, CheckBox):
    '''PropertyBoolean is used as widget to display
       :class:`~kivy.properties.BooleanProperty`.
    '''
    pass


class PropertyViewer(ScrollView):
    '''PropertyViewer is used to display property names and their corresponding
       value.
    '''

    widget = ObjectProperty(allownone=True)
    '''Widget for which properties are displayed.
       :data:`widget` is a :class:`~kivy.properties.ObjectProperty`
    '''

    prop_list = ObjectProperty()
    '''Widget in which all the properties and their value is added. It is a
       :class:`~kivy.gridlayout.GridLayout.
       :data:`prop_list` is a :class:`~kivy.properties.ObjectProperty`
    '''

    kv_code_input = ObjectProperty()
    '''It is a reference to the KVLangArea.
       :data:`kv_code_input` is a :class:`~kivy.properties.ObjectProperty`
    '''

    def __init__(self, **kwargs):
        super(PropertyViewer, self).__init__(**kwargs)
        self._label_cache = {}

    def on_widget(self, instance, new_widget):
        '''Default handler for 'on_widget'.
        '''
        self.clear()
        if new_widget is not None:
            self.discover(new_widget)

    def clear(self):
        '''To clear :data:`prop_list`.
        '''
        self.prop_list.clear_widgets()

    def discover(self, value):
        '''To discover all properties and add their
           :class:`~designer.components.property_viewer.PropertyLabel` and
           :class:`~designer.components.property_viewer.PropertyBoolean`/
           :class:`~designer.components.property_viewer.PropertyTextInput`
           to :data:`prop_list`.
        '''

        add = self.prop_list.add_widget
        get_label = self._get_label
        props = list(value.properties().keys())
        props.sort()

        for prop in props:
            ip = self.build_for(prop)
            if not ip:
                continue
            add(get_label(prop))
            add(ip)

    def _get_label(self, prop):
        try:
            return self._label_cache[prop]
        except KeyError:
            lbl = self._label_cache[prop] = PropertyLabel(text=prop)
            return lbl

    def build_for(self, name):
        '''Creates a EventHandlerTextInput for each property given its name
        '''

        prop = self.widget.property(name)
        if isinstance(prop, NumericProperty):
            return PropertyTextInput(propwidget=self.widget, propname=name,
                                     proptype='NumericProperty',
                                     kv_code_input=self.kv_code_input)

        elif isinstance(prop, StringProperty):
            return PropertyTextInput(propwidget=self.widget, propname=name,
                                     proptype='StringProperty',
                                     kv_code_input=self.kv_code_input)

        elif isinstance(prop, ListProperty):
            return PropertyTextInput(propwidget=self.widget, propname=name,
                                     proptype='ListProperty',
                                     kv_code_input=self.kv_code_input)

        elif isinstance(prop, BooleanProperty):
            ip = PropertyBoolean(propwidget=self.widget, propname=name,
                                 proptype='BooleanProperty',
                                 kv_code_input=self.kv_code_input)
            ip.record_to_undo = True
            return ip

        elif isinstance(prop, OptionProperty):
            ip = PropertyOptions(prop, propwidget=self.widget, propname=name,
                                 proptype='OptionProperty',
                                 kv_code_input=self.kv_code_input)
            return ip

        return None
