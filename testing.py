import json

import numpy as np
import pandas as pd

file = 'data.json'

with open(file) as f:
    json_file = f.read()
    data = json.loads(json_file)

class Group():
    for k,v in data['IRM'].items(): # neuroradio, et abdo pelvi
        for k1, v1 in v.items():
            for k2, v2 in v1.items():
                return k2


{% extends "base.html" %}
{% import 'bootstrap/wtf.html' as wtf %}


{% block app_content %}
    <h1>Hello, {{ current_user.username }}.</h1>
    <br>

    <!DOCTYPE html>
    <html>
    <head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
      <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.3.1/jquery.min.js"></script>
      <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/js/bootstrap.min.js"></script>
    </head>

    <body>

    <div class="container">
      <h2>Simple Collapsible</h2>
      <p>Click on the button to toggle between showing and hiding content.</p>
      {% for items in many_keys %}
        <button type="button" class="btn btn-info" data-toggle="collapse" data-target="#demo"> {{items}}</button>
        <div id="demo" class="collapse in">
            {{items}}
        </div>
        {% endfor %}
    </div>

    </body>
    </html>

{% endblock %}
