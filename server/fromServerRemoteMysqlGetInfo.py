import mysql.connector
from mysql.connector import Error
import uuid
import re
import getPhoInfo#图片数据json解析
import fromWebAPIGetSize#处理文件大小解析记录有错误的文件
import config as configpy#引入config
class WizServer:
    def __init__(self,db_config,wiz_config):
        self.db_config=db_config
        self.wiz_config=wiz_config
        self.phoData=getPhoInfo.getData()
        self.passageData=[]
    def connectDatabase(self):
        # print("connect database")
        try:
            self.connection = mysql.connector.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config['port']
            )

            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("成功连接到MySQL数据库")
                self.getPassageInfo()
                self.getAttachments()
                # self.getAllUsers()
                # self.getUserLoginInfo()
                self.connectionDatabaseClose()
                # self.show()
        except Error as e:
            print(f"连接数据库时出错: {e}")
            return None, None
        except Exception as e:
            # 非 MySQL 错误（如数据字段异常）也记录，避免 gunicorn worker 直接崩溃且无日志
            print(f"加载笔记数据时出错: {type(e).__name__}: {e}")
            raise
    def connectionDatabaseClose(self):
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("数据库连接已关闭")
    def _get_pho_count(self, kb_guid, doc_guid):
        """从 document_structure.json 取图片数；json 未收录该笔记时返回 0，避免 KeyError 拖垮服务。"""
        kb_key = str(kb_guid)
        doc_key = str(doc_guid)
        photos = self.phoData.get(kb_key, {}).get(doc_key, [])
        if photos is None:
            return 0
        try:
            return len(photos)
        except TypeError:
            return 0

    def getPassageInfo(self):
        self.cursor.execute("SELECT * FROM wiz_document")
        results = self.cursor.fetchall()
        for row in results:
            if row["DOCUMENT_OWNER"] !=self.wiz_config['author']:#筛选指定用户
                continue
            kb_guid = uuid.UUID(bytes=row["KB_GUID"])
            doc_guid = uuid.UUID(bytes=row["DOCUMENT_GUID"])
            body_text = row["BODY_TEXT"] or ""
            pho_count = self._get_pho_count(kb_guid, doc_guid)
            print('#'*50)
            print(f'标题: {row["DOCUMENT_TITLE"]}')
            print(f'路径: {row["DOCUMENT_CATEGORY"]}')
            print(f'附件数: {row["DOCUMENT_ATTACHMENT_COUNT"]}')
            print(f'创建日期: {row["DT_CREATED"]}')
            print(f'笔记字数: {len(body_text)}')
            print(f'笔记GUID: {doc_guid}')
            print(f'笔记图片数量: {pho_count}')
            one = {
                "GUID": [kb_guid, doc_guid],
                "name": row["DOCUMENT_TITLE"],
                "path": row["DOCUMENT_CATEGORY"],
                "attachCount": row["DOCUMENT_ATTACHMENT_COUNT"],
                "creatDate": row["DT_CREATED"],
                "wordCount": len(body_text),
                "phoCounut": pho_count,
                "attachInfo": [],
            }
            self.passageData.append(one)
    def getAttachments(self):
        self.cursor.execute("SELECT * FROM wiz_attachment")
        results = self.cursor.fetchall()
        for row in results:
            print('#'*50)
            print(f"笔记附件名称: {row['ATTACHMENT_NAME']}")
            print(f"笔记附件创建日期: {row['DT_CREATED']}")
            # print(f"笔记附件数据修改时间: {row['DT_DATA_MODIFIED']}")
            # print(f"笔记附件信息修改时间: {row['DT_INFO_MODIFIED']}")
            print(f"笔记附件数据大小: {row['ATTACHMENT_DATA_SIZE']}")
            # print(f"笔记附件版本号: {row['VERSION']}")
            print(f"笔记附件GUID: {uuid.UUID(bytes=row['ATTACHMENT_GUID'])}")
            # print(f"笔记附件所属笔记GUID: {uuid.UUID(bytes=row['DOCUMENT_GUID'])}")
            for i, one in enumerate(self.passageData):
                if one["GUID"][1]==uuid.UUID(bytes=row['DOCUMENT_GUID']):
                    self.passageData[i]['attachInfo'].append({"name":row['ATTACHMENT_NAME'],"creatDate":row['DT_CREATED'],"size":row['ATTACHMENT_DATA_SIZE'],"attGUID":uuid.UUID(bytes=row['ATTACHMENT_GUID'])})

    def getAllUsers(self):
        self.cursor.execute("SELECT * FROM wizasent.wiz_user")
        results = self.cursor.fetchall()
        for row in results:
            print('#'*50)
            print(f"用户GUID: {row["USER_GUID"]}")
            print(f"用户邮箱: {row["EMAIL"]}")
            print(f"用户展示名称: {row["DISPLAYNAME"]}")
            print(f"用户创建日期: {row["DT_CREATED"]}")
            print(f"用户上次登陆时间: {row["LAST_LOGIN"]}")
    def getUserLoginInfo(self):
        self.cursor.execute("SELECT * FROM wizasent.wiz_log_user")
        results = self.cursor.fetchall()
        for row in results:
            print('#'*50)
            try:
                email = re.search(r'<email>(.*?)</email>', row["LOG_MSG"][:-1]).group(1)
                ip = re.search(r'<ip>(.*?)</ip>', row["LOG_MSG"][:-1]).group(1)
                clientType = re.search(r'<type>(.*?)<type>', row["LOG_MSG"][:-1]).group(1)
                print(f"用户登录IP: {ip}")
                print(f"用户登录邮箱: {email}")
                print(f"用户登录平台: {clientType}")
                print(f"用户登录时间: {row["DT_LOG"]}")
            except:
                userId = re.search(r'userId\s*=\s*([^,]+)', row["LOG_MSG"]).group(1).strip()
                ip = re.search(r'ip\s*=\s*([^,]+)', row["LOG_MSG"]).group(1).strip()
                clientType = re.search(r'clientType\s*=\s*([^,]+)', row["LOG_MSG"]).group(1).strip()
                print(f"用户注册IP: {ip}")
                print(f"用户注册邮箱: {userId}")
                print(f"用户注册平台: {clientType}")
                print(f"用户注册时间: {row["DT_LOG"]}")
    def sizeCorrect(self):
        # 初始化文件大小解析API
        wizAPI = fromWebAPIGetSize.wizWebAPI(username=configpy.wiz_config['username'], password=configpy.wiz_config['password'],
                                             domain=configpy.wiz_config['server'])
        wizAPI.getWizToken()
        deleteL = []
        for i, one in enumerate(self.passageData):
            # print(one)
            if one['attachInfo']:  # 存在附件
                for j, o in enumerate(one['attachInfo']):  # 遍历附件列表
                    res = wizAPI.getMessage(str(one['GUID'][1]))['resources']  # 先调用webapi获取附件数据，避免多附件时重复请求
                    if o['size'] == 0:
                        # print("有文件大小记录错误文件存在", o['name'])
                        a = str(o['attGUID'])
                        change = False  # 是否修正数据
                        for a in res:  # 遍历webapi返回数据
                            if str(o['attGUID']) in a['name']:
                                change = True
                                print(f"修正数据{one['name']}.{o['name']}.size from {o['size']} to {a['size']}")
                                self.passageData[i]['attachInfo'][j]['size'] = a['size']  # 修改本地列表里面的大小信息
                                # print(self.passageData[i]['attachInfo'][j])
                                break
                        if change == False:  # 数据没有被更正，表明原始数据已经被删除，执行在本地列表删除该条数据
                            # 只有音频才会存在过期情况，某些附件可能不会出现在webapi的返回数据中
                            if '.mp3' in o['name']:
                                # print(self.passageData[i]['attachInfo'][j])
                                print(f"删除过期音频数据{one['name']}.{o['name']}.size from {o['size']} to NaN")
                                deleteL.append([i, j])
                                # del self.passageData[i]['attachInfo'][j] 这里删除会出现下标混乱的问题，在完全遍历后进行删除，这里只是记录删除下标数据
                            else:
                                print(f"出现异常附件数据{one['name']}.{o['name']}.size from {o['size']} to Error")
            else:
                pass
        for a in deleteL:  # 后续删除避免下标混乱问题出现
            del self.passageData[a[0]]['attachInfo'][a[1]]
        # print(self.passageData)
        wizAPI.logOut()
        return self.passageData
    def show(self):
        print("Wiz Server",self.db_config,self.wiz_config)
    def returnInfo(self):
        return self.passageData
if __name__ == '__main__':
    db_config = {
        'host': '110.40.44.43',
        'database': 'wizksent',
        'user': 'root',
        'password': 'aI9DCyNpEKWe9pn5',
        'port': 3301
    }
    wiz_config={
        'server':'http://110.40.44.43:9251',
        'author':'2113365920@qq.com',
        'username':'2113365920@qq.com',
        'password':'111111',
    }
    wiz = WizServer(db_config,wiz_config)
    wiz.show()
    wiz.connectDatabase()
    wiz.sizeCorrect()#修正录音数据大小异常
    data=wiz.returnInfo()
    print(data)

