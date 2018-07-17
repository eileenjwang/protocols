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


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index/', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def index():
    conn = sql.connect('protocols.db', timeout=10)
    c = conn.cursor()
    # create table
    c.execute('CREATE TABLE IF NOT EXISTS Protocols (version_id INTEGER PRIMARY KEY, user, timestamp, JSON_text TEXT)')
    file = 'data.json'
    with open(file) as f:
        json_file = f.read()
    #data = json.loads(json_file)
    #textfile = json.dumps(data)
    now = str(datetime.datetime.now())
    user = str(current_user)
    #c.execute("INSERT INTO Protocols (user, timestamp, JSON_text) VALUES (?,?,?)",
            #(user, now, json_file,))
    # Save (commit) the changes
    conn.commit()
    # close connection
    conn.close()

    with sql.connect("protocols.db") as con:
        cur = con.cursor()
        cur.execute("SELECT JSON_text FROM Protocols ORDER BY version_id DESC LIMIT 1")
        rows = cur.fetchall()

    import uuid
    count = 0
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
                        count +=1
                        dict_5 = dict(name=k5, id= count, list=[])
                        dict_4['list'].append(dict_5)
                        for k6, v6 in v5.items():
                            dict_6 = dict(name=k6, id= uuid.uuid4(), list=[])
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

@bp.route('/edit_protocols/<int:id>', methods=['GET', 'POST'])
@csrf.exempt
@login_required
def edit_protocols(id):
    #create database that stores data[][][]...
    import sqlite3 as sql
    with sql.connect("protocols.db") as con:
        cur = con.cursor()
        cur.execute("SELECT JSON_text FROM Protocols ORDER BY version_id DESC LIMIT 1")
        rows = cur.fetchall()
    import uuid
    count = 0
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
                        count +=1
                        dict_5 = dict(name=k5, id= count, list=[])
                        dict_4['list'].append(dict_5)
                        for k6, v6 in v5.items():
                            dict_6 = dict(name=k6, id= uuid.uuid4(), list=[])
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

    index_dict = []
    for ele1 in dicts_all:
        for ele2 in ele1["list"]:
            for ele3 in ele2["list"]:
                for ele4 in ele3["list"]:
                    for ele5 in ele4['list']:
                        hello = "data['IRM'][{}][{}][{}][{}][{}]".format(ele1['name'], ele2['name'], ele3['name'], ele4['name'], ele5['name'])
                        index_dict.append(hello)

    with sql.connect('indexing.db', timeout=10) as conn:
        c = conn.cursor()
        # create table
        c.execute('CREATE TABLE IF NOT EXISTS index_dict (id INTEGER PRIMARY KEY, indexing)')
        ########DO THIS CODE THE FIRST TIME#####
        #for element in index_dict:
            #c.execute("INSERT INTO index_dict (indexing) VALUES (?)",(element,))
        c.execute("SELECT indexing FROM index_dict WHERE id=?", (id,))
        row = c.fetchone()
        #print(row[0])

    import re
    contents = re.findall("\[(.*?)\]", row[0])
    #data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5])

    #form
    form = EditProtocolsForm(meta={'csrf': False})
    if request.method == 'POST': #and form.validate()#
        del form.submit
        data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5]).update(form.data)
        textfile = json.dumps(data)
        now = str(datetime.datetime.now())
        user = str(current_user)
        con = sql.connect("protocols.db")
        cur = con.cursor()
        cur.execute("INSERT INTO Protocols (user, timestamp, JSON_text) VALUES (?,?,?)",
            (user, now, textfile,))
        con.commit()
        con.close()
        flash('Vos changements ont été enregistrés.')
        return redirect(url_for('main.index'))
    elif request.method == 'GET':
        form.Implantation.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Implantation")
        form.InstallationPatient.Durée.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("InstallationPatient", {}).get('Durée')
        form.Antenne.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Antenne")
        ### partially hard-coded for class Séquences
        dict_sequences=[]
        dict_sequences.append(data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[0])
        dict_sequences.append(data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[1])
        for element in range(0,len(dict_sequences)):
            childform = sub_Séquences()
            childform.Nom = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[element]['Nom']
            childform.Durée = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Séquences")[element]['Durée']
            form.Séquences.append_entry(childform)
        ### Injection
        form.Injection.Contraste.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Injection", {}).get("Contraste")
        form.Injection.pré_scan.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Injection", {}).get("pré_scan")
        form.Injection.per_scan.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Injection", {}).get("per_scan")
        ###
        form.Protocole_machine.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Protocole_machine")
        form.Durée_acquisition.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Durée_acquisition")
        form.Durée_examen.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Durée_examen")
        form.Durée_bloc_irm.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Durée_bloc_irm")
        form.Date_création.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Date_création")
        form.Date_dernière_modification.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Date_dernière_modification")
        form.Auteur.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Auteur")
        form.Statut.Production.data = data.get('IRM', {}).get(contents[1], {}).get(contents[2], {}).get(contents[3], {}).get(contents[4], {}).get(contents[5], {}).get("Statut", {}).get("Production")

    return render_template('edit_protocols.html', form=form)
