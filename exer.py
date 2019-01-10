#创建弹幕参数信息表
#创建用户个人信息表
#创建视频参数信息表

import pymysql

db = pymysql.connect(host = 'localhost',user = 'root',password = '679243',port = 3306,db ='spiders' )
cursor = db.cursor()
#rank是sql关键词，不能作为字段名
sql_1= '''
CREATE TABLE IF NOT EXISTS danmu_parameter (user_id VARCHAR(255) NOT NULL,play_time TIME(5) NOT NULL,
dt DATETIME(6) NOT NULL,lenth int(30) NOT NULL,pattern VARCHAR(25) NOT NULL,size VARCHAR(255) NOT NULL,
color VARCHAR(255) NOT NULL,cid INT(255) NOT NULL,detail VARCHAR(255) NOT NULL,PRIMARY KEY(user_id,dt))
'''
sql_2='''
CREATE TABLE IF NOT EXISTS user_info (user_id VARCHAR(255) NOT NULL,user_name VARCHAR(255) NOT NULL,
sex VARCHAR(25),rank_row VARCHAR(255),sign VARCHAR(255),level INT(255) NOT NULL,jointime DATETIME(6) NOT NULL,
is_vip VARCHAR(25) NOT NULL,vip_type VARCHAR(25),following int(8),follower int(8),PRIMARY KEY(user_id))
'''
sql_3='''
CREATE TABLE IF NOT EXISTS video_parameter (cid INT(255) NOT NULL,video_name VARCHAR(255) NOT NULL,video_lenth time(6),
video_url VARCHAR(255),video_type VARCHAR(255),broadcast_num INT(255),collect_num INT(255),his_bullet INT(255),
PRIMARY KEY(cid))
'''

# TODO 加入 danmu_test

cursor.execute(sql_1)
cursor.execute(sql_2)
db.close()
