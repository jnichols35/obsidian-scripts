import os

import asana
from datetime import date

client = asana.Client.access_token({os.environ['token']})
me = client.users.me()
workspace_id = me['workspaces'][0]['gid']
user_id = me['gid']
due_today = str(date.today())
tasks = client.tasks.get_tasks({'assignee': user_id, 'workspace': workspace_id, 'completed_since': 'now',
                                'opt_fields': 'name,due_on'}, opt_pretty=True)


# date yyyy-mm-dd
def asana_tasks(due_date):
    return [(task['name']) for task in tasks if task['due_on'] == due_date]
