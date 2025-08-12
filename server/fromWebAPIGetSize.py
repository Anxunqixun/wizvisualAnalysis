import requests
class wizWebAPI:
    def __init__(self,username,password,domain):
        self.username = username
        self.password = password
        self.token = ""
        self.kbGuid = ''
        self.headers = {}
        self.data = []
        self.domain = domain
        self.update_url()  # 初始化 URL
    def update_url(self):
        self.url={
            "getWizToken":f"{self.domain}/as/user/login",
            "logOut":f"{self.domain}/as/user/logout",
            "getMessage":f"{self.domain}/ks/note/download/{self.kbGuid}/",
        }
    def getWizToken(self):
        params = {
            'clientType': 'web',
            'clientVersion': '4.0',
            'lang': 'zh-cn',
        }
        json_data = {
            'userId': self.username,
            'password': self.password,
            'autoLogin': True,
            'domain': 'clouded.top',
            'deviceId': None,
        }
        response = requests.post(self.url['getWizToken'],params=params,json=json_data,).json()
        if response['returnCode'] == 200:#登陆成功
            self.token = response["result"]["token"]
            self.kbGuid = response["result"]["kbGuid"]
            self.update_url()
            self.headers["X-Wiz-Token"] = self.token
        elif response['returnCode'] == 31002:#用户名密码错误
            print(response["returnMessage"])

    def logOut(self):
        params = {
            'domain': 'clouded.top',
            'clientType': 'web',
            'clientVersion': '4.0',
            'lang': 'zh-cn',
        }
        requests.get(self.url['logOut'], params=params,headers=self.headers)
        print("退登录成功！！")

    def getMessage(self,uid):
        params = {
            'downloadInfo': '1',
            'downloadData': '1',
            'withFavor': 'false',
            'withShare': 'true',
            'clientType': 'web',
            'clientVersion': '4.0',
            'lang': 'zh-cn',
        }
        response = requests.get(f'{self.url['getMessage']}{uid}',params=params,headers=self.headers).json()
        return response
if __name__ == '__main__':
    main=wizWebAPI(username="yinghuo@clouded.top",password="anxunqixun",domain="http://110.40.44.43:9251")
    main.getWizToken()
    res=main.getMessage('f482cc33-ffaa-481c-a985-f1268790eb82')
    print(res)
    main.logOut()
