from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm, EditProtocolsForm, sub_Séquences
from app.models import User
from app.main import bp
import sqlite3 as sql
import json
import datetime, time
from app import csrf
import re
from pprint import pprint
import unidecode
import uuid
from wtforms import StringField, SubmitField, TextField, FormField, FieldList
from wtforms.validators import ValidationError, DataRequired
from flask_wtf import FlaskForm

class DataTree:     

    def __init__(self, json_data):  
        self.json_data = json_data
        self.index = {}
        self.root = DataTree.json_to_graph(self.json_data, parent=None, tree=self)

    @staticmethod
    def json_to_graph(json_data, root_level=0, is_parent_leaf=False, prefix='', parent=None, tree=None):
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
       
        level = root_level
        for key, node_data in json_data.items():
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
                # 'html_id': uuid.uuid4(),
                'is_child_leaf': is_child_leaf,
                'tree': tree
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
                            tree=tree
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
                            tree=tree
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

# class BaseClass(object):
#     def __init__(self, classtype):
#         self._type = classtype

class DynamicForm(FlaskForm):
    class Meta:
        crsf = False

    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls


class DynamicDictForm(FlaskForm):
    class Meta:
        crsf = False

    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls

# def FormFactory(name, argnames, BaseClass=DynamicForm):
#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             # here, the argnames variable is the one passed to the
#             # ClassFactory call
#             if key not in argnames:
#                 raise TypeError("Argument %s not valid for %s" 
#                     % (key, self.__class__.__name__))
#             setattr(self, key, value)
#             value.bind(self, key)
#             print('setting attribute', key, value)

#         BaseClass.__init__(self)

#     newclass = type(name, (BaseClass,),{"__init__": __init__})
#     newclass.meta = None
#     return newclass

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
            tree = None
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
        if tree:
            tree.index[id] = self

    def __str__(self):
        return DataNode.node_to_str(self.tree)

    def to_dict(self):
        """TODO"""
        d = {self.label: {}}

    @staticmethod
    def node_to_dict(node):
        """TODO"""
        if not node.is_leaf:
            subdict = {}
            for child in node.children:
                subdict[child.label] = DataNode.node_to_dict(child)
            return subdict
        else:
            if len(node.children) == 0:
                d = {node.label : node.leaf_content}
                return d
            # TODO handle the rest...
   
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

    def get_form(self):
        form_field_info = []


        for node in self.children:
            field_label = node.label
            attr = camelify(field_label)
            content = None

            if node.leaf_type == 'str' or node.leaf_type == 'bool':
                # define form attribute (field)
                DynamicForm.append_field(attr, TextField(node.label, validators=[DataRequired()]))

            elif node.leaf_type == 'dict':
                for child in node.children:
                    child_attr = camelify(child.label)
                    DynamicDictForm.append_field(child_attr, TextField(child.label, validators=[DataRequired()]))
                DynamicForm.append_field(attr, FormField(DynamicDictForm))
            
            form_field_info.append(
                {
                    'node': node,
                    'attr': attr,
                    # 'content': content,
                    # 'field_obj': field_obj
                })
        DynamicForm.append_field('submit', SubmitField('Soumettre'))

        # submit = SubmitField('Soumettre')
        form = DynamicForm()

        # define field values
        for field_d in form_field_info:
            attr = field_d['attr']
            node = field_d['node']
            if node.leaf_type == 'str' or node.leaf_type == 'bool':
                getattr(form, attr).data = node.leaf_content

            elif node.leaf_type == 'dict':
                for child in node.children:
                    child_attr = camelify(child.label)
                    print('** dict data', getattr(getattr(form, attr), child_attr))
                    getattr(getattr(form, attr), child_attr).data = child.leaf_content

        return form

def get_json_data():
    with sql.connect("protocols.db") as con:
        cur = con.cursor()
        cur.execute("SELECT JSON_text FROM Protocols ORDER BY version_id DESC LIMIT 1")
        rows = cur.fetchall()
    return json.loads(rows[0][0])


def camelify(s):
    """
    Simplifies strings into CamelCase strings
    """
    # remove accents
    s = unidecode.unidecode(s)
    s = ''.join(x for x in s.title() if not x.isspace())
    s = s.replace(':', '')
    s = s.replace('.', '')
    return s

def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.
    >>> print slugify("[Some] _ Article's Title--")
    some-articles-title
    source: https://blog.dolphm.com/slugify-a-string-in-python/
    """

    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')

    # "[some]___article's_title__"
    # "some___articles_title__"
    s = re.sub('\W', '', s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace('_', ' ')

    # "some   articles title  "
    # "some articles title "
    s = re.sub('\s+', ' ', s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(' ', '-')

    # remove accents
    s = unidecode.unidecode(s)

    return s

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def index():
    
    json_data = get_json_data()
    tree_obj = DataTree(json_data)

    return render_template('index.html', title='Accueil', protocols=[tree_obj.root])


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Vos changements ont été enregistrés.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Modifier votre profil',
                           form=form)

@bp.route('/edit_protocols/<id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def edit_protocols(id):

    json_data = get_json_data()
    tree_obj = DataTree(json_data)

    form_node = tree_obj.index[id]

    if request.method == 'GET':
        form = form_node.get_form()
        print('Fields: ')
        for field in form:
            print(field)
        print(form.data)

        # for node, field_attribute in form_field_info:
        #     field = getattr(form, field_attribute)
        #     field.data = node.leaf_content

    # if request.method == 'POST': #and form.validate()#
    #     pass
    #     # del form.submit
    #     # data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5]).update(form.data)
    #     # textfile = json.dumps(data)
    #     # now = str(datetime.datetime.now())
    #     # user = str(current_user)
    #     # con = sql.connect("protocols.db")
    #     # cur = con.cursor()
    #     # cur.execute("INSERT INTO Protocols (user, timestamp, JSON_text) VALUES (?,?,?)",
    #     #     (user, now, textfile,))
    #     # con.commit()
    #     # con.close()
    #     # flash('Vos changements ont été enregistrés.')
    #     # return redirect(url_for('main.index'))

    # elif request.method == 'GET':
    #     for field in form:
    #         field.data = 
    #     form.Implantation.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Implantation")
    #     form.InstallationPatient.Durée.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("InstallationPatient", {}).get('Durée')
    #     form.Antenne.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Antenne")
    #     ### partially hard-coded for class Séquences
    #     dict_sequences=[]
    #     dict_sequences.append(data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[0])
    #     dict_sequences.append(data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[1])
    #     for element in range(0,len(dict_sequences)):
    #         childform = sub_Séquences()
    #         childform.Nom = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[element]['Nom']
    #         childform.Durée = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[element]['Durée']
    #         form.Séquences.append_entry(childform)
    #     ### Injection
    #     form.Injection.Contraste.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Injection", {}).get("Contraste")
    #     form.Injection.pré_scan.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Injection", {}).get("pré_scan")
    #     form.Injection.per_scan.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Injection", {}).get("per_scan")
    #     ###
    #     form.Protocole_machine.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Protocole_machine")
    #     form.Durée_acquisition.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Durée_acquisition")
    #     form.Durée_examen.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Durée_examen")
    #     form.Durée_bloc_irm.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Durée_bloc_irm")
    #     form.Date_création.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Date_création")
    #     form.Date_dernière_modification.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Date_dernière_modification")
    #     form.Auteur.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Auteur")
    #     form.Statut.Production.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Statut", {}).get("Production")

    title = 'Modifier protocole {}'.format(form_node.label)
    return render_template('edit_protocols.html', form=form, title=title)
    # return render_template('index.html', title='Form ' + form_node['label'], protocols=[form_node])

