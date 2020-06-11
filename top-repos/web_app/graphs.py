import plotly
import plotly.graph_objects as go
import chart_studio.plotly as py
import chart_studio
import plotly.express as px
# for testing
import plotly.io as pio
import pandas as pd
import numpy as np
import json
import requests
from datetime import date, timedelta
from dotenv import load_dotenv
import os
from github import Github

load_dotenv()

# github personal authentication token
PAT = os.getenv("PAT", default="OOPS")
CHART_STUDIO_USERNAME = os.getenv("CHART_STUDIO_USERNAME", default="OOPS")
CHART_STUDIO_API_KEY = os.getenv("CHART_STUDIO_API_KEY", default="OOPS")
CHART_STUDIO_SHARING = os.getenv("CHART_STUDIO_SHARING", default="OOPS")

# Config files for chart studio
chart_studio.tools.set_credentials_file(username=CHART_STUDIO_USERNAME, api_key=CHART_STUDIO_API_KEY)
# Config for share settings, can be public, private, etc
chart_studio.tools.set_config_file(world_readable=True, sharing=CHART_STUDIO_SHARING)

# example structure
def create_graph():
    trace0 = go.Scatter(
    x=[1, 2, 3, 4],
    y=[10, 15, 13, 17]
    )
    trace1 = go.Scatter(
    x=[1, 2, 3, 4],
    y=[16, 5, 11, 9]
    )
    data = [trace0, trace1]
    
    plot = py.plot(data, filename = 'basic-line', auto_open=True)

    return plot

# straight API issues pull from github for kubernetes
def issues_graph():
    URL = "https://api.github.com/repos/kubernetes/kubernetes/issues?page=1"
    URL2 = "https://api.github.com/repos/kubernetes/kubernetes/issues?page=2"
    URL3 = "https://api.github.com/repos/kubernetes/kubernetes/issues?page=3"
    
    # sending get request and saving the response as response object 
    r = requests.get(url = URL)
    r2 = requests.get(url = URL2)
    r3 = requests.get(url = URL3) 
    
    # extracting data in json format 
    json_data_1 = r.json()
    json_data_2 = r2.json()
    json_data_3 = r3.json() 

    # converting from json to pandas data frame
    issues_df_1 = pd.DataFrame(json_data_1)
    issues_df_2 = pd.DataFrame(json_data_2)
    issues_df_3 = pd.DataFrame(json_data_3)

    # appending dataframes
    issues_df = issues_df_1.append(issues_df_2)
    issues_df = issues_df.append(issues_df_3)
    issues_df['body_length'] = issues_df['body'].str.len()

    # plot figure
    fig = px.scatter(issues_df, x="created_at", y="comments", color="author_association",
                 size='body_length', hover_data=['title'])

    # define layour parameters
    fig.update_layout(
    title="Kubernetes Issues Comments",
    xaxis_title="Created At",
    yaxis_title="Number of Comments",
    font=dict(
        family="Courier New, monospace",
        size=12,
        color="#7f7f7f",
    ))

    # variable for plot to return, saves filename to chart_studio
    plot = py.plot(fig, filename='issues-comments-kubernetes-v2')
    return plot

def merge_fraction():
    g = Github(PAT)
    repo = g.get_repo("kubernetes/kubernetes")
    all_pulls = repo.get_pulls(state="all")

    """Displays Kubernetes pull request merge fraction visualization.
    Keywork arguments:
    days -- number of days to display (int)
    """
    days = 7

    limit = date.today() - timedelta(days)
    pulls = []

    for pull in all_pulls:
      pull_date = pull.created_at.date()
      if pull_date == date.today():
        continue
      elif pull_date >= limit:
        pulls.append(pull)
      else: 
        break

    pulls_dict = {
        'created_at': [pull.created_at.date() for pull in pulls],
        'is_merged': [pull.merged for pull in pulls]
    }

    columns = list(pulls_dict.keys())
    df = pd.DataFrame(pulls_dict, columns=columns)

    total_count = df.groupby("created_at")["is_merged"].count().rename("total_count")
    true_count = df[df.is_merged==True].groupby("created_at")["is_merged"].count().rename("merged_count")
    false_count = df[df.is_merged==False].groupby("created_at")["is_merged"].count().rename("not_merged_count")

    df = pd.concat([true_count, false_count, total_count], axis=1).reset_index().fillna(0)
    df = df.rename(columns={"index": "created"})
    df['merge_fraction'] = df['merged_count']/df['total_count']
    
    # plot params
    fig = px.scatter(df, x="created", y="merge_fraction", range_y=[0,1],
                     size='total_count', hover_data=['total_count'])
    fig.update_yaxes(dtick=0.1)
    fig.update_layout(
        title=f"Kubernetes Past {days} Days Merge Fraction",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="black"
        )
    )
    
    plot = py.plot(fig, filename='merge-fractions-kubernetes')
    return plot

def code_frequency():
    g = Github(PAT)
    repo = g.get_repo("kubernetes/kubernetes")
    all_pulls = repo.get_pulls(state="all")

    """Displays Kubernetes additions and deletions for the given period.

    Keywork arguments:
    days -- number of days to display (int)
    """
    days = 7

    limit = date.today() - timedelta(days)
    pulls = []

    for pull in all_pulls:
      pull_date = pull.created_at.date()
      if pull_date == date.today():
        continue
      elif pull_date >= limit:
        pulls.append(pull)
      else: 
        break

    pulls_dict = {
        'created_at': [pull.created_at.date() for pull in pulls],
        'additions': [pull.additions for pull in pulls],
        'deletions': [pull.deletions for pull in pulls]
    }

    columns = list(pulls_dict.keys())
    df = pd.DataFrame(pulls_dict, columns=columns)

    additions_count = df.groupby("created_at")["additions"].sum()
    deletions_count = df.groupby("created_at")["deletions"].sum()

    df = pd.concat([additions_count, deletions_count], axis=1).reset_index().fillna(0)
    df = df.rename(columns={"index": "created"})

    fig = go.Figure()

    fig.add_trace(go.Bar(x=df["created_at"],
                    y=df["additions"],
                    name='Additions',
                    marker_color='green'
                    ))
    
    fig.add_trace(go.Bar(x=df["created_at"],
                    y=df["deletions"],
                    name='Deletions',
                    marker_color='red'
                    ))

    fig.update_layout(
        title=f'Kubernetes Past {days} Days Code Frequency',
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Changes',
            titlefont_size=16,
            tickfont_size=14,
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        barmode='group',
        xaxis_tickangle=-45,
        bargap=0.15, # gap between bars of adjacent location coordinates.
        bargroupgap=0.1 # gap between bars of the same location coordinate.
    )
    
    plot = py.plot(fig, filename='code-frequency-kubernetes')
    return plot


