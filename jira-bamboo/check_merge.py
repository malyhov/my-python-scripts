#!/usr/bin/env python3

import json
import os
import requests
import subprocess
import sys
import xml.etree.ElementTree as etree

DEBUG = False

job_type = sys.argv[1]
plan_key = sys.argv[2]
branch = sys.argv[3]

URL_JIRA_ISSUE = "http://jira/rest/api/latest/issue"
URL_BAMBOO_PLAN = "http://bamboo/rest/api/latest/plan"
HEADERS = {
        'authorization': "Basic Secret-String",
        'content-type': "application/json"
        }
BASE_DIR = '/var/atlassian/application-data/bamboo/xml-data/build-dir/'+plan_key

# Для тестов repo1
job_type_repo1 = 'repo1_test'
job_id_repo1_prefix = 'r1t_'
allure_folder_repo1 = '-R1T'
# Для тестов repo2
job_type_cpengine = 'repo2_test'
job_id_cpengine_prefix = 'r2t_'
allure_folder_cpengine = '-R2T'

# Для мержа repo1
job_type_repo1_merge = 'repo1_merge'
job_id_php_merge_prefix = 'r1m_'
allure_folder_repo1_merge = '-R1M'
# Для мержа repo2
job_type_repo2_merge = 'repo2_merge'
job_id_repo2_merge_prefix = 'r2m_'
allure_folder_repo2_merge = '-R2M'



def back_to_in_progress(plan_key, branch):
    '''
    If test is fail, reopen task
    '''
    url = URL_BAMBOO_PLAN + "/{}/label.json".format(plan_key)
    response = requests.request("GET", url, headers=HEADERS)
    if DEBUG:
        print("----- Plan key: %s, Branch: %s" % (plan_key, branch))
        print(response.text)
        print("-------------------------------------------------------------")

    try:
        issue_name = json.loads(response.text)['labels']['label'][0]['name']
    except IndexError:
        issue_name = branch
    url = URL_JIRA_ISSUE + "/{}/transitions".format(issue_name)
    querystring = {"expand":"transitions.fields"}
    payload = "{ \"update\": { \"comment\": [ { \"add\": {\"body\": \"Merge problem.\"} }]},\"transition\": {\"id\": \"3\"}}"
    response = requests.request("POST", url, data=payload, headers=HEADERS, params=querystring)
    if DEBUG:
        print("----- Issue Name: %s, Branch: %s" % (issue_name, branch))
        print(response.text)
        print("-------------------------------------------------------------")


def run_script_merge_abort(job_type):
    '''
    Abort merge
    '''
    shell_command_testhost = ''
    shell_command_testhost = 'ssh user@server /srv/scripts/abort_merge_to_master.sh {}'.format(job_type)

    output_testhost = subprocess.check_output(shell_command_testhost, shell=True)
    if DEBUG:
        print("----------------- Output from BranchTester ------------------")
        print("----- Branch: %s, Result: %s, Job type: %s" % (branch, result, job_type))
        print(output_testhost)
        print("-------------------------------------------------------------")


def run_script_merge_commit(branch, job_type):
    '''
    Commit merge
    '''
    shell_command_testhost = ''
    shell_command_testhost = 'ssh user@server /srv/scripts/commit_merge_to_master.sh {} {}'.format(job_type, branch)

    output_testhost = subprocess.check_output(shell_command_testhost, shell=True)
    if DEBUG:
        print("----------------- Output from BranchTester ------------------")
        print("----- Branch: %s, Result: %s, Job type: %s" % (branch, result, job_type))
        print(output_testhost)
        print("-------------------------------------------------------------")



# Устанавливаем переменные в зависимости от типа тестов
if job_type == job_type_repo1:
    job_id = job_id_repo1_prefix+job_id
    BASE_DIR += allure_folder_repo1
elif job_type == job_type_repo2:
    job_id = job_id_repo2_prefix+job_id
    BASE_DIR += allure_folder_repo2
elif job_type == job_type_repo1_merge:
    job_id = job_id_repo1_prefix+job_id
    BASE_DIR += allure_folder_repo1_merge
elif job_type == job_type_repo2_merge:
    job_id = job_id_repo2_merge_prefix+job_id
    BASE_DIR += allure_folder_repo2_merge
else:
    print('Unknown Job Type')
    sys.exit(1)

xml_path = '{}/{}'.format(BASE_DIR, job_id)
if DEBUG:
    print(xml_path)

# Разбираем xml файлы с результатами тестов
files = os.listdir(xml_path)
xml_files = filter(lambda x: x.endswith('.xml'), files)
for file in xml_files:
    if DEBUG:
        print(file)
    full_file = xml_path+'/'+file
    if DEBUG:
        print(full_file)
    tree = etree.parse(full_file)
    root = tree.getroot()
    entries = root.findall(xml_element)
    for child in root.iter('test-case'):
        status = child.attrib['status']
        if status != 'passed':
            print("!!! Тесты не прошли. Смотри Artifacts -> Allure Report !!!")
            back_to_in_progress(plan_key, branch)
            run_script_merge_abort(job_type)
            sys.exit(1)
print("Все тесты прошли успешно")
run_script_merge_commit(branch, job_type)
sys.exit(0)
