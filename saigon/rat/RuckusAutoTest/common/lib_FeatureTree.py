"""
The FeatureTree is the implementation of Feature Update Index Tree based on
Tree data structure. It provides the facilities to build a tree with a
tree nodes structure, either by default or as an input parameter, and to
iterate path from root node to a child node which has the desired value.

NOTES:
- Each node in a tree has zero or more child nodes.
- A node that has a child is called the child's parent node.
- A node has at most one parent.
- The topmost node in a tree is called the root node. Being the topmost node,
the root node will not have parents.

The code requires the Python package Pynu - Python Node Utilities installed.
Source: http://pypi.python.org/pypi/Pynu
"""
import re
from pynu.tree import TreeNode


class FeatureTree(object):
    def __init__(self, nodes_level):
        self.root = None
        self.create_tree(nodes_level)


    def create_tree(self, nodes_level):
        '''
        creates a tree with the tree nodes structure specified.
        uses nodes_level as the default if nothing given.
        '''
        for level in nodes_level.iterkeys():
            parents_list = nodes_level[level].iterkeys()

            parent_node = None
            for parent in parents_list:
                # 'root'
                if parent == 'root':
                    value = nodes_level[level][parent][0] #'8.0.0.0'
                    parent_node = self._create_node(value)

                    self.root = parent_node

                # '8.0.0.0'
                else:
                    parent_node = self.root.children.find(value='^%s$' % parent)
                    # when root node created yet has no child
                    if parent_node == None:
                        parent_node = self.root

                    for value in nodes_level[level][parent]:
                        parent_node.children.append(self._create_node(value))


    def _create_node(self, value):
        '''
        creates a node with the given value.
        each node has its value and name, although node.name is not used
        '''
        node = TreeNode()
        node.value = value
        node.name = '_'.join(['node', value])

        return node


    def iterate_path(self, value):
        '''
        iterates the path from root node to node with value specified
        '''
        node = self.root.children.find(value='^%s$' % value)
        path = [node]

        try:
            for _node in node.parent.find():
                path.append(_node)

        except:
            path.append(self.root)

        while path:
            yield path.pop()


    def print_tree(self):
        '''
        tests TreeNode.walk()
        '''
        for i, node in enumerate(self.root.walk()):
            print(i, node, node.value, node.name)


def tst():
    ft_dict = \
    dict(# top level, contains root node '9.5.0.0'
         level0={'root': ['9.5.0.0']},
         level1 = {'9.5.0.0': ['9.6.0.0', '9.5.1.0', '9.5.2.0', '9.5.3.0']},
         level2 = {'9.6.0.0': ['9.7.0.0', '9.6.1.0', '9.6.2.0', '9.6.3.0']},
         level3 = {'9.7.0.0': ['9.8.0.0', '9.7.1.0', '9.7.2.0', '9.7.3.0']},
         level4 = {'9.8.0.0': ['9.9.0.0', '9.8.1.0', '9.8.2.0', '9.8.3.0']},
         level5 = {'9.9.0.0': ['10.0.0.0', '9.9.1.0', '9.9.2.0', '9.9.3.0','9.9.0.99','9.10.0.0']},
         level6 = {'10.0.0.0': ['10.1.0.0', '10.0.1.0', '10.0.2.0', '10.0.3.0']},
    )   
    #updated by jluh 2013-10-29
    #0.0.0.99 will follow the last version.
    first_num = True
    comp_num = ''
    for num in ft_dict.keys():    
        if first_num:
            comp_num = int(re.findall(r'level(\d+)', num)[0])
            first_num = False
            continue
        if comp_num < int(re.findall(r'level(\d+)', num)[0]):
            comp_num = int(re.findall(r'level(\d+)', num)[0])
            
    last_ver_key = u'level' + str(comp_num)
    ft_dict[last_ver_key][ft_dict[last_ver_key].keys()[0]].append('0.0.0.99')
    
    #generate the feature tree.    
    ft = FeatureTree(ft_dict)

    ft.print_tree()
    print('complete!!!\n')


if __name__ == "__main__":
    tst()
