from flask_wtf import FlaskForm
from wtforms import SubmitField, TextField, FormField, FieldList, RadioField
from wtforms.validators import DataRequired

from app.main.utils import slugify, camelify

class DataTree:     

    def __init__(self, json_data):  
        self.json_data = json_data
        self.index = {}
        self.root = DataTree.json_to_graph(self.json_data, parent=None, tree=self, keys=[])

    @staticmethod
    def json_to_graph(json_data, root_level=0, is_parent_leaf=False, prefix='', parent=None, tree=None, keys=[]):
        """Converts json object into graph object that is easier to traverse and output in template.

        Args:
            json_data (dict): the json data (dict of dicts of dicts ... of dicts (depth of n))

        Returns:
            json_tree (list): list of nodes (dict) of the form
                [ 
                    {
                        'id': <str>, 
                        'label': <str>, 
                        'level': <int>,
                        'children': <list>, 
                        'is_leaf': <bool>, 
                        'leaf_type': <str>,
                        'leaf_content': <str>
                    },
                    ...
                ]
                such that:
                    id (str): unique to the node
                    label (str): the node label (corresponds to dictionary key)
                    children (list): list of child nodes
                    is_leaf (bool): True if node correponds to the level that must be output in form format 
                        (not necessarily the last level of the dict), False if corresponds to accordion header
                    leaf_type (str): One of ['str', 'bool', 'list', 'dict', None]
                        None if is_leaf is False
                        Examples of (key, value) pairs according to leaf_type:
                            'str': 
                                "Antenne": "head coil"
                            'bool':
                                "Implantation": true
                            'dict': 
                                "Injection": {
                                    "aucune": true,
                                    "pré_scan": false,
                                    "per_scan": false
                                   }
                            'list':
                                "Séquences": [
                                    {
                                     "Nom": "T1 AXIAL",
                                     "Durée": "00:03:45"
                                    },
                                    {
                                     "Nom": "FLAIR AXIAL",
                                     "Durée": "00:04:02"
                                    }
                                   ]
        """
       
        # first survey

        level = root_level
        for key, node_data in json_data.items():
            keys = list(keys)
            keys.append(key)

            node_id = '{prefix}_{level}-{slug}'.format(
                prefix=prefix, 
                level=level,
                slug=slugify(key))
            node_id = node_id.strip('_')

            is_root_leaf, is_leaf, is_terminal_leaf, is_child_leaf = False, False, False, False

            if is_parent_leaf:
                is_leaf = True
                is_child_leaf = True
            elif DataTree.is_leaf(key, node_data):
                is_leaf = True
                is_root_leaf = True

            leaf_type = None
            leaf_content = None
            if is_leaf:
                leaf_type = type(node_data).__name__
                if isinstance(node_data, bool) or isinstance(node_data, str):
                    leaf_content = node_data
                    is_terminal_leaf = True

            node_kwargs = {
                'id': node_id,
                'parent': parent,
                'label': key,
                'level': level,
                'is_leaf': is_leaf,
                'leaf_type': leaf_type,
                'leaf_content': leaf_content,
                'is_root_leaf': is_root_leaf,
                'is_terminal_leaf': is_terminal_leaf,
                'is_child_leaf': is_child_leaf,
                'tree': tree,
                'keys': keys
            }
            node = DataNode(**node_kwargs)

            # add child nodes in recursive fashion
            children = []
            if isinstance(node_data, dict):
                for child_key, child_node_data in node_data.items():
                    child_dict = {child_key: child_node_data}
                    children.append(
                        DataTree.json_to_graph(
                            child_dict, 
                            root_level=level+1, 
                            prefix=node_id,
                            is_parent_leaf=is_leaf,
                            parent=node,
                            tree=tree,
                            keys=keys,
                        )
                    )

            if isinstance(node_data, list):
                for child_node_data in node_data:
                    child_dict = { 'list' : child_node_data}
                    children.append(
                        DataTree.json_to_graph(
                            child_dict, 
                            root_level=level+1, 
                            is_parent_leaf=is_leaf,
                            prefix=node_id,
                            parent=node,
                            tree=tree,
                            keys=keys
                        )
                    )

            node.children = children
            return node

    @staticmethod
    def is_leaf(key, value):
        """
        Predefined manner to determine if node is leaf (can be changed if we decide to change the schema in the future).
        """
        rvalue = isinstance(value, dict) and len(value.items()) > 1 and 'SALLE' in key
        return rvalue

class DataNode:

    def __init__(self, 
            parent=None, 
            id='0', 
            label='Unknown', 
            level=0,
            children = [],
            is_leaf = False,
            leaf_type = 'Unknown',
            leaf_content = 'No content',
            is_root_leaf = False,
            is_terminal_leaf = False,
            is_child_leaf = False,
            tree = None,
            keys = [],
            ):
        self.parent = parent
        self.id = id
        self.label = label
        self.level = level
        self.children = children
        self.is_leaf = is_leaf
        self.leaf_type = leaf_type
        self.leaf_content = leaf_content
        self.is_root_leaf = is_root_leaf
        self.is_terminal_leaf = is_terminal_leaf
        self.is_child_leaf = is_child_leaf
        self.tree = tree
        self.keys = keys
        self.index = {}
        self.form_classes = {}

        if tree:
            tree.index[id] = self

    def __str__(self):
        return DataNode.node_to_str(self.tree)

    def to_dict(self, form=None):
        """TODO"""
        if not form:
            form, _ = self.get_form(fill_data=True)

        def rebuild(node, index):
            if isinstance(node, str):
                pass

            elif isinstance(node, dict):
                nodes = list(node.items())
                for key, val in nodes:
                    if key not in index.keys():
                        del node[key]
                        continue

                    new_key = index[key]
                    if new_key != key:
                        node[new_key] = val
                        del node[key]

                    if val == 'Oui':
                        node[new_key] = True
                    elif val == 'Non':
                        node[new_key] = False
                    else:
                        rebuild(val, index)

            elif isinstance(node, list):
                for item in node:
                    rebuild(item, index)

        d = dict(form.data.items())
        rebuild(d, self.index)
        return d

    def get_key_path(self):
        return self.keys

   
    @staticmethod
    def node_to_str(node, level=0):
        if node.is_leaf and (node.leaf_type == 'str' or node.leaf_type == 'bool'):
            content = '{indent}* {node_label}:{node_content}'.format(
                  indent = '  ' * node.level,
                  node_label = node.label,
                  node_content = node.leaf_content
                )
        else:
            children_content = '\n'.join([DataNode.node_to_str(child, level=node.level) for child in node.children])
            content = '{indent}{node_id}\n{node_content}'.format(
              level = node.level,
              indent = '  ' * node.level,
              node_id = node.id,
              node_content = children_content
            )
        return content


    def get_form_class_for_attr(self, attr, form_prefix=''):
        class_name = form_prefix + attr + 'Class'

        if class_name not in self.form_classes.keys():
            form_class = type(class_name, (DynamicChildForm,), {})
        
        self.form_classes[attr] = form_class
        return form_class


    def get_form(self, fill_data=False, form_prefix=''):
        form_field_info = []

        priority = { 'str': 0, 'bool': 1, 'dict': 2, 'list': 3 }
        for node in sorted(self.children, key=lambda x: priority[x.leaf_type]):
            field_label = node.label
            attr = camelify(field_label)
            field_id = slugify(field_label)
            sub_form_class = None
            content = None

            self.index[attr] = field_label

            if node.leaf_type == 'str':
                # define form attribute (field)
                DynamicForm.append_field(attr, TextField(node.label, validators=[DataRequired()], id=field_id))
            elif node.leaf_type == 'bool':
                DynamicForm.append_field(attr, RadioField(choices=[(True, 'Oui'), (False, 'Non')], id=field_id))

            elif node.leaf_type == 'dict':
                sub_form_class = self.get_form_class_for_attr(attr)
                # sub_form_class = type(attr + 'Class', (DynamicForm,), {})
                for child in node.children:
                    child_attr = camelify(child.label)
                    self.index[child_attr] = child.label
                    child_field_id = slugify(child.label)
                    sub_form_class.append_field(child_attr, TextField(child.label, validators=[DataRequired()], id=child_field_id))
                DynamicForm.append_field(attr, FormField(sub_form_class, id=field_id))
            
            elif node.leaf_type == 'list':
                first_list = node.children[0]
                sub_form_class = self.get_form_class_for_attr(attr)

                for child in first_list.children:
                    child_attr = camelify(child.label)
                    self.index[child_attr] = child.label
                    child_field_id = slugify(child.label)
                    sub_form_class.append_field(child_attr, TextField(child.label, validators=[DataRequired()], id=child_field_id))
                DynamicForm.append_field(attr, FieldList(FormField(sub_form_class, id=field_id)))
            

            form_field_info.append(
                {
                    'node': node,
                    'attr': attr,
                    'sub_form_class': sub_form_class,
                    # 'content': content,
                    # 'field_obj': field_obj
                })

        form = DynamicForm()

        # define field values
        if fill_data:
            for field_d in form_field_info:
                attr = field_d['attr']
                node = field_d['node']
                sub_form_class = field_d['sub_form_class']
                if node.leaf_type == 'str':
                    getattr(form, attr).data = node.leaf_content
                if node.leaf_type == 'bool':
                    if node.leaf_content == 'Oui':
                        getattr(form, attr).data = True
                    elif node.leaf_content == 'Non':
                        getattr(form, attr).data = False
                    elif node.leaf_content in [True, False]:
                        getattr(form, attr).data = node.leaf_content

                elif node.leaf_type == 'dict':
                    for child in node.children:
                        child_attr = camelify(child.label)
                        getattr(getattr(form, attr), child_attr).data = child.leaf_content

                elif node.leaf_type == 'list':
                    field_list = getattr(form, attr)
                    create_entries = len(field_list.entries) == 0
                    
                    for i, node_list in enumerate(node.children):
                        child_form = sub_form_class()
                        for child in node_list.children:
                            child_attr = camelify(child.label)
                            setattr(child_form, child_attr, child.leaf_content)
                        if create_entries:
                            print('Create entry', i)
                            field_list.append_entry(child_form)
                        # else:
                        #     print('No need to create entry', i)
                        #     field_list.entries[i] = child_form

        return (form, self.index)

class BaseForm(object):
    @classmethod
    def append_field(cls, name, field):
        if not hasattr(cls, name):
            setattr(cls, name, field)
        return cls

class DynamicForm(FlaskForm, BaseForm):
    class Meta:
        crsf = False

class DynamicChildForm(FlaskForm, BaseForm):
    class Meta:
        crsf = False
