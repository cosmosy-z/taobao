# -*- coding: utf-8 -*-
import scrapy
import re
import time
import urllib.request
from taobao.items import TbItem


class TbSpider(scrapy.Spider):
    name = 'tb'
    allowed_domains = ['tabao.com', "detail.tmall.com", "s.taobao.com", "item.taobao.com", "dsc.taobaocdn.com",
                       "img.alicdn.com"]
    start_urls = ['https://www.taobao.com/']


    def start_requests(self):
        return [scrapy.Request(url="https://www.taobao.com/",  callback=self.start_search)]


    def start_search(self,response):
        keyword = input("please input what do you what to seach ?").strip()
        keyword = urllib.request.quote(keyword)
        for i in range(1,2): # 这里可以优化，可以写一个自动判断是否还有下一页的函数
            url = "https://s.taobao.com/search?q=" + keyword + "&s=" + str(i * 44)
            yield scrapy.Request(url=url,callback=self.parse_search_page)
            time.sleep(20)

    def parse_search_page(self, response):
        """处理搜索页面"""
        html = response.body.decode("utf8", "ignore")
        try:
            # 查找uid 和是否属于天猫，因为淘宝和天猫的详情页面不一样，得到是一个tupe
            uids_and_isTmail = re.compile(r'"nid":"(.*?)".*?"isTmall":(.*?),').findall(html)
            for uid_and_isTmail in uids_and_isTmail:
                if uid_and_isTmail[1] == "true":
                    detailUrl = "https://detail.tmall.com/item.htm?id=" + str(uid_and_isTmail[0])
                else:
                    detailUrl = "https://item.taobao.com/item.htm?id=" + str(uid_and_isTmail[0])
                yield scrapy.Request(detailUrl, callback=self.parsePictureUrl)
                time.sleep(10)
        except Exception as e:
            print(e)

    def parsePictureUrl(self, response):
        """通过详情页面得到存放高清图片的网址"""
        html = response.body.decode("utf8", "ignore")
        try:
            pictureUrl = re.compile('descUrl.*?:.*?//(.*?)\'').findall(html)[0]
            #必须加http才能访问
            pictureUrl = "http://" + pictureUrl
            yield scrapy.Request(pictureUrl, callback=self.parsePicture)
        except Exception as e:
            print(e)

    def parsePicture(self, response):
        """打开存放高清图片的网址后得到是一个json文件，里面有各个高清图片的详细网址，得到这些详细网址，然后交由scrapy下载"""
        item = TbItem()
        html = response.body.decode("utf8","ignore")
        try:
            downPictureUrlList = re.compile('src=.*?\"(.*?)\"').findall(html)
            for downPictureUrl in downPictureUrlList:
                item["img"] = [downPictureUrl]
                yield item
        except:
            print("can not find down page")

    def parse(self, response):
        pass
