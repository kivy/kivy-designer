from kivy.uix.widget import Widget


class TreeException(Exception):
    pass


class TreeNode(object):
    '''TreeNode class for representing information of Widgets
    '''

    def __init__(self):
        super(TreeNode, self).__init__()

        self.parent_node = None
        self.list_children = []
        self.class_name = ''
        self.base_class_name = ''
        self.is_subclassed = False
        self.widget = None


class Tree(object):
    '''Tree class for saving all the information regarding widgets
    '''

    def __init__(self):
        super(Tree, self).__init__()

        self.list_root_nodes = []

    def insert(self, widget, parent=None):
        '''inserts a new node of widget with parent.
           Returns new node on success
        '''

        if not isinstance(widget, Widget):
            TreeException('Tree accepts only Widget to be inserted')

        if parent is None:
            node = TreeNode()
            node.widget = widget
            self.list_root_nodes.append(node)
            return node

        if not isinstance(parent, Widget):
            TreeException('Tree only accepts parent to be a Widget')

        parent_node = self.get_node_for_widget(parent)
        node = TreeNode()
        node.widget = widget
        node.parent_node = parent_node
        if parent_node is None:
            self.list_root_nodes.append(node)
        else:
            parent_node.list_children.append(node)
        return node

    def _get_node_for_widget(self, widget, node):
        if node.widget == widget:
            return node

        for _node in node.list_children:
            node_found = self._get_node_for_widget(widget, _node)
            if node_found is not None:
                return node_found

        return None

    def get_node_for_widget(self, widget):
        '''Returns node for widget, None if not found
        '''
        for _root in self.list_root_nodes:
            node = self._get_node_for_widget(widget, _root)
            if node is not None:
                return node

        return None

    def traverse_tree(self, node=None):
        '''Traverse the tree, and run traverse code for every node
        '''
        if node is None:
            for _node in self.list_root_nodes:
                self.traverse_tree(_node)
        else:
            # Add traverse code here
            for child in node.list_children:
                self.traverse_tree(child)

    def delete(self, widget):
        '''deletes a node of widget from the Tree.
           Returns that node on deletion
        '''
        if not isinstance(widget, Widget):
            TreeException('Tree accepts only Widget to be deleted')

        node = self.get_node_for_widget(widget)
        if node in self.list_root_nodes:
            self.list_root_nodes.remove(node)
        else:
            node.parent_node.list_children.remove(node)
        return node
