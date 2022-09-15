#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yang wei
@file:feishu_app_tools.py
@time:2021/12/07
"""

import requests
from pandas import DataFrame
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


if __name__ == '__main__':
    app = FeiShuApp()
    # print(app.access_token)
    # chat = "oc_8beab9c240f458cdc3f4879ac5f35e22"
    # content = "\\n构建类型：ci \\n代码工程：ai-studio \\n构建时长：10 \\n构建结果：success"
    # app.send_message_by_chat("AI", "wei.yang", "ai-studio", 'success', content, 'v1.0.0', link='http://www.baidu.com')
    # app.send_message_by_chat("AI", "wei.yang", "ai-studio", 'success', 'failed~~~', 'v1.0.0', link='http://www.baidu.com')
    l = app.get_sheet_contents(get_config().get('feishu', 'spreadsheetToken'),
                               get_config().get('feishu', 'white_list_sheetid') + '!A1:C')
    print(l)
    # data_frame = DataFrame(l, columns=l[0])
    # data_frame.drop([0], inplace=True)
    # print(data_frame)
    pass
