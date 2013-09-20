from kivy.properties import ObjectProperty, OptionProperty
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.app import App


class OperationBase(object):
    '''UndoOperationBase class, Abstract class for all Undo Operations
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
        self.widget_op_type = widget_op_type
        self.parent = parent
        self.widget = widget
        self.playground = playground
        self.kv_str = kv_str

    def do_undo(self):
        '''Override of :class:`OperationBase`.do_undo.
           This will undo a WidgetOperation.
        '''
        if self.widget_op_type == 'add':
            self.playground.remove_widget_from_parent(self.widget, True)

        else:
            self.widget.parent = None
            self.playground.add_widget_to_parent(self.widget, self.parent,
                                                 from_undo=True,
                                                 kv_str=self.kv_str)

    def do_redo(self):
        '''Override of :class:`OperationBase`.do_redo.
           This will redo a WidgetOperation.
        '''

        if self.widget_op_type == 'remove':
            self.playground.remove_widget_from_parent(self.widget, True)

        else:
            self.widget.parent = None
            self.playground.add_widget_to_parent(self.widget, self.parent,
                                                 from_undo=True,
                                                 kv_str=self.kv_str)


class WidgetDragOperation(OperationBase):

    def __init__(self, widget, cur_parent, prev_parent, prev_index,
                 playground, extra_args):
        self.widget = widget
        self.cur_parent = cur_parent
        self.prev_parent = prev_parent
        self.prev_index = prev_index
        self.playground = playground
        self.cur_index = extra_args['index']
        self.extra_args = extra_args

    def do_undo(self):
        self.cur_parent.remove_widget(self.widget)
        self.playground.drag_wigdet(self.widget, self.prev_parent,
                                    extra_args={'index': self.prev_index,
                                                'prev_index': self.cur_index,
                                                'x': self.extra_args['prev_x'],
                                                'y': self.extra_args['prev_y']},
                                    from_undo=True)

    def do_redo(self):
        self.prev_parent.remove_widget(self.widget)
        self.playground.drag_wigdet(self.widget, self.cur_parent,
                                    extra_args={'index': self.cur_index,
                                                'prev_index': self.prev_index,
                                                'x': self.extra_args['x'],
                                                'y': self.extra_args['y']},
                                    from_undo=True)


class PropOperation(OperationBase):
    '''PropOperation class for Property Operations of changing property value
    '''

    def __init__(self, prop, oldvalue, newvalue):
        super(PropOperation, self).__init__('property')
        self.prop = prop
        self.oldvalue = oldvalue
        self.newvalue = newvalue

    def do_undo(self):
        '''Override of :class:`OperationBase`.do_undo.
           This will undo a PropOperation.
        '''

        setattr(self.prop.propwidget, self.prop.propname, self.oldvalue)
        self._update_widget(self.oldvalue)

    def _update_widget(self, value):
        '''After do_undo or do_redo, this function will update the PropWidget's
           value associated with that property.
        '''
        self.prop.record_to_undo = False
        if isinstance(self.prop, TextInput):
            self.prop.text = value
        elif isinstance(self.prop, CheckBox):
            self.prop.active = value

    def do_redo(self):
        '''Override of :class:`OperationBase`.do_redo.
           This will redo a PropOperation.
        '''

        setattr(self.prop.propwidget, self.prop.propname, self.newvalue)
        self._update_widget(self.newvalue)


class UndoManager(object):
    '''UndoManager is reponsible for managing all the operations related
       to Widgets. It is also responsible for redoing and undoing the last
       available operation.
    '''

    def __init__(self, **kwargs):
        super(UndoManager, self).__init__(**kwargs)
        self._undo_stack_operation = []
        self._redo_stack_operation = []

    def push_operation(self, op):
        '''To push an operation into _undo_stack.
        '''
        App.get_running_app().root._curr_proj_changed = True
        self._undo_stack_operation.append(op)

    def do_undo(self):
        '''To undo last operation
        '''
        if self._undo_stack_operation == []:
            return

        operation = self._undo_stack_operation.pop()
        operation.do_undo()
        self._redo_stack_operation.append(operation)

    def do_redo(self):
        '''To redo last operation
        '''

        if self._redo_stack_operation == []:
            return

        operation = self._redo_stack_operation.pop()
        operation.do_redo()
        self._undo_stack_operation.append(operation)

    def cleanup(self):
        '''To cleanup operation stacks when another project is loaded
        '''
        self._undo_stack_operation = []
        self._redo_stack_operation = []
