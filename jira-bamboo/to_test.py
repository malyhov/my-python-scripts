#!/usr/bin/env python3
# Если к Jira таску прикреплен бранч, запускаем в Bamboo соответствующий план тестирования

import json
import requests
import sys

issue_name = sys.argv[1]

DEBUG = False

build_key = ''
username = 'user'
password = 'password'

URL_BAMBOO = "http://bamboo/rest/api/latest"
URL_JIRA_ISSUE = "http://jira/rest/api/latest/issue/"
URL_JIRA_DEV_ISSUE = "http://jira/rest/dev-status/1.0/issue/"


def get_key_by_repo(repo_key, branch):
    # чтобы найти бранч нужно вызвать список всех тасков для данного repo
    bamboo_repo_url = URL_BAMBOO + '/plan/{}/branch.json'.format(repo_key)
    response = requests.get(bamboo_repo_url, auth=(username, password))
    repo_branches = json.loads(response.text)['branches']['branch']
    branch = branch.replace('/', '-')

    for b in repo_branches:
        # и найти в них тот у которого shortName соответствует нашему бранчу
        if b['shortName'] == branch:
            # и так получим ключ джоба который нужно вызывать
            build_key = b['key']
            print("Ключ джоба: {}".format(build_key))
            return build_key


def set_label(build_key):
    url = URL_BAMBOO + '/plan/{}/label'.format(build_key)

    payload = '<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>\n<label name=\"{}\"/>'.format(issue_name)
    headers = {
        'authorization': "Basic Secret-String",
        'content-type': "application/xml"
        }
    response = requests.request("POST", url, data=payload, headers=headers)
    if DEBUG:
        print("----- SET_LABEL: BUILD_KEY: %s, ISSUE: %s -----" % (build_key, issue_name))
        print(response.text)
        print("-------------------------------------------------------------")


# По имени таска найти его ID
issue_url = URL_JIRA_ISSUE + issue_name
response = requests.get(issue_url, auth=(username, password))
issue_id=json.loads(response.text)['id']

# По ID таска найти информацию о нем, проверить есть ли бранчи. 
branch_url = URL_JIRA_DEV_ISSUE + 'detail?issueId={}&applicationType=stash&dataType=pullrequest'.format(issue_id)
response = requests.get(branch_url, auth=(username, password))
branches = json.loads(response.text)['detail'][0]['branches']

# Если бранчи есть, смотрим к какому repo они относятся
if branches:

    for b in branches:
        url = b['url'].split('/')
        repo = url[6]
        branch = b['name']

        # В зависимости от repo дальше выбирается план тестирования в Bamboo
        if repo == 'repo1':
            # repo_key жестко прописан в Bamboo
            repo_key = 'TMB-TA'
            print('Вызываем Bamboo план TMB-TA и branch=', branch)
        elif repo == 'repo2':
            repo_key = 'TMB-TMB'
            print('Вызываем Bamboo план TMB-TMB и branch=', branch)
        elif repo == 'repo3':
            repo_key = 'TMB-TSB'
            print('Вызываем Bamboo план TMB-TSB и branch=', branch)
        else:
            print('ERROR: Нет планов тестирования для указанного репозитория')
            continue

        build_key = get_key_by_repo(repo_key, branch)
        if build_key:
            # Добавить issue_name в label плана тестирования бранча
            set_label(build_key)
            # Запустить нужный джоб
            bamboo_queue_url = URL_BAMBOO + '/queue/{}.json'.format(build_key)
            response = requests.post(bamboo_queue_url, auth=(username, password))
            print('Ответ сервера: {}'.format(response.text))
else:
    print('No branches in this task')

