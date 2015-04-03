from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, NumericProperty, StringProperty,\
    BoundedNumericProperty, BooleanProperty, OptionProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.app import App

from designer.undo_manager import PropOperation


class PropertyLabel(Label):
    '''This class represents the :class:`~kivy.label.Label` for showing
       Property Names in :class:`~designer.propertyviewer.PropertyViewer`.
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
       It is used when :class:`~designer.undo_manager.UndoManager` undoes
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

        root = App.get_running_app().root
        if not conversion_err:
            try:
                setattr(self.propwidget, self.propname, value)
                self.kv_code_input.set_property_value(self.propwidget,
                                                      self.propname, value,
                                                      self.proptype)
                if self.record_to_undo:
                    root.undo_manager.push_operation(
                        PropOperation(self, oldvalue, value))
                self.record_to_undo = True
            except Exception:
                self.have_error = True
                setattr(self.propwidget, self.propname, oldvalue)


class PropertyOptions(PropertyBase, Spinner):
    '''PropertyOptions to show/set/get options for an OptionProperty
    '''

    def __init__(self, prop, **kwargs):
        PropertyBase.__init__(self)
        Spinner.__init__(self, values=prop.options, **kwargs)

    def on_propvalue(self, *args):
        '''Default handler for 'on_propvalue'.
        '''
        self.text = self.propvalue


class PropertyTextInput(PropertyBase, TextInput):
    '''PropertyTextInput is used as widget to display
       :class:`~kivy.properties.StringProperty` and
       :class:`~kivy.properties.NumericProperty`.
    '''

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

    def on_widget(self, instance, value):
        '''Default handler for 'on_widget'.
        '''
        self.clear()
        if value is not None:
            self.discover(value)

    def clear(self):
        '''To clear :data:`prop_list`.
        '''
        self.prop_list.clear_widgets()

    def discover(self, value):
        '''To discover all properties and add their
           :class:`~designer.propertyviewer.PropertyLabel` and
           :class:`~designer.propertyviewer.PropertyBoolean`/
           :class:`~designer.propertyviewer.PropertyTextInput`
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
        '''To create :class:`~designer.propertyviewer.PropertyBoolean`
           :class:`~designer.propertyviewer.PropertyTextInput`
           for Property 'name'
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

        elif isinstance(prop, BooleanProperty):
            ip = PropertyBoolean(propwidget=self.widget, propname=name,
                                 proptype='BooleanProperty',
                                 kv_code_input=self.kv_code_input)
            ip.record_to_undo = True
            return ip

        elif isinstance(prop, OptionProperty):
            ip = PropertyOptions(prop, propwidget=self.widget, propname=name,
                                 proptype='StringProperty',
                                 kv_code_input=self.kv_code_input)
            return ip

        return None
