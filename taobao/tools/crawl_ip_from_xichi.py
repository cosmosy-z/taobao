import requests
from fake_useragent import UserAgent
from scrapy.selector import Selector
import time
import pymysql


class GetIPFromXichi(object):
    """通过西刺得到可用的IP，存入数据库"""
    def crawl_ip(self):
        """爬取西刺的免费IP"""
        ip_list = []
        for i in range(1, 20):
            headers = UserAgent()
            ua = getattr(headers, "random")
            ua = {"User-Agent": ua}
            url = "http://www.xicidaili.com/nn/" + str(i)
            response = requests.get("http://www.xicidaili.com/nn/", headers=ua)
            # time.sleep(3)
            selector = Selector(text=response.text)
            alltr = selector.css("#ip_list tr")
            for tr in alltr[1:]:
                speed_str = tr.css(".bar::attr(title)").extract_first()
                if speed_str:
                    speed = float(speed_str.split("秒")[0])
                else:
                    speed = 0
                all_text = tr.css("td ::text").extract()
                ip = all_text[0]
                port = all_text[1]
                type = all_text[6]
                if not 'HTTP' in type.upper():
                    type = "HTTP"
                ip_list.append((ip, port, type, speed))

        conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="outback")
        cursor = conn.cursor()
        insert_sql = """insert into ip_proxy(ip,port,type,speed) VALUES (%s,%s,%s,%s) """
        for i in ip_list:
            try:
                cursor.execute(insert_sql, (i[0], i[1], i[2], i[3]))
                conn.commit()
            except Exception as e:
                print(e)
                conn.rollback()

        cursor.close()
        conn.close()

if __name__ == "__main__":
    crawl_ip_from_xichi=GetIPFromXichi()
    crawl_ip_from_xichi.crawl_ip()

