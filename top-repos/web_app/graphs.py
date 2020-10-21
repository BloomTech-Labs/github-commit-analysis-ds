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
import time

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

# straight API issues pull from github for kubernetes
def issues_graph(full_name):

    URL = f"https://api.github.com/repos/{full_name}/issues?page=1"
    URL2 = f"https://api.github.com/repos/{full_name}/issues?page=2"
    URL3 = f"https://api.github.com/repos/{full_name}/issues?page=3"
    
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
    plot = py.plot(fig, filename='issues-comments-kubernetes-v2', auto_open=True)
    return plot

# merge fraction graphs and API pull
def merge_fraction(days):
    g = Github(PAT)
    repo = g.get_repo("kubernetes/kubernetes")
    all_pulls = repo.get_pulls(state="all")

    """Displays Kubernetes pull request merge fraction visualization.
    Keywork arguments:
    days -- number of days to display (int)
    """

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

def code_frequency(days):
    g = Github(PAT)
    repo = g.get_repo("kubernetes/kubernetes")
    all_pulls = repo.get_pulls(state="all")

    """
    Displays Kubernetes additions and deletions for the given period.
    Keywork arguments:
    days -- number of days to display (int)
    """
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

# top contributors graphs
def top_contributors(full_name):
  """
  Displays top 10 all-time contributors for the given repository.
  Keyword arguments:
  full_name -- owner and name of repository in format: "owner/repo"
  
  """
  g = Github(PAT)
  repo = g.get_repo(full_name)
  stats = repo.get_stats_contributors()[90:]

  repo_data = {
      'user': [stat.author.login for stat in stats],
      'name': [g.get_user(stat.author.login).name for stat in stats],
      'followers': [g.get_user(stat.author.login).followers for stat in stats],
      'total_commits': [stat.total for stat in stats],
  }

  columns = list(repo_data.keys())
  df = pd.DataFrame(repo_data, columns=columns)
  
  fig = go.Figure([go.Scatter(x=df["user"], 
                          y=df["total_commits"], 
                          text=df[['followers', 'name']],
                          marker=dict(size=20, color=df['followers'],showscale=True),
                          hovertemplate =
                          "<b>%{x}</b><br>" +
                          "Name: %{text[1]}<br>" +
                          "Followers: %{text[0]}<br>" +
                          "<extra></extra>",
                          )])

  fig.update_layout(
    title=f'Top 10 All-Time Contributors: {full_name}',
    # annotations=[dict(
    #     xref='paper',
    #     yref='paper',
    #     x=0.5, y=-0.25,
    #     showarrow=False,
    #     text ='This is my caption for the Plotly figure'
    # )]),
    xaxis=dict(
        tickangle=45
    ),
    yaxis=dict(
        title='Total Commits',
    ),
  )
  
  plot = py.plot(fig, filename='top-contributors-kubernetes', auto_open=True)
  return plot

def yearly_commit_activity(owner_repo):
  """Displays commit activity grouped by week for the last 365 days.

  Keywork arguments:
  owner_repo -- owner and name of repository in format: "owner/repo"
  """
  g = Github(PAT)
  repo = g.get_repo(owner_repo)
  stats = repo.get_stats_commit_activity()

  repo_data = {
      'week': [stat.week for stat in stats],
      'total_commits': [stat.total for stat in stats],
  }

  columns = list(repo_data.keys())
  df = pd.DataFrame(repo_data, columns=columns)
  
  fig = go.Figure([go.Bar(x=df["week"], 
                          y=df["total_commits"]
                          )])

  fig.update_layout(
    title=f'Yearly Commit Activity: {owner_repo}',

    yaxis=dict(
        title='Total Commits'
    ),
  )
  
  plot = py.plot(fig, filename='yearly-commit-activity', auto_open=True)
  return plot

def yearly_code_frequency(owner_repo):
  """Displays the number of additions and deletions pushed this year.

  Keywork arguments:
  owner_repo -- owner and name of repository in format: "owner/repo"
  """

  g = Github(PAT)
  repo = g.get_repo(owner_repo)
  stats = repo.get_stats_code_frequency()[::-1]
  months_included = []
  stats_included = []

  while len(months_included) < 12:
    for stat in stats:
      mo = stat.week.month
      if mo not in months_included:
        months_included.append(mo)
        stats_included.append(stat)

  repo_data = {
      'week': [stat.week for stat in stats_included],
      'additions': [stat.additions for stat in stats_included],
      'deletions': [stat.deletions for stat in stats_included]
  }

  columns = list(repo_data.keys())
  df = pd.DataFrame(repo_data, columns=columns)
  
  fig = go.Figure(data=[
                        go.Bar(x=df["week"], y=df["additions"], name="Additions", marker_color='green'),
                        go.Bar(x=df["week"], y=df["deletions"], name="Deletions", marker_color='red')
                        ])

  fig.update_layout(
    title=f'Yearly Code Frequency: {owner_repo}',
    barmode="overlay",
    yaxis=dict(
      title='Changes'
    ),
    # xaxis=dict(
    #   showticklabels=True,
    #   type='category',
    #   tickformat='%b %d,%Y',
    #   # tickmode='linear'
    # )
  )
  
  plot = py.plot(fig, filename='yearly-code-frequency', auto_open=True)
  return plot

def last_weeks_daily_commits(owner_repo):
  """Displays the number of additions and deletions pushed this year.

  Keywork arguments:
  owner_repo -- owner and name of repository in format: "owner/repo"
  """
  g = Github(PAT)
  repo = g.get_repo(owner_repo)
  stats = repo.get_stats_punch_card()
  stats = stats.raw_data

  repo_data = {
      'day': [stat[0] for stat in stats],
      'commits': [stat[2] for stat in stats]
  }

  columns = list(repo_data.keys())
  df = pd.DataFrame(repo_data, columns=columns)
  df = df.groupby(["day"]).sum().reset_index()
  
  d = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday', 4: 'Thursday', 5: 'Friday', 6:'Saturday' } 
  df = df.replace({"day": d}) 
  
  fig = go.Figure([go.Bar(x=df["day"], y=df["commits"])])

  fig.update_layout(
    title=f"Last Week's Daily Commits: {owner_repo}",
    yaxis=dict(
      title='Commits'
    )
  )
  
  plot = py.plot(fig, filename='past-week-daily-commits', auto_open=True)
  return plot

#execute function to keep up to date
# wrapped these in a timer that loads once a day

#def timer():
#    # make
#    time.sleep(5)
#
#    # can make this user defined if we want to
#    repo = "kubernetes/kubernetes"
#    days = 7
#
#    # execute functions
#    issues_graph(repo)
#    merge_fraction(days)
#    code_frequency(days)
#    top_contributors(repo)
#    yearly_commit_activity(repo)
#    yearly_code_frequency(repo)
#    last_weeks_daily_commits(repo)
#
##execute
#timer()