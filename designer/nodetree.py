from kivy.uix.treeview import TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.app import App

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
                print rule.name, 'is custom'
                break

        if root_widget == node or not is_child_custom:
            for child in node.children:
                self.recursive_insert(child, b)

    def refresh(self, *l):
        '''This function will refresh the tree. It will first remove all nodes
           and then insert them using recursive_insert
        '''
        for node in self.tree.root.nodes:
            self.tree.remove_node(node)

        self.recursive_insert(self.playground.root, self.tree.root)
