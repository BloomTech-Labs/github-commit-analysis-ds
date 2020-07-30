import os
from dotenv import load_dotenv
import requests
from pprint import pprint
import base64
import json
from github import Github
import pandas as pd

load_dotenv()

# global

#USERNAME = os.getenv("USERNAME", default="OOPS")
#PASSWORD = os.getenv("PASSWORD", default="OOPS")
#PAT = os.getenv("PERSONAL_ACCESS_TOKEN", default="OOPS")
#
##plug in
#client = Github(PAT)
#
# top contributors graphs for kubernetes
def top_contributors():
  """
  Displays top 10 all-time contributors for the given repository.
  Keyword arguments:
  full_name -- owner and name of repository in format: "owner/repo"
  
  """

  repo = g.get_repo("kubernetes/kubernetes")
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

#plug in
#g = Github(username, pw)

#-----USING PYGITHUB FOR REPOSITORIES-----

# pointing to a specific repo from list of user repos
# see if we can plug the dataframe into this
# GET /repos/:owner/:repo
#this_repo ="kubernetes/kubernetes"
#repo = client.get_repo(this_repo)
#
## grabbing important features
#description = repo.description
#name = repo.full_name
#topics = repo.get_topics()
#forks_count = repo.forks_count
#language = repo.language
#oic = repo.open_issues_count
#watchers_count = repo.watchers_count
#subscribers_count = repo.subscribers_count
#
## printing output
#print("\n-----PRINT STATEMENT-----\n"
#"\nDescription: ", description,
#"\nName: ", name,
#"\nTopics: ", topics,
#"\nForks Count: ", forks_count,
#"\nCoding Language: ", language,
#"\nOpen Issues Count: ", oic,
#"\nWatchers Count: ", watchers_count,
#"\nSubscribers Count: ", subscribers_count
#)

#------WORKING CODE------

#TOdo*********
#top100_file = 'git_app/top_100_repos.json'
#pd.read_json
#print(top100_file)
#
## user defined repo
#repo = 'apache/spark'
#
## api-endpoint for repo commits, can only receive last 100
## added ?per_page=100 to maximize outputs
#URL = f"https://api.github.com/repos/{repo}/commits?per_page=100"
#
## requests a response using import requests
#response = requests.get(URL)
#
## converting the request to a json iterable list
#data = response.json()
#
## Calling DataFrame constructor on list 
##df = pd.DataFrame(data)
#
## getting the numbers of rows to iterate through later
#rows = 100
#
## initializing lists
#date_dict = []
#message_dict = []
#reason_dict = []
#
## for integer in range of df shape
#for i in range(rows):
#  # grabbing date of commit (timestamp)
#  date = data[i]['commit']['author']['date']
#  # append each date to date_dict list
#  date_dict.append(date)
#  
#  # same thing for commit message
#  message = data[i]['commit']['message']
#  message_dict.append(message)
#
#  # same thing for the commit reason
#  reason = data[i]['commit']['verification']['reason']
#  reason_dict.append(reason)
#
#  # place each parameter into a dictionary
#  commit_dict = {
#      "repo": repo,
#      "date": date_dict,
#      "message": message_dict,
#      "reason": reason_dict}
#
#df_commit = pd.DataFrame.from_dict(commit_dict, orient='columns')
#print(df_commit)