from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, \
        BoundedNumericProperty, BooleanProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.app import App

from designer.undo_manager import PropOperation

class PropertyLabel(Label):
    '''This class represents the Label for showing Property Names in
       PropertyViewer.
    '''
    pass

class PropertyBase(object):
    '''This class represents Abstract Class for Property showing classes i.e.
       PropertyTextInput and PropertyBoolean
    '''

    propwidget = ObjectProperty()
    '''It is an instance to the Widget whose property value is displayed.
    '''

    propname = StringProperty()
    '''It is the name of the property.
    '''

    propvalue = ObjectProperty(allownone=True)
    '''It is the value of the property.
    '''

    oldvalue = ObjectProperty(allownone=True)
    '''It is the old value of the property
    '''

    have_error = BooleanProperty(False)
    '''It specifies whether there have been an error in setting new value 
       to property
    '''

    proptype = StringProperty()
    '''It is the type of property.
    '''

    record_to_undo = BooleanProperty(False)
    '''It specifies whether the property change has to be recorded to undo.
       It is used when UndoManager undoes or redoes the property change.
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
                if value == 'None':
                    value = None
                else:
                    value = float(value)
        except Exception:
            conversion_err = True

        root = App.get_running_app().root
        if not conversion_err:
            try:
                setattr(self.propwidget, self.propname, value)
                root.kv_code_input.set_property_value(self.propwidget,
                                                      self.propname, value,
                                                      self.proptype)
                if self.record_to_undo:
                    root.undo_manager.push_operation(
                        PropOperation(self, oldvalue, value))
                self.record_to_undo = True
            except Exception:            
                self.have_error = True
                setattr(self.propwidget, self.propname, oldvalue)


class PropertyTextInput(PropertyBase, TextInput):
    '''PropertyTextInput is used as widget to display StringProperty and
       NumericProperty.
    '''

    def insert_text(self, substring, from_undo=False):
        '''Override of TextInput.insert_text, it first checks whether the
           value being entered is valid or not. If yes, then it enters
           that value otherwise it doesn't. For Example, if Property is 
           NumericProperty then it will first checks if value being entered
           should be a number or decimal only.
        '''
        if self.proptype == 'NumericProperty' and \
           substring.isdigit() == False and\
           (substring != '.' or '.' in self.text)\
           and substring not in 'None':
                return

        super(PropertyTextInput, self).insert_text(substring)


class PropertyBoolean(PropertyBase, CheckBox):
    '''PropertyTextInput is used as widget to display BooleanProperty.
    '''
    pass


class PropertyViewer(ScrollView):
    '''PropertyViewer is used to display property names and their corresponding
       value.
    '''

    widget = ObjectProperty(allownone=True)
    '''Widget for which properties are displayed
    '''

    prop_list = ObjectProperty()
    '''Widget in which all the properties and their value is added. It is a 
       GridLayout.
    '''

    def on_widget(self, instance, value):
        self.clear()
        if value is not None:
            self.discover(value)

    def clear(self):
        '''To clear prop_list.
        '''
        self.prop_list.clear_widgets()

    def discover(self, value):
        '''To discover all properties and add their PropertyLabel and
           PropertyTextInput/PropertyBoolean to prop_list.
        '''

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
        '''To create PropertyBoolean/PropertyTextInput for Property 'name'
        '''

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
