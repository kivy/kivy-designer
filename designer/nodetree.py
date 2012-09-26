from kivy.uix.treeview import TreeViewNode
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty


class TreeViewButton(BoxLayout, TreeViewNode):
    tree = ObjectProperty(None)
    app = ObjectProperty(None)
    node = ObjectProperty(None)

    def focus(self, *l):
        self.app.focus_widget(self.node)

    def remove(self, *l):
        print "remove", self.node
        parent = self.node.parent
        parent.remove_widget(self.node)
        self.tree.refresh()


class WidgetsTree(ScrollView):
    playground = ObjectProperty(None)
    app = ObjectProperty(None)
    tree = ObjectProperty(None)

    def recursive_insert(self, node, treenode):
        b = TreeViewButton(tree=self, node=node, app=self.app)
        self.tree.add_node(b, treenode)

        for child in node.children:
            self.recursive_insert(child, b)

    def refresh(self, *l):
        for node in self.tree.root.nodes:
            self.tree.remove_node(node)

        self.recursive_insert(self.app.playground.root, self.tree.root)
