import os
from dotenv import load_dotenv
import requests
from pprint import pprint
import base64
import json
from github import Github
from flask import Flask, request, jsonify, render_template, Response
import pandas as pd
import numpy as np
from pprint import pformat
import plotly
import plotly.express as px
import chart_studio.plotly as py
import plotly.graph_objects as go
# current app ppints to config in app.py
from flask import Blueprint, jsonify, request, render_template, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from web_app.models import db, migrate, User, Repos
from web_app.services import github_api_client
from web_app.graphs import create_graph, issues_graph, merge_fraction, code_frequency

load_dotenv()

# can make client global variable if you want to
client = github_api_client()

#
#
# -----ROUTING-----
#
#

# specifying for Blueprint to be used in app.py
my_routes = Blueprint('my_routes', __name__)

@my_routes.route("/")
def index():
    return render_template("homepage.html")

@my_routes.route("/ds")
def ds_index():
    return render_template("ds.html")


# gathering all the repos and displaying what is stored in the Repos database
@my_routes.route("/ds/repos")
@my_routes.route("/ds/repos.json")
def repos():
    repos = Repos.query.all()
    #print(len(users))
    print(type(repos))
    print(type(repos[0]))
    repos_response = []
    for repo in repos:
        repos_dict = repo.__dict__
        del repos_dict["_sa_instance_state"]
        repos_response.append(repos_dict)
    return jsonify(repos_response)

# user is able to input reposiotry names and they'll be added to the Repos database
@my_routes.route("/ds/repos/add", methods=["POST"])
def add_repos():
    print("ADD A NEW REPO....")
    print("FROM DATA:", dict(request.form)) # detects what information was sent to server when a POST request was made
    # something
    # return jsonify({"message": "CREATED OK"})
    if "repo" in request.form:
        repo = request.form["repo"]
        print(repo)
        db.session.add(Repos(repo=repo))
        db.session.commit()
        return jsonify({"message": "CREATED OK", "repo": repo})
    else:
        return jsonify({"message": "OOPS PLEASE SPECIFY A REPOSITORY!"})

# ------- repo commit response --------
@my_routes.route('/repos/commits', methods=['GET', 'POST'])
def commits():
    # user inputs repo name
    ui_commit = request.form['repo_commits']
    URL = f"https://api.github.com/repos/{ui_commit}/commits?per_page=100"
    response = requests.get(URL)
    data = response.json()
    data = pformat(data)
    return data

@my_routes.route('/repos/comments', methods=['GET', 'POST'])
def comments():
    # user inputs repo name
    ui_comments = request.form['repo_comments']
    URL = f"https://api.github.com/repos/{ui_comments}/comments?per_page=100"
    response = requests.get(URL)
    data = response.json()
    data = pformat(data)
    return data

#
#
# ----- GRAPHS TESTING ROUTE -----
# Use this to test new routes and generate new plotly graphs
#

@my_routes.route('/graphs')
def graphs():

    plot = merge_fraction()

    return render_template('graphs.html', plot=plot)

#
#
# ----- WEB ROUTES -----
#
#

@my_routes.route("/web")
def web_index():
    # return "Example"
    return render_template("web.html")

# Kubernetes endpoints
# ----- GRAPHS -----
@my_routes.route('/web/kubernetes')
def kubernetes():
    return render_template('kubernetes.html')
