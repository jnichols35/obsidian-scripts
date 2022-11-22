import os

import json
from atlassian import Jira

jira = Jira(
    url='{os.environ['url']}',
    username='{os.environ['username']}',
    password='{os.environ['password']}',
    cloud=True)
JQL = '{os.environ['JQL']}'
data = jira.jql(JQL)
json_object = json.dumps(data, indent=1)
data_json = json.loads(json_object)
item_number = data_json['total']


def jira_tasks():
    return [({os.environ['url']} + "/browse/" + data_json['issues'][i]['key']) for i in range(item_number)]
  
