#!/usr/bin/python3
import json
import requests
import sys

DEBUG = False

issue_name = sys.argv[1]

JIRA_ISSUE_URL = "http://jira/rest/api/latest/issue/%s"
JIRA_SEARCH_URL = "http://jira/rest/api/latest/search"
HEADERS = {
    'authorization': "Basic Secret-String",
    'content-type': "application/json",
    }

flag_task_template = 'EPIC_NAME'
flag_epic_template = 'EPIC_TEMPLATE'
flag_epic_type = 'Epic'



def get_issue_type(issue_name):
    url = JIRA_ISSUE_URL % issue_name
    response = requests.request("GET", url, headers=HEADERS)
    issue_type = json.loads(response.text)['fields']['issuetype']['name']
    if DEBUG:
        print("Тип таска: ", issue_type)
    return issue_type


def get_client_name(issue_name):
    url = JIRA_ISSUE_URL % issue_name
    response = requests.request("GET", url, headers=HEADERS)
    client_name = json.loads(response.text)['fields']['customfield_10008']
    if DEBUG:
        print("Имя клиента: ", client_name)
    return client_name


def get_issue_summary(issue_name):
    url = JIRA_ISSUE_URL % issue_name
    response = requests.request("GET", url, headers=HEADERS)
    summary = json.loads(response.text)['fields']['summary']
    if DEBUG:
        print("Summary: ", summary)
    return summary


def get_linked_tasks():
    querystring = {"jql":"cf[10009]=TEMP-1","fields":"issues"}
    response = requests.request("GET", JIRA_SEARCH_URL, headers=HEADERS, params=querystring)
    tasks = json.loads(response.text)['issues']
    return tasks


def create_new_issue(issue_name, new_summary):
    url = JIRA_ISSUE_URL % ''
    payload_str = ("{\"fields\":{\"project\":{\"key\":\"DELIVERY\"},"
                  "\"summary\":\"%s\",\"issuetype\":{\"name\": \"Task\"},"
                  "\"customfield_10009\":\"%s\"}}"
                  % (new_summary, issue_name))
    payload = payload_str.encode('utf-8')
    response = requests.request("POST", url, data=payload, headers=HEADERS)
    if DEBUG:
        print(response.text)


def write_epic_name(client_name):
    url = JIRA_ISSUE_URL % issue_name
    payload_str = "{\"fields\":{\"summary\":\"%s\"}}" % client_name
    payload = payload_str.encode('utf-8')
    response = requests.request("PUT", url, data=payload, headers=HEADERS)


def create_tasks_in_epic(issue_name, client_name):
    tasks = get_linked_tasks()
    # Добавляем таски в новый эпик
    for t in tasks:
        linked_task_name = t['key']
        task_summary = get_issue_summary(linked_task_name)
        new_summary = task_summary.replace(flag_task_template, client_name)
        create_new_issue(issue_name, new_summary)
    # Делаем правильное название эпика
    write_epic_name(client_name)



print("--- Start Epic Gen -----")
issue_type = get_issue_type(issue_name)
if issue_type != flag_epic_type:
    print(issue_name, " не эпик - пропускаем\n")
    sys.exit(0)

summary = get_issue_summary(issue_name)
if summary == flag_epic_template:
    client_name = get_client_name(issue_name)
    create_tasks_in_epic(issue_name, client_name)
else:
    print(issue_name, " не шаблонный эпик - пропускаем\n")
print("--- Finish Epic Gen -----")
