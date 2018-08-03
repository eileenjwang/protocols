from app.main.utils import get_config_json, get_random_password, get_username_for_node
from app.models import User, Role, user_manager
from app import db
from flask import current_app

def find_user_node(username, tree):
    def _recursive_find_user_node(username, node):
        if node.is_root_leaf:
            node_username = get_username_for_node(node)
            if node_username == username:
                return node
        else:
            for child in node.children:
                item = _recursive_find_user_node(username, child)
                if item:
                    return item

    node = _recursive_find_user_node(username, tree.root)
    return node


def update_users(tree):
    config = get_config_json()
    username_field = config['username_field']
    email_field = config['email_field']
    user_list = []

    def _get_role(node):
        level = node.level
        while level != 1:
            node = node.parent
            level = node.level
        return node.label

    def _recursive_find_users_helper(user_list, node):
        if node.is_root_leaf:
            username = None
            email = None
            for child in node.children:
                if child.label == username_field:
                    username = child.leaf_content
                elif child.label == email_field:
                    email = child.leaf_content


            if username and email and isinstance(username, str) and isinstance(email, str):
                role = _get_role(node)
                user = (username, email, role)
                print("Found user", user)
                return user
        else:
            if not node.is_leaf:
                items = []
                for child_node in node.children:
                    user = _recursive_find_users_helper(items, child_node)
                    if user:
                        items.append(user)
                user_list.extend(items)

    _recursive_find_users_helper(user_list, tree.root)
    # print(user_list)
    roles = {}
    for username, email, role in user_list:
        if role not in roles:
            user_role = Role.query.filter(Role.name).one_or_none()
            if not user_role:
                user_role = Role(name=role)
                db.session.add(user_role)
                db.session.commit()

            roles[role] = user_role
        # print(username, email, role)
        # check if username exists
        user = User.query.filter(User.username == username).one_or_none()
        print(username, email)
        if user:
            db.session.delete(user)
            db.session.commit()



        # if user does not exist, create a user with a tmp password
        tmp_password = get_random_password()
        hash_password = user_manager.hash_password(tmp_password)
        user = User(username=username, email=email, tmp_password=tmp_password, password=hash_password, reinitialise=False)

        # user.tmp_password = tmp_password
        # user.set_password(tmp_password)
        if role in roles.keys():
            user.roles = [user_role,]
        db.session.add(user)
        db.session.commit()
