from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, \
        BoundedNumericProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.app import App

from designer.undo_manager import PropOperation

class PropertyLabel(Label):
    pass

class PropertyBase(object):
    propwidget = ObjectProperty()
    propname = StringProperty()
    propvalue = ObjectProperty(allownone=True)
    oldvalue = ObjectProperty(allownone=True)
    have_error = BooleanProperty(False)
    proptype = StringProperty()
    record_to_undo = BooleanProperty(False)

    def set_value(self, value):
        self.have_error = False
        conversion_err = False
        oldvalue = getattr(self.propwidget, self.propname)
        try:
            if isinstance(self.propwidget.property(self.propname),
                          NumericProperty):
                if value == 'None':
                    value = None
                else:
                    value = float(value)
        except Exception:
            conversion_err = True
        
        root = App.get_running_app().root
        if not conversion_err:
            #try:
                setattr(self.propwidget, self.propname, value)
                root.kv_code_input.set_property_value(self.propwidget,
                                                      self.propname, value,
                                                      self.proptype)
                if self.record_to_undo:
                    root.undo_manager.push_operation(
                        PropOperation(self, oldvalue, value))
                self.record_to_undo = True
            #except Exception:            
            #    self.have_error = True
            #    setattr(self.propwidget, self.propname, oldvalue)


class PropertyTextInput(PropertyBase, TextInput):

    def insert_text(self, substring, from_undo=False):
        if self.proptype == 'NumericProperty' and \
           substring.isdigit() == False and\
           (substring != '.' or '.' in self.text)\
           and substring not in 'None':
                return

        super(PropertyTextInput, self).insert_text(substring)


class PropertyBoolean(PropertyBase, CheckBox):
    pass


class PropertyViewer(ScrollView):

    widget = ObjectProperty(allownone=True)
    prop_list = ObjectProperty()

    def on_widget(self, instance, value):
        self.clear()
        if value is not None:
            self.discover(value)

    def clear(self):
        self.prop_list.clear_widgets()

    def discover(self, value):
        add = self.prop_list.add_widget
        props = value.properties().keys()
        props.sort()
        for prop in props:
            ip = self.build_for(prop)
            if not ip:
                continue
            add(PropertyLabel(text=prop))
            add(ip)

    def build_for(self, name):
        prop = self.widget.property(name)
        if isinstance(prop, NumericProperty):
            return PropertyTextInput(propwidget=self.widget, propname=name,
                                     proptype = 'NumericProperty')
        elif isinstance(prop, StringProperty):
            return PropertyTextInput(propwidget=self.widget, propname=name,
                                     proptype = 'StringProperty')
        elif isinstance(prop, BooleanProperty):
            ip = PropertyBoolean(propwidget=self.widget, propname=name,
                                   proptype = 'BooleanProperty')
            ip.record_to_undo = True
            return ip

        return None

