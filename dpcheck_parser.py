#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yang wei
@file:dpcheck_parser.py
@time:2022/09/13
"""
import jinja2
import os
import datetime
from pandas import DataFrame

from config_manager import get_config
from feishu_app_tools import FeiShuApp
from html_parser import HTMLParser
from jenkins_tools import JenkinsTools
from send_email import SendEmail

app = FeiShuApp()


def get_dp_check_report_url():
    job_name = get_config().get('check', 'jenkins_job')
    report_url = JenkinsTools().get_job_last_success_url(job_name)
    return report_url


def dp_report_parser(report_url):
    parser = HTMLParser()
    parser.html_parser(report_url)
    summary = parser.get_pd_report_summary_result()
    detail = parser.get_pd_detail_report()
    for s in range(len(summary)):
        summary[s].update({"vulnerabilities": detail[s]})
    return DataFrame(summary)


def get_white_list():
    result = app.get_sheet_contents(get_config().get('feishu', 'spreadsheetToken'),
                                    get_config().get('feishu', 'white_list_sheetid') + '!A1:C')
    for r in result:
        r[1] = r[1].replace("\n", ";")
        if isinstance(r[2], list):
            r[2] = ";".join(r[2]['text'])
    print(result)
    data_frame = DataFrame(result, columns=result[0])
    data_frame.drop([0], inplace=True)
    return data_frame


def get_module_owner():
    result = app.get_sheet_contents(get_config().get('feishu', 'spreadsheetToken'),
                                    get_config().get('feishu', 'owner_list_sheetid') + '!A1:B')
    data_frame = DataFrame(result, columns=result[0])
    data_frame.drop([0], inplace=True)
    return data_frame


def send_email(html_content):

    mail_info = {
        "host": get_config().get('mail', 'server_host'),
        "from_user": get_config().get('mail', 'from_user'),
        "from_pwd": get_config().get('mail', 'from_pwd'),
        "to_user": get_config().get('mail', 'to_user'),
        "cc_user": get_config().get('mail', 'cc_user'),
        "attachment_path": "",
        "attachment": "",
    }
    mail = SendEmail(mail_info)
    mail.send_mail("第三方依赖扫描报告:dependency_check", html_content)


if __name__ == '__main__':
    if os.path.exists('dependency-check-report.html'):
        url = './dependency-check-report.html'
    else:
        url = get_dp_check_report_url() + '/artifact/dependency-check-report.html'
    level_threshold = get_config().get('check', 'level_threshold').split(",")

    resource_result = dp_report_parser(url)
    resource_result = resource_result[resource_result['level'].isin(level_threshold)]
    owner_list = get_module_owner()
    resource_result = resource_result.merge(owner_list, how='left', left_on='module', right_on='module')
    white_list = get_white_list()
    tmp_result = resource_result.merge(white_list, how='left', left_on=['package_name', 'module'],
                                       right_on=['package', 'module'])
    # 根据白名单进行过滤
    # package_name中不包含package的 并且 cpe_configuration不包含vulnerability_id的
    # tmp_result = tmp_result[tmp_result.apply(lambda x: str(x['package']) not in str(x['package_name']) and str(x['vulnerability_id']) not in str(x['cpe_configuration']), axis=1)]
    tmp_result = tmp_result[[str(x[0]) not in str(x[1]) and str(x[2]) not in str(x[3]) for x in
                             zip(tmp_result['package'], tmp_result['package_name'],
                                 tmp_result['vulnerability_id'], tmp_result['cpe_configuration'])]]
    if tmp_result.shape != (0, 0):
        filename = "第三方依赖扫描结果%s" % datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        file_token = app.create_sheet_file(filename, get_config().get('feishu', 'folder_token'))
        result = tmp_result.drop(axis=1, columns=['package', 'vulnerability_id']).sort_values(
            by=['owner', 'module', 'level'], axis=0)
        owner = result['owner']
        result.pop('owner')
        result.insert(1, 'owner', owner)
        result.rename(columns={'package_name': 'package', 'cpe_configuration': 'vulnerability_id'}, inplace=True)
        result = result.reset_index(drop=True)
        if not os.path.exists("target"):
            os.mkdir("target")
        result_list = []
        owners = result['owner'].drop_duplicates().to_list()
        for owner in owners:
            owner_result = result.groupby(result['owner']).get_group(owner)
            owner_result.to_excel("target" + os.sep + "result_%s.xlsx" % owner)
            try:
                sheet_token = app.create_sheet(file_token, "{}团队测试结果".format(owner))
                app.insert_sheet_contents(file_token, sheet_token, owner_result.values.tolist())
            except Exception as e:
                print("填写飞书文档失败！")
                print(e)
            result_list.append({"owner": owner, "result": owner_result})
        result.to_excel("target" + os.sep + "result.xlsx")

        with open('dependency_check_test_report.html', 'r', encoding='utf-8') as f:
            template_file = f.read()
        template = jinja2.Template(template_file)
        html_content = template.render(result_lists=result_list)
    # html_content = result.to_html('result.html', encoding='utf-8', col_space=100, na_rep="0", index=False)
    else:
        html_content = "测试通过"
    send_email(html_content)
