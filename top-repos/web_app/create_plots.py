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
chart_studio.tools.set_config_file(world_readable=True, sharing='public')


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
    )
  )
  
  plot = py.plot(fig, filename='yearly-code-frequency', auto_open=True)
  return plot

yearly_code_frequency("kubernetes/kubernetes")