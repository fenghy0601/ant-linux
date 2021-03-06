# coding:utf-8
import lxml.html
import json
import re
import crawler_tools
import csv

class Crawler_fund:
    def __init__(self, url):
        self.html = crawler_tools.download(url)
        self.tree = lxml.html.fromstring(self.html)
        self.type = url.split('/')[-1].strip('.html')

    def get_max_page(self):
        return self.tree.cssselect('div#pagebar >label')[-2].text_content()

    def get_fund_info(self):
        funds = self.tree.cssselect('table#tblite_pg > tbody > tr')
        for single_fund in funds:
            id = single_fund[0].text_content()
            name = single_fund.cssselect('td.fname')[0].text_content()
            fb = single_fund.cssselect('td > span.fb')[0].text_content()
            date = single_fund.cssselect('td > span.date')[0].text_content()
            num = []
            for num_attr in single_fund.cssselect('td[class*=num]'):
                num.append(num_attr.text_content())
            start_num = single_fund.cssselect('div.l > a')[0].text_content()
            cost_rate = single_fund.cssselect('div.r')[0].text_content()
            print id, name, fb, date, num, start_num, cost_rate

    def main(self):
        page = self.get_max_page()
        print "Total Page: %s" % page
        #Csv_output()
        for i in range(int(page)):
            print "PAGE: %s" % (i + 1)
            url = 'http://fundapi.eastmoney.com/fundtradenew.aspx?ft=%s&sc=1n&st=desc&pi=%s&pn=100&cp=&ct=&cd=&ms=&fr=&plevel=&fst=&ftype=&fr1=&fl=0&isab=' % (self.type, i)
            fund_page = Crawler_json(url, self.type)
            fund_page.data_format()

class Crawler_json:
    def __init__(self, url, type):
        self.html = crawler_tools.download(url)
        self.type = type

    def decode_json(self):
        # 将解码的格式预处理成Python可识别的json格式i
        pre_string = self.html.split('=')[-1].rstrip(';')
        m = re.findall('(\{|\,)(\w+):', pre_string)
        data_name = 'datas'
        formatted_str = ''
        for substring in m:
            # 匹配变量命名规则
            if 'data' in substring[1]:
                data_name = substring[1]
            formatted_str = re.sub(substring[1], '\"%s\"' % substring[1], pre_string)
            pre_string = formatted_str
        return json.loads(formatted_str)[data_name]

    def data_format(self):
        datas = self.decode_json()
        for data in datas:
            data = data.split('|')
            fund_attr = []
            for i in range(0, 2) + range(3 ,15) + [18, 24]:
                if data[i] == '':
                    # 日期格式空值处理, 将空值替换为mysql-timestamp类型最小时间
                    if i == 3:
                        data[i] = '1970-01-02'
                    # 非日期格式空值处理
                    else:
                        data[i] = '-999'
                fund_attr.append(data[i].encode('utf-8'))
            fund_attr.append(self.type)
            print "ID:" + fund_attr[0] + "\tNAME:"+ fund_attr[1]
            Csv_output(fund_attr)

class Csv_output:
    def __init__(self, row = None):
        if row is None:
            row = ["ID", "NAME", "DATE", "VALUE", "R_DAY", "R_WEEK", "R_MONTH", "R_3MONTH", "R_6MONTH", "R_YEAR", "R_2YEAR", "R_3YEAR", "SINCE_LAST_YEAR", "SINCE_SET_UP", "BUY_RATE", "LOWEST_COST"]
        with open('fund_data.csv', mode='a') as csv_file:
            self.writer = csv.writer(csv_file)
            self.writer.writerow(row)

if __name__ == '__main__':
    Crawler_fund('http://fund.eastmoney.com/trade/pg.html').main()
    Crawler_fund('http://fund.eastmoney.com/trade/gp.html').main()
    #Crawler_fund('http://fund.eastmoney.com/trade/hh.html').main()
    Crawler_fund('http://fund.eastmoney.com/trade/zq.html').main()
    Crawler_fund('http://fund.eastmoney.com/trade/zs.html').main()
    Crawler_fund('http://fund.eastmoney.com/trade/qdii.html').main()
    #Crawler_fund('http://fund.eastmoney.com/trade/hb.html').main()
    #Crawler_fund('http://fund.eastmoney.com/trade/lc.html').main()
    #Crawler_fund('http://fund.eastmoney.com/trade/bb.html').main()