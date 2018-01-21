import requests
import pymysql


class GetIp(object):
    """从数据库中取出可用的IP给爬虫使用"""
    conn = pymysql.connect(host="127.0.0.1", user="root", password="root", db="outback")
    cursor = conn.cursor()

    def get_random_ip(self):
        select_sql = "select ip,port,type from ip_proxy ORDER  by rand() limit 1"

        result = self.cursor.execute(select_sql)
        for ip_info in self.cursor.fetchall():
            ip = ip_info[0]
            port = ip_info[1]
            type = ip_info[2].lower()
            judge_result = self.judge_ip(type, ip, port, )
            if judge_result:
                # 这里不能关闭连接，因为每一个请求都会云获取一个IP，如果关了，就只能获取一个
                # self.cursor.close()
                # self.conn.close()

                return "{0}://{1}:{2}".format(type, ip, port)
            else:
                self.get_random_ip()

    def judge_ip(self, type, ip, port):
        baidu = "https://www.baidu.com"
        proxy_url = "{0}://{1}:{2}".format(type, ip, port)
        try:
            proxy_dict = {type:proxy_url,}
            response = requests.get(baidu, proxies=proxy_dict)
        except Exception as e:
            print("invalid in or port ")
            self.delete_ip(ip)
            return False
        else:
            code = response.status_code
            if code >= 200 and code < 300:
                print("effective ip,the ip is",proxy_url)
                return True
            else:
                print("invalid iP ")
                self.delete_ip(ip)
                return False

    def delete_ip(self, ip):
        delete_sql = """delete FROM ip_proxy where ip='{0}'""".format(ip)
        try:
            self.cursor.execute(delete_sql)
            self.conn.commit()
        except Exception as e:
            print(e)



if __name__ == "__main__":
    get_ip = GetIp()
    ip = get_ip.get_random_ip()
    print(ip)
