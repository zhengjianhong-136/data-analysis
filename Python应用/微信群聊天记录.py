# -*- coding: utf-8 
# 获取微信群聊天记录并判断语句情绪倾向
from wxpy import *
import pymysql
from aip import AipNlp
import time
import re

bot=Bot(cache_path=True)

db = pymysql.connect(host="localhost",user="root",passwd="root",
                 db="itchat",charset="utf8",port=3306)
cursor = db.cursor()  

group_list = ['群名1','群名2'] 
my_groups = [bot.groups().search(i)[0] for i in group_list]

counter = 0

APP_ID = '16618016'
API_KEY = 'DfqxIBf8kweTFQfdS3I7fb2S'
SECRET_KEY = '9Un1OcKcUfGU4Av85W3M25RUw2gSjTno'
client = AipNlp(APP_ID, API_KEY, SECRET_KEY)

@bot.register(my_groups, except_self=False)
def fn(msg):
    if msg.type == "Text":
        group_name = re.findall(r'[\u4E00-\u9FA5A-Za-z0-9_]+',str(msg))[0]
        comment = msg.text
        member = msg.member.name
        create_time = msg.create_time
        res = client.sentimentClassify(comment)
        positive_prob = res['items'][0]['positive_prob']
        negative_prob = res['items'][0]['negative_prob']
        global counter
        counter = counter + 1
        print('收到第{}条信息，时间:{}'.format(counter,create_time))
        print(msg)
        sql = "INSERT INTO wechat_comment (group_name,member,comment,create_time,positive_prob,negative_prob) VALUES ('{}','{}','{}','{}','{}','{}')" \
        .format(group_name,member,comment,create_time,positive_prob,negative_prob)
        
        time.sleep(0.2)
        try:
            if cursor.execute(sql):
                db.commit()
        except Exception as e:
            print("Insert Failed")
            print(e)
            db.rollback()

embed()

#bot.logout()
#db.close()
