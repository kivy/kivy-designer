from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.app import App

class OperationBase(object):
    '''UndoOperationBase class, base class for all Undo Operations
    '''

    def __init__(self, operation_type):
        super(OperationBase, self).__init__()
        self.operation_type = operation_type

    def do_undo(self):
        pass

    def do_redo(self):
        pass

class WidgetOperation(OperationBase):
    '''WidgetOperation class for widget operations of add and remove
    '''

    def __init__(self, widget_op_type, widget, parent, playground, kv_str):
        super(WidgetOperation, self).__init__('widget')
        self.widget_op_type  = widget_op_type
        self.parent = parent
        self.widget = widget
        self.playground = playground
        self.kv_str = kv_str

    def do_undo(self):
        if self.widget_op_type == 'add':
            self.playground.remove_widget_from_parent(self.widget, True)

        else:
            self.widget.parent = None
            self.playground.add_widget_to_parent(self.widget, self.parent,
                                                 from_undo=True,
                                                 kv_str=self.kv_str)

    def do_redo(self):
        if self.widget_op_type == 'remove':
            self.playground.remove_widget_from_parent(self.widget, True)

        else:
            self.widget.parent = None
            self.playground.add_widget_to_parent(self.widget, self.parent,
                                                 from_undo=True,
                                                 kv_str=self.kv_str)

class PropOperation(OperationBase):
    '''PropOperation class for Property Operations of changing property value
    '''

    def __init__(self, prop, oldvalue, newvalue):
        super(PropOperation, self).__init__('property')
        self.prop = prop
        self.oldvalue = oldvalue
        self.newvalue = newvalue

    def do_undo(self):
        setattr(self.prop.propwidget, self.prop.propname, self.oldvalue)
        self._update_widget(self.oldvalue)

    def _update_widget(self, value):
        self.prop.record_to_undo = False
        if isinstance(self.prop, TextInput):
            self.prop.text = value
        elif isinstance(self.prop, CheckBox):
            self.prop.active = value

    def do_redo(self):
        setattr(self.prop.propwidget, self.prop.propname, self.newvalue)
        self._update_widget(self.newvalue)

class UndoManager(object):

    def __init__(self, **kwargs):
        super(UndoManager, self).__init__(**kwargs)
        self._undo_stack_operation = []
        self._redo_stack_operation = []

    def push_operation(self, op):
        App.get_running_app().root._curr_proj_changed = True
        self._undo_stack_operation.append(op)

    def do_undo(self):
        if self._undo_stack_operation == []:
            return

        operation = self._undo_stack_operation.pop()
        operation.do_undo()
        self._redo_stack_operation.append(operation)

    def do_redo(self):
        if self._redo_stack_operation == []:
            return

        operation = self._redo_stack_operation.pop()
        operation.do_redo()
        self._undo_stack_operation.append(operation)
    
    def cleanup(self):
        self._undo_stack_operation = []
        self._redo_stack_operation = []
