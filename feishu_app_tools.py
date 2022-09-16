#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yang wei
@file:feishu_app_tools.py
@time:2021/12/07
"""

import requests

from config_manager import get_config


class FeiShuApp:
    def __init__(self):
        self.base_url = "https://open.feishu.cn"
        self.app_id = get_config().get('feishu', 'app_id')
        self.app_secret = get_config().get('feishu', 'app_secret')
        self.access_token = self.get_access_token()
        self.header = {"Authorization": "Bearer %s" % self.access_token}

    def get_access_token(self):
        uri = "/open-apis/auth/v3/app_access_token/internal/"
        params = {"app_id": self.app_id, "app_secret": self.app_secret}
        res = requests.post(self.base_url + uri, json=params)
        access_token = res.json()['app_access_token']
        return access_token

    def get_sheet_contents(self, spreadsheet_token, sheet_range):
        uri = "/open-apis/sheets/v2/spreadsheets/{}/values/{}"
        res = requests.get(self.base_url + uri.format(spreadsheet_token, sheet_range), headers=self.header)
        result = res.json()['data']['valueRange']['values']
        return result

    def create_sheet_file(self, title, folder_token):
        uri = "/open-apis/sheets/v3/spreadsheets"
        self.header.update({"Content-Type": "application/json; charset=utf-8"})
        json_body = {"title": title, "folder_token": folder_token}
        res = requests.post(self.base_url + uri, headers=self.header, json=json_body)
        return res.json()['data']['spreadsheet']['spreadsheet_token']

    def get_first_sheet_token(self, spreadsheet_token):
        uri = "/open-apis/sheets/v3/spreadsheets/{}/sheets/query".format(spreadsheet_token)
        res = requests.get(self.base_url + uri, headers=self.header)
        print(res.text)
        return res.json()['data']['sheets'][0]['sheet_id']

    def create_sheet(self, spreadsheet_token, sheet_title):
        uri = "/open-apis/sheets/v2/spreadsheets/{}/sheets_batch_update"
        self.header.update({"Content-Type": "application/json; charset=utf-8"})
        json_body = {"requests": [{"addSheet": {"properties": {"title": sheet_title}}}]}
        res = requests.post(self.base_url + uri.format(spreadsheet_token), headers=self.header, json=json_body)
        print(res.text)
        return res.json()['data']['replies'][0]['addSheet']['properties']['sheetId']

    def insert_sheet_contents(self, spreadsheet_token, sheet_id, contents):
        uri = "/open-apis/sheets/v2/spreadsheets/{}/values_prepend"
        self.header.update({"Content-Type": "application/json; charset=utf-8"})
        json_body = {"valueRange": {"range": "{}!A:E".format(sheet_id), "values": contents}}
        res = requests.post(self.base_url + uri.format(spreadsheet_token), headers=self.header, json=json_body)
        print(res.text)
        return res


if __name__ == '__main__':
    app = FeiShuApp()
    # print(app.access_token)
    # chat = "oc_8beab9c240f458cdc3f4879ac5f35e22"
    # content = "\\n构建类型：ci \\n代码工程：ai-studio \\n构建时长：10 \\n构建结果：success"
    # app.send_message_by_chat("AI", "wei.yang", "ai-studio", 'success', content, 'v1.0.0', link='http://www.baidu.com')
    # app.send_message_by_chat("AI", "wei.yang", "ai-studio", 'success', 'failed~~~', 'v1.0.0', link='http://www.baidu.com')
    # l = app.get_sheet_contents(get_config().get('feishu', 'spreadsheetToken'),
    #                            get_config().get('feishu', 'white_list_sheetid') + '!A1:C')
    # print(l)
    # data = ['be-data-insights', '刘振杰', 'CRITICAL', 'image@be-data-insights@2.5.0_82_test_2.52209061623_8870273_standard@2022-09-15.tar: layer.tar: WireFrame.jar', '', 'cpe:2.3:a:wire:wire:1.8.0.332:*:*:*:*:*:*:*', 'CVE-2020-27853\nCVE-2021-41093\nCVE-2020-15258\nCVE-2018-8909\nCVE-2021-32665\nCVE-2021-32666\nCVE-2022-23625\nCVE-2022-31009\nCVE-2021-21301\nCVE-2021-32755']
    # app.insert_sheet_contents("shtcnmyBVbKtGD3L4kvL5mNSZvc", '838814', data)

    r = app.create_sheet_file("aaasss", get_config().get('feishu', 'folder_token'))
    print(r)
    print(app.get_first_sheet_token(r))
    # print(app.create_sheet(r, "1"))
    # app.create_sheet(r, "2")
    # data_frame = DataFrame(l, columns=l[0])
    # data_frame.drop([0], inplace=True)
    # print(data_frame)
    pass
