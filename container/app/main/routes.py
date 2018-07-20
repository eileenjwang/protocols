from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required

import sqlite3 as sql
import json
import datetime, time

from app import db
from app.models import User
from app.main import bp
from app import csrf
from app.main.graph_models import DataTree
from app.main.utils import get_json_data

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/', methods=['GET', 'POST'])
# @login_required
@csrf.exempt
def index():

    json_data = get_json_data(current_app)
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
    return render_template('edit_profile.html', title='Modifier votre profil', form=form)

@bp.route('/edit_protocols/<id>', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def edit_protocols(id):

    json_data = get_json_data(current_app)
    tree_obj = DataTree(json_data)

    form_node = tree_obj.index[id]
    title = 'Modifier protocole {}'.format(form_node.label)

    if request.method == 'GET':
        form = form_node.get_form(fill_data=True)

        return render_template('edit_protocols.html', form=form, title=title)

    elif request.method == 'POST':
        form = form_node.get_form(fill_data=False)

        new_json_subdata = form_node.to_dict(form=form)
        keys = form_node.get_key_path()

        # update subset of json_data and build new_json_data
        new_json_data = dict(json_data.items())
        d = new_json_data
        for k in keys[:-1]:
            d = d[k]
        d[keys[-1]] = new_json_subdata

        # save new version to db
        with sql.connect(current_app.config.get('PROTOCOLS_DB')) as con:
            cur = con.cursor()
            json_str = json.dumps(new_json_data)
            now = str(datetime.datetime.now())
            user = str(current_user)
            cur.execute("INSERT INTO Protocols (user, timestamp, JSON_text) VALUES (?,?,?)",
                (user, now, json_str,))
            con.commit()

        flash('Vos changements ont été enregistrés.')
        return redirect(url_for('main.index'))
