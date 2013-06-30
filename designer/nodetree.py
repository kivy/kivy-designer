from kivy.uix.treeview import TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty
from kivy.app import App

class WidgetTreeElement(TreeViewLabel):
    node = ObjectProperty(None)

class WidgetsTree(ScrollView):
    playground = ObjectProperty(None)
    tree = ObjectProperty(None)

    def recursive_insert(self, node, treenode):
        if node is None:
            return

        b = WidgetTreeElement(node=node)
        self.tree.add_node(b, treenode)
        class_rules = App.get_running_app().root.project_loader.class_rules
        root_widget = App.get_running_app().root.project_loader.root_rule.widget

        is_child_custom = False
        for rule in class_rules:
            if rule.name == type(node).__name__:
                is_child_custom = True
                break

        if root_widget == node or not is_child_custom:
            for child in node.children:
                self.recursive_insert(child, b)

    def refresh(self, *l):
        for node in self.tree.root.nodes:
            self.tree.remove_node(node)

        self.recursive_insert(self.playground.root, self.tree.root)
