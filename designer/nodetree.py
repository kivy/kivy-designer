from kivy.uix.treeview import TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.app import App
from kivy.clock import Clock

from designer.uix.placeholder import Placeholder

class WidgetTreeElement(TreeViewLabel):
    '''WidgetTreeElement represents each node in WidgetsTree
    '''
    node = ObjectProperty(None)

class WidgetsTree(ScrollView):
    '''WidgetsTree class is used to display the Root Widget's Tree in a 
       Tree hierarchy.
    '''
    playground = ObjectProperty(None)
    '''This property is an instance of :class:`~designer.playground.Playground`
       :data:`playground` is a :class:`~kivy.properties.ObjectProperty`
    '''

    tree = ObjectProperty(None)
    '''This property is an instance of :class:`~kivy.uix.treeview.TreeView`.
       This TreeView is responsible for showing Root Widget's Tree.
       :data:`tree` is a :class:`~kivy.properties.ObjectProperty`
    '''
    
    project_loader = ObjectProperty()
    '''Reference to :class:`~designer.project_loader.ProjectLoader` instance.
       :data:`project_loader` is a :class:`~kivy.properties.ObjectProperty`
    '''
    
    dragging = BooleanProperty(False)

    selected_widget = ObjectProperty(allownone=True)
    

    def recursive_insert(self, node, treenode):
        '''This function will add a node to TreeView, by recursively travelling
           through the Root Widget's Tree.
        '''

        if node is None:
            return

        b = WidgetTreeElement(node=node)
        self.tree.add_node(b, treenode)
        class_rules = self.project_loader.class_rules
        root_widget = self.project_loader.root_rule.widget

        is_child_custom = False
        for rule in class_rules:
            if rule.name == type(node).__name__:
                is_child_custom = True
                break

        if root_widget == node or not is_child_custom:
            for child in node.children:
                if not isinstance(child, Placeholder):
                    self.recursive_insert(child, b)

    def refresh(self, *l):
        '''This function will refresh the tree. It will first remove all nodes
           and then insert them using recursive_insert
        '''
        for node in self.tree.root.nodes:
            self.tree.remove_node(node)

        self.recursive_insert(self.playground.root, self.tree.root)

    def on_touch_up(self, touch):
        self.dragging = False
        if self.collide_point(*touch.pos):
            Clock.unschedule(self._start_dragging)
            super(WidgetsTree, self).on_touch_up(touch)

        return False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and not self.dragging:
            self.dragging = True
            self.touch = touch
            Clock.schedule_once(self._start_dragging, 2)
            node = self.tree.get_node_at_pos((self.touch.x, self.touch.y))
            if node:
                self.selected_widget = node.node
            else:
                self.selected_widget = None

            super(WidgetsTree, self).on_touch_down(touch)

        return False

    def _start_dragging(self, *args):
        if self.dragging and self.selected_widget:
            self.playground.selected_widget = self.selected_widget
            self.playground.dragging = False
            self.playground.touch = self.touch
            self.playground.start_widget_dragging()