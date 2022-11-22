#!/usr/bin/python
import os
import re

import arrow as arrow
import requests as requests

from asana_tasks_api import *
from jira_tasks_api import *

# variables
city = {os.environ['location']}
daily_notes = {os.environ['dir']}


def weather():
    url = f'https://wttr.in/{city}'
    payload = {'format': '3'}
    res = requests.get(url, params=payload)

    return res.text.strip()


def get_link_for_file(file, link_text=""):
    if link_text != "":
        return "[[" + file.replace(".md", "") + "|" + link_text + "]]"
    else:
        return "[[" + file.replace(".md", "") + "]]"


def get_daily_notes_filename(offset=0):
    file_date = arrow.now()
    if offset != 0:
        file_date = file_date.shift(days=offset)
    return file_date.format('YYYY-MM-DD') + ".md"


def read_file(file_name):
    file_content = ""
    with open(file_name, 'r') as file_obj:
        for line in file_obj:
            file_content += line
    return (file_content)


def get_humanize_date_from_daily_note(file_name):
    daily_note = re.search("\d{4}\.\d{2}\.\d{2}\.[A-Za-z]{3}", os.path.basename(file_name).replace(".md", ""))
    if daily_note:
        (year, mon, day, _) = os.path.basename(file_name).replace(".md", "").split(".")
        todo_date = arrow.get(year + '-' + mon + '-' + day)
        return " (from " + todo_date.humanize() + ")"
    else:
        return ""


def find_todos(file_name, pattern):
    matches = {}
    with open(file_name, 'r') as file_obj:
        for line in file_obj:
            todo = ""
            result = re.search(pattern, line.strip())
            if result:
                if result.group(1):
                    todo = result.group(1).strip()
                    if " (from " in todo:
                        pos = todo.find("(from ")
                        todo = todo[:pos].strip()
                    else:
                        todo = todo.strip()
                    matches[todo] = file_name
    return matches


def search_in_file(file_name, search_for):
    # Searches file_name for search_for and returns boolean result
    with open(file_name, 'r') as file_obj:
        for line in file_obj:
            if search_for in line:
                return True
    return False


def get_done_todos():
    done_task_pattern = "\[x\](.*)"
    done = {}

    for root, dirs, files in os.walk(daily_notes):
        for fi in files:
            fi_done = {}
            if fi.endswith(".md"):
                fi_done = find_todos(os.path.join(root, fi), done_task_pattern)
                for m in fi_done:
                    if m in done.keys():
                        continue
                    else:
                        done[m] = fi_done[m]
    return done


def get_open_todos():
    open_task_pattern = "\[\s\](.*)"
    open = {}

    for root, dirs, files in os.walk(daily_notes):
        for fi in files:
            fi_open = {}
            if fi.endswith(".md"):
                fi_open = find_todos(os.path.join(root, fi), open_task_pattern)
                for m in fi_open:
                    if m in open.keys():
                        continue
                    else:
                        open[m] = fi_open[m]
    return open


daily_notes_file = os.path.join(daily_notes, get_daily_notes_filename())
if os.path.exists(daily_notes_file):
    print("File already exists. Not overwriting...")
else:
    print("Generating daily notes file " + os.path.basename(daily_notes_file) + "...")
    with open(daily_notes_file, 'w') as fh:
        tasks = {}

        # Weather Info
        fh.write(weather() + "\n")

        done_todos = get_done_todos()
        open_todos = get_open_todos()

        for task in open_todos.keys():
            if task in done_todos.keys():
                continue
            else:
                tasks[task] = open_todos[task]

        fh.write("\n## To-Do\n")
        if len(tasks) == 0:
            fh.write("No open to-do items\n")
        else:
            for item in tasks:
                fh.write("- [ ] " + item + get_humanize_date_from_daily_note(tasks[item]) + "\n")

        asana_tasks = asana_tasks(due_today)
        fh.write("\n## Asana To-Do\n")
        if len(asana_tasks) == 0:
            fh.write("No open to-do items\n")
        else:
            for item in list(asana_tasks):
                fh.write("- [ ] " + item + "\n")

        jira_tasks = jira_tasks()
        fh.write("\n## Jira To-Do\n")
        if len(jira_tasks) == 0:
            fh.write("No open to-do items\n")
        else:
            for item in list(jira_tasks):
                fh.write("- [ ] " + item + "\n")
