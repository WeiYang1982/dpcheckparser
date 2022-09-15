#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yang wei
@file:html_parser.py
@time:2022/09/13
"""
import json
import re
from pandas import DataFrame
from lxml import etree


class HTMLParser:
    def __init__(self):
        self.total = 0
        self.case_detail_result = []
        self.case_summary_result = []
        self.html_content = None
        self.detail_keys = ["result", "type", "module", "caseName", "duration", "expect", "runTime"]
        self.summary_keys = ["module", "total", "passed", "failed"]

    def html_parser(self, html_file):
        self.html_content = etree.parse(html_file, etree.HTMLParser(encoding='utf-8'))

    def get_pd_report_summary_result(self):
        """
        返回样例：
        [{
            "level":{
                "MEDIUM":2
            },
            "package_name":"pkg:javascript/jquery@3.4.1",
            "image_name":"action"
        }]
        """
        table = self.html_content.xpath("//table[@id='summaryTable']/tr")
        result = []
        for i in range(1, len(table)):
            tmp_d = {}
            tr = table[i]
            td_list = tr.findall('td')

            level = td_list[3].xpath("./text()")[0].upper()
            count = int(td_list[4].xpath("./text()")[0])
            if level != '\xa0' and count != 0:
                image_name = td_list[0].xpath("./*/text()")[0]
                try:
                    module_name = td_list[0].xpath("./*/text()")[0].split("@")[1]
                except IndexError:
                    module_name = image_name
                vulnerabilities = ";".join(td_list[1].xpath("./*/text()"))
                package_name = ";".join(td_list[2].xpath("./*/text()"))
                tmp_d.update({"module": module_name, "level": level, "file_name": image_name, "package_name": package_name, "cpe_configuration": vulnerabilities})
                # tmp_d['level'] = {level: count}
            if tmp_d != {}:
                result.append(tmp_d)
        return result

    def get_pd_detail_report(self):
        target_result = []
        vulnerabilities = self.html_content.xpath("//div[@class='subsectioncontent']")
        files = self.html_content.xpath("//h3[@class='subsectionheader standardsubsection']/text()")
        for i in range(len(files)):
            tmp_num = []
            # 取漏洞编号
            nums = vulnerabilities[i].xpath("./div[@class='subsectioncontent standardsubsection']/p/b/a | ./div[@class='subsectioncontent standardsubsection']/p/span[@class='underline']/b")
            for num in nums:
            #     # not(*)   不包含下级节点
            #     # not(@class)  属性中不包含class
            #     tmp_scores = num.xpath("./../../../ul/li[not(*) and not(@class)][1]/text()")
            #     tmp_score = re.findall("[0-9]?[0-9].[0-9]", str(tmp_scores))
            #     score_index = tmp_score.index(max(tmp_score))
            #     level = tmp_scores[score_index][12:][:-6]
            #     tmp_num.append({num.text: level})
                tmp_num.append(num.text)
            target_result.append(tmp_num)
        return target_result


if __name__ == '__main__':
    html_file = "http://ci-bj.mycyclone.com/job/TestGroup/view/%E5%AE%89%E5%85%A8%E6%89%AB%E6%8F%8F/job/dependency_check/156/artifact/dependency-check-report.html"
    # html_content = etree.parse(html_file, etree.HTMLParser())
    parser = HTMLParser()
    parser.html_parser(html_file)
    summary = parser.get_pd_report_summary_result()
    # print(parser.total)
    detail = parser.get_pd_detail_report()
    # for s in range(len(summary)):
    #     summary[s].update({"CVE_ID": detail[s]})
    # df = DataFrame(summary)
    # print(df)
    # with open('result', 'w', encoding='utf-8') as f:
    #     json.dump(summary, f, ensure_ascii=False)
    # print(parser.case_summary_result)
    # pass
