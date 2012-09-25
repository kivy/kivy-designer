from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, \
        BoundedNumericProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox

class PropertyLabel(Label):
    pass

class PropertyBase(object):
    propwidget = ObjectProperty()
    propname = StringProperty()
    propvalue = ObjectProperty(allownone=True)
    oldvalue = ObjectProperty(allownone=True)
    have_error = BooleanProperty(False)

    def set_value(self, value):
        self.have_error = False
        oldvalue = getattr(self.propwidget, self.propname)

        try:
            if isinstance(self.propwidget.property(self.propname), NumericProperty):
                value = float(value)
        except Exception:
            pass
        try:
            setattr(self.propwidget, self.propname, value)
        except Exception:
            self.have_error = True
            setattr(self.propwidget, self.propname, oldvalue)



class PropertyTextInput(PropertyBase, TextInput):
    pass

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
            return PropertyTextInput(propwidget=self.widget, propname=name)
        elif isinstance(prop, StringProperty):
            return PropertyTextInput(propwidget=self.widget, propname=name)
        elif isinstance(prop, BooleanProperty):
            return PropertyBoolean(propwidget=self.widget, propname=name)
        return None

