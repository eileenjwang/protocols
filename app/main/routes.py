from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User
from app.main import bp
import sqlite3 as sql
import json

@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
#######
    # import json
    # file = 'data.json'
    # with open(file) as f:
        # json_file = f.read()
        # data = json.loads(json_file)
    with sql.connect("protocols.db") as con:
        cur = con.cursor()
        cur.execute("SELECT JSON_text FROM Protocols ORDER BY version_id DESC LIMIT 1")
        rows = cur.fetchall()

    import uuid

    dicts_all = []
    data = json.loads(rows[0][0])
    for k1, v1 in data['IRM'].items():
        dict_1 = dict(name= k1, id= uuid.uuid4(), list=[])
        for k2, v2 in v1.items():
            dict_2 = dict(name=k2, id= uuid.uuid4(), list=[])
            dict_1['list'].append(dict_2)
            for k3, v3 in v2.items():
                dict_3 = dict(name=k3, id= uuid.uuid4(), list=[])
                dict_2['list'].append(dict_3)
                for k4, v4 in v3.items():
                    dict_4 = dict(name=k4, id= uuid.uuid4(), list=[])
                    dict_3['list'].append(dict_4)
                    for k5, v5 in v4.items():
                        dict_5 = dict(name=k5, id= uuid.uuid4(), list=[])
                        dict_4['list'].append(dict_5)
                        for k6, v6 in v5.items():
                            dict_6 = dict(name=k6, id= k6, list=[])
                            if isinstance(v6, (str, int, bool)):
                                dict_6['list'].append(v6)
                                dict_5['list'].append(dict_6)
                            if isinstance(v6, dict):
                                for k7, v7 in v6.items():
                                    dict_7 = dict(name=k7, id= uuid.uuid4(), list=[])
                                    dict_6['list'].append(dict_7)
                                    dict_7['list'].append(v7)
                                dict_5['list'].append(dict_6)
                            if isinstance(v6, list):
                                for element in v6:
                                    for key1, value1 in element.items():
                                        dict_7 = dict(name=key1, id= uuid.uuid4(), list=[])
                                        dict_6['list'].append(dict_7)
                                        dict_7['list'].append(value1)
                                dict_5['list'].append(dict_6)

        dicts_all.append(dict_1)
##########
    return render_template('index.html', title='Accueil', dicts_all=dicts_all)


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
