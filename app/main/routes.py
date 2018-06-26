from flask import render_template, flash, redirect, url_for, request, g, current_app
from flask_login import current_user, login_required
from app import db
from app.main.forms import EditProfileForm
from app.models import User
from app.main import bp


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/', methods=['GET', 'POST'])
@login_required
def index():
#######
    import json

    import numpy as np
    import pandas as pd

    file = 'data.json'

    with open(file) as f:
        json_file = f.read()
        data = json.loads(json_file)

    many_keys = []
    for k,v in data['IRM'].items(): # neuroradio, et abdo pelvi
        for k1, v1 in v.items():
            for k2, v2 in v1.items():
                many_keys.append(k2)
    many_keys = many_keys[0:4]
##########
    return render_template('index.html', title='Accueil', many_keys = many_keys)


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
