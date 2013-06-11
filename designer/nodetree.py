from kivy.uix.treeview import TreeViewLabel
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty


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

        for child in node.children:
            self.recursive_insert(child, b)

    def refresh(self, *l):
        for node in self.tree.root.nodes:
            self.tree.remove_node(node)

        self.recursive_insert(self.playground.root, self.tree.root)
