#根据视频网址打印出uid、弹幕参数信息、弹幕内容、cid
#B站反爬虫策略：一旦发现，就封ip一天到5天不等。
import requests
from requests.exceptions import RequestException
import re
from lxml import etree
import time
import pymysql
import os
import random
from multiprocessing.pool import Pool

# 请求网页
# input: url
# output: response
def get_request(url):
	# normal header , but need more to escape from anti-spider
	headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
	'accept-encoding': 'gzip, deflate, br','accept-language': 'zh-CN,zh;q=0.9',
	'cookie': 'buvid3=7232EE0B-1D08-4503-B552-13EFB4C4008032136infoc; \
	rpdid=kxxkxillokdosixkxwoww; fts=1527077787;dsess=BAh7CkkiD3Nlc3Npb25faWQGOgZFVEkiFWQwZDF\
	jNmFlY2E0NTgzZTYGOwBG%0ASSIJY3NyZgY7AEZJIiU1ZDNjZTg0NGIxZDgxODgzNjY1NmNjMTkyZjlmNzQ2%0AZQY\
	7AEZJIg10cmFja2luZwY7AEZ7B0kiFEhUVFBfVVNFUl9BR0VOVAY7AFRJ%0AIi1lYjMzYjY0MmEzNTBiOTUxNDU1ZmF\
	lMzYzNDM5YTkxNTgzYTYyMGRiBjsA%0ARkkiGUhUVFBfQUNDRVBUX0xBTkdVQUdFBjsAVEkiLWJiMGUwM2Q3ZWEyZDk4%0\
	AYTc1ODA4YmNkYmIxNzgxYWExYmI4NjA0ZTQGOwBGSSIKY3RpbWUGOwBGbCsH%0AnVsFW0kiCGNpcAY7AEYiEjM2LjE1Mi\
	4yNC4xNTY%3D%0A--605988e60fe080a2652f12305a8d4368a36cae7c; dssid=85nkd0d1c6aeca458; sid=8w0s9mcd;\
	LIVE_BUVID=b9ead54c3deb498fb160a16aee5c76e9; LIVE_BUVID__ckMd5=9a95a79f3627c673; stardustvideo=1; \
	CURRENT_FNVAL=16; im_notify_type_13843783=0; im_seqno_13843783=1; im_local_unread_13843783=0;\
	UM_distinctid=1673b1f0c656f1-0cfcba14929d75-36664c08-e1000-1673b1f0c6674e; arrange=matrix; \
	finger=edc6ecda; CURRENT_QUALITY=16; BANGUMI_SS_21715_REC=150705; _dfcaptcha=96566f558cf7bf69d256eb41c7f22719; \
	DedeUserID=13843783; DedeUserID__ckMd5=ce8306a137667c08; SESSDATA=64d84044%2C1549527244%2C793a4a11;\
	bili_jct=a09f5218790347208f68346d354f0736'}
	proxies={'http':"http://47.92.151.20:16819"}
	time.sleep(random.randint(1,3))
	RETRY_TIMES = 8 # 以后改这里比较好
	num = RETRY_TIMES # 重试次数
	while num > 0:
		try:
			response = requests.get(url, headers = headers, timeout = 3, proxies = proxies)
			response.raise_for_status()
			time.sleep(random.random())
			# ****************
			# fix by Dongagent
			# ****************
			if response.status_code == 200 and response.content:
				return response
				break
		except RequestException as e:
			print('error:',e," try again")
			num -= 1
		else:
			if response.status_code != 200:
				print("recent response.status_code is: ", response.status_code, ". connection ERROR")
			else:
				if not response.content:
					print("recent response.content is: ", response.content, ". It's Empty.")
					time.sleep(random.randint(1,3))
			num -= 1
	else:
		# 8次都失败
		print('Try ', num ,' times, But all failed')

# 获取弹幕xml文件的网址
# input:视频网址
# output:xml网址请求的响应

def get_bullet_xml(url):
	# get cid part
	pageResponse = get_request(url)
	if pageResponse:						  #确保传入的响应内容不为空，保证程序正常运行
		pageResponse.encoding = 'utf-8' 
		cid = re.findall("\"cid\":(\d+)",pageResponse.text)
		# get bullet-screen comments part
		xml_link = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + cid[0] 
		print(xml_link)
		return get_request(xml_link),cid[0]

# 解析弹幕文件，获取数据，元组形式
# input:请求xml网址的response文本
# output:以（uid,播放时间,发送时间，弹幕内容，弹幕类型，弹幕颜色，弹幕长度）元组为元素的列表
def parse_page(danmu):
	#将获取的XML弹幕文件写入本地
	if danmu:
		with open('bilibili.xml','wb') as f:
			f.write(danmu[0].content)
		html = etree.parse('bilibili.xml',etree.HTMLParser())
		items = html.xpath('//d/@p')		   #获取弹幕参数
		content = html.xpath('//d/text()')	 #获取弹幕内容
		results = zip(items,content)		   #元组对应的列表形式

		fail_urls = []
		elements = []
		i = 0
		#count = 0
		for result in results:
			if i > 10:
				break

			# 既然i暂时不作为第几个解析成功的一个计数，那就暂时作为result的计数
			print("*****************")
			print("第", i, "个result")
			i += 1

		#	if count>3:
		#		break
		#将播放秒数转化为时：分：秒的格式
		#	else:
			seconds = float(result[0].split(',')[0])
			m, s = divmod(seconds, 60)
			h, m = divmod(m, 60)
			play_time = "%d:%02d:%02d"%(h,m,s)

			#将发送时间的UNIX时间戳转化为年-月-日 时：分：秒格式
			time_local = time.localtime(int(result[0].split(',')[4]))
			dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)

			#请求获取uid的接口
			analysisAPI_url = 'https://biliquery.typcn.com/api/user/hash/' + result[0].split(',')[6]
			api_response = get_request(analysisAPI_url)

			# 这里是经典的非空判断，事实上我上面在request加的代码就是非空判断，当然这里可以再加一重
			#（其实是代码冗余，前期这么写的话逻辑更保险就是了）
			if api_response:
				# print("api_response是：", api_response)


				if api_response.status_code != 200:		 #以防出现网络连接而后续程序中断的问题
					print(api_response.status_code)
					user = 'null'

				else:
					if api_response.content:
						user_id = api_response.json()['data'][0]['id']	
					

						#弹幕内容、模式、大小、颜色
						pattern = result[0].split(',')[1]
						size = result[0].split(',')[2]
						color = hex(int(result[0].split(',')[3]))
						detail = result[1]

						#获取数据（uid,播放时间,发送时间，弹幕内容，弹幕长度，弹幕颜色，弹幕类型，cid）的元组
						element = {"index":i, "user_id":user_id,"play_time":play_time,
							"dt":dt,"lenth":len(detail),"pattern":pattern,
							"size":size,"color":color,"cid":danmu[1],"detail":detail,}
						print(element)
						# print(i)
						# i = i + 1
						elements.append(element)
						#count = count+1
					else:
						print("api_response.content值为空，打印result:", result)
						print("api_response.content值为空，打印url:", analysisAPI_url)
			else:
				print("怎么api_response为空？？？不管了，先加到fail_urls里面")
				fail_urls.append(analysisAPI_url)
		print("*----------------------------*")
		print("fail_urls个数为: ", len(fail_urls))
		print("分别为:")
		for fail_url in fail_urls:
			print(fail_url)
		print("*----------------------------*")
		return elements

#将用户名存入txt（去重）
#input:解析XML后的数据
#output：user_id.txt
def save_data(elements):
	user_list=[]
	for element in elements:
		if str(element['user_id']) not in user_list:	  #用户列表去重
			user_list.append(str(element['user_id']))

	# path = "test"
	# os.chdir(path)
	filename = elements[0]['cid']+'.txt'
	if not os.path.exists(filename):
		for user in user_list:
			with open(filename,'a') as file:
				file.write(user+'\n')
	else: 
		print('The txt file has exists!')

#将弹幕参数信息存入数据库
#input:解析XML后的数据
#output:插入数据后的danmu_parameter
def save_to_database(elements):	
	for element in elements:
		db = pymysql.connect(host = 'localhost',user='root',password='679243',port=3306, db='spiders')
		cursor = db.cursor()
		table = 'danmu_parameter'
		keys = ','.join(element.keys())
		values = ','.join(['%s']*len(element))
		sql = 'INSERT INTO {table}({keys})VALUES ({values}) ON DUPLICATE KEY UPDATE '.format(table = table,keys = keys,values = values)
		update = ','.join(["{key}=%s".format(key=key) for key in element])
		sql += update
		try:
			if cursor.execute(sql,tuple(element.values()) * 2):
				print('Successful')
				db.commit()
				print()

		except Exception as e:
			print(e)
			print('Failed')
			db.rollback()
		db.close()

def main(url):
	# danmu = get_bullet_xml(url)
	# elements = parse_page(danmu)
	elements = []
	elements.append({'user_id': 386847572, 'play_time': '0:00:22', 'dt': '2019-01-01 12:19:46', 'lenth': 13, 'pattern': '1', 'size': '25', 'color': '0xffffff', 'cid': '66614530', 'detail': 'up all night '})
	elements.append({'user_id': 23291226, 'play_time': '0:01:18', 'dt': '2019-01-01 11:40:37', 'lenth': 4, 'pattern': '1', 'size': '25', 'color': '0xffffff', 'cid': '66614530', 'detail': '有超凡！'})
	save_data(elements)
	save_to_database(elements)

#使用多进程POOL池
if __name__ == '__main__':
	urls = ['https://www.bilibili.com/video/av37866145/',
			'https://www.bilibili.com/video/av37743569/',
			'https://www.bilibili.com/video/av38096452/',
			'https://www.bilibili.com/video/av39425207/']
	# for url in urls:
	# 	main(url)
		# print(url)
	main(urls)
	'''
	pool = Pool(processes = 10)

	pool.map(main, urls)
	pool.close()
	pool.join()
	'''