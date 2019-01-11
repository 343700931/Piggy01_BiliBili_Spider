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
from multiprocessing import Pool, Lock
import threadpool


# ---------------Class Methods START-----------------


class Cid_Manager(object):
	"""docstring for Cid_Manager"""
	# 单例模式

	# *****************************

	# usage
	'''
	cid_Manager = Cid_Manager() # 实例化
	cid_Manager.add_url(cid, url)   # 添加cid-url到字典
	cid_Manager.get_url(cid)	# 获取cid对应的url
	'''
	# *****************************

	def __new__(cls, *args, **kwargs):
			if not hasattr(cls, '_instance'):
				cls._instance = super().__new__(cls, *args, **kwargs)
				cls.url_dic = {"cid" : "url"}
				cls.file_path_dic = {"cid" : "path"}
			return cls._instance

	def add_url(self, cid, url):
		if cid not in self.url_dic.keys():
			self.url_dic[cid] = url
			return 0
		else:
			return -1
	
	def get_url(self, cid):
		if cid in self.url_dic.keys():
			return self.url_dic.get(cid)
		else:
			print("Cid_Manager don't know this cid.")
			return -1

	def add_path(self, cid, file_path):
		if cid not in self.file_path_dic.keys():
			self.file_path_dic[cid] = file_path
			return 0
		else:
			return -1

	def get_path(self, cid):
		if cid in self.file_path_dic.keys():
			return self.file_path_dic.get(cid)
		else:
			print("Cid_Manager don't know this cid.")
			return -1

# 通过cid保存cid和url
def save_cid_and_url(cid, url):
	# 生成url manager的实例
	cid_Manager = Cid_Manager()
	if cid_Manager.add_url(cid, url) == 0:
		print("Cid_Manager: operation 'add_url' success.")
	else:
		print("Cid_Manager already had this cid.")

# 通过cid获取url
def get_url_from_cid(cid):
	# 生成url manager的实例
	cid_Manager = Cid_Manager()
	return cid_Manager.get_url(cid)

# 通过cid保存对应的文件夹路径
def save_path_with_cid(cid, file_path):
	# 生成url manager的实例
	cid_Manager = Cid_Manager()
	if cid_Manager.add_path(cid, file_path) == 0:
		print("Cid_Manager: operation 'add_path' success.")
	else:
		print("Cid_Manager don't know this cid.")

# 通过cid获取file path
def get_path_from_cid(cid):
	# 生成url manager的实例
	cid_Manager = Cid_Manager()
	return cid_Manager.get_path(cid)

# ---------------Class Methods END-----------------


# 请求网页
# input: url
# output: response
def get_request(url):
	# normal header , but need more to escape from anti-spider

	user_agent = [
	"Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
	"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
	"Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
	"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
	"Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
	"Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
	"Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
	"Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
	"Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
	"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
	"Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
	"Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
	"Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
	"Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
	"Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
	"MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
	"Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
	"Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
	"Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
	"Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
	"Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
	"Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
	"UCWEB7.0.2.37/28/999",
	"NOKIA5700/ UCWEB7.0.2.37/28/999",
	"Openwave/ UCWEB7.0.2.37/28/999",
	"Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
	# iPhone 6：
	"Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",
	# 原本使用的
	'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
	]

	

	headers = {
	'User-Agent':random.choice(user_agent),
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
	proxies = {'http':"http://47.92.151.20:16819"}
	time.sleep(random.randint(1, 3))
	RETRY_TIMES = 20 # 以后改这里比较好
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
		print('Try ', RETRY_TIMES ,' times, But all failed')

# 获取弹幕xml文件的网址
# input:视频网址
# output:xml网址请求的响应

def get_bullet_xml(url):
	if 'bangumi/play/ep' in url:
		return get_ep_bullet_xml(url)
	else:
		return get_av_bullet_xml(url)

# 获取url中有av号的弹幕xml文件的网址
# input:视频网址
# output:xml网址请求的响应

def get_av_bullet_xml(url):
	# get cid part
	print('we enter the av url')
	pageResponse = get_request(url)
	if pageResponse:						  #确保传入的响应内容不为空，保证程序正常运行
		pageResponse.encoding = 'utf-8' 
		cid = re.findall("\"cid\":(\d+)",pageResponse.text)
		print("av cid type: ", type(cid))

		save_cid_and_url(cid[0], url)
		# get bullet-screen comments part
		xml_link = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + cid[0] 
		print(xml_link)
		return get_request(xml_link),cid[0]
	else:
		print("wrong")

#获取url中有ep号的弹幕xml文件的网址
# input:视频网址
# output:xml网址请求的响应

def get_ep_bullet_xml(url):
	print('we enter the ep url')
	js_url ='https://bangumi.bilibili.com/view/web_api/season?ep_id='+url[url.find('ep')+2:]
	print(js_url)
	pageResponse = get_request(js_url)
	if pageResponse:		
		print("pageResponse.code:", pageResponse.json()['code'])				  #确保传入的响应内容不为空，保证程序正常运行
		cid = pageResponse.json()['result']['episodes'][0]['cid']
		cid = str(cid)
		print("ep cid type: ", type(cid))
		# cid强转str
		save_cid_and_url(str(cid), url)
		xml_link = "https://api.bilibili.com/x/v1/dm/list.so?oid=" + str(cid)
		print(xml_link)
		return get_request(xml_link), cid
	else: 
		print('we can not get access to js_url')



lock = Lock() #申明一个全局的lock对象
def analyze_result(result):

	# 格式所需
	cid = result[1]
	result = result[0]

	# requests
	#请求获取uid的接口
	analysisAPI_url = 'https://biliquery.typcn.com/api/user/hash/' + result[0].split(',')[6]
	api_response = get_request(analysisAPI_url)

	#	if count>3:
	#		break
	#将播放秒数转化为时：分：秒的格式
	#	else:
	global lock #引用全局锁
	global i
	global i_substract_flag

	lock.acquire() #申请锁


	# 既然i暂时不作为第几个解析成功的一个计数，那就暂时作为result的计数
	i += 1
	print("*****************")
	print("第", i, "个result")

	
	seconds = float(result[0].split(',')[0])
	m, s = divmod(seconds, 60)
	h, m = divmod(m, 60)
	play_time = "%d:%02d:%02d"%(h,m,s)

	#将发送时间的UNIX时间戳转化为年-月-日 时：分：秒格式

	time_local = time.localtime(int(result[0].split(',')[4]))
	dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)


	# 这里是经典的非空判断，事实上我上面在request加的代码就是非空判断，当然这里可以再加一重
	# 此处的判断是为了把多次访问全部失败的url收集起来
	if api_response:
		# print("api_response是：", api_response)

		if api_response.status_code != 200:		 #以防出现网络连接而后续程序中断的问题
			print(api_response.status_code)

			user = 'null' # TODO 

		else:
			if api_response.content:
				user_id = api_response.json()['data'][0]['id']	
			
				#弹幕内容、模式、大小、颜色
				pattern = result[0].split(',')[1]
				size = result[0].split(',')[2]
				color = hex(int(result[0].split(',')[3]))
				detail = result[1]


				#获取数据（uid,播放时间,发送时间，弹幕内容，弹幕长度，弹幕颜色，弹幕类型，cid）的元组
				url = get_url_from_cid(cid)
				element = {"id":i, "user_id":user_id,"play_time":play_time,
					"dt":dt,"lenth":len(detail),"pattern":pattern,
					"size":size,"color":color,"cid":cid,"detail":detail,"url":url}
				print(result)
				print(element)
				print("save_to_database")
				db_element = [element]
				save_to_database(db_element)

				global elements
				elements.append(element)

			else:
				print("api_response.content值为空，打印result:", result)
				print("api_response.content值为空，打印url:", analysisAPI_url)
	else:
		print("怎么api_response为空？？？不管了，先加到fail_results里面")
		global fail_results
		if not fail_results:
			fail_results = []
		# result重新组装
		fail_result = [result, cid]

		fail_results.append(fail_result)
		
		i -= 1 # 此处为了保证i是顺序的


	lock.release() #释放锁


# 解析弹幕文件，获取数据，元组形式
# input:请求xml网址的response文本
# output:以（uid,播放时间,发送时间，弹幕内容，弹幕类型，弹幕颜色，弹幕长度）元组为元素的列表
def parse_page(danmu):
	#将获取的XML弹幕文件写入本地
	if danmu:
		# 这里锁是为了让多进程分开在不同的文件夹里面，不用导致每个文件夹的东西不同
		global lock
		lock.acquire()
		# cid是重要每个视频的唯一标识
		cid = danmu[1] 
		print("cid type: ", type(cid))
		# 当前目录下建这个文件夹用来存所有的result, 文件夹用build_results + 时间
		time_local = time.localtime(time.time())
		dt = time.strftime("%m-%d %H-%M-%S",time_local)
		dir_name = "build_results"
		path_name = "build_results/" + dt + " cid_" + cid + '/'
		# 把path存起来
		save_path_with_cid(cid, path_name)
		# xml名字由bilibili + cid 组成
		xml_name = path_name + 'bilibili_cid_' + cid + '.xml'
		# 创建文件夹
		if not os.path.exists(dir_name):
			os.mkdir(dir_name)
		if not os.path.exists(path_name):
			os.mkdir(path_name)
		# 保存xml
		with open(xml_name,'wb') as f:
			f.write(danmu[0].content)

		

		# 处理参数，获取results
		html = etree.parse(xml_name,etree.HTMLParser())
		items = html.xpath('//d/@p')		   #获取弹幕参数
		content = html.xpath('//d/text()')	 #获取弹幕内容
		results = zip(items,content)		   #元组对应的列表形式

		lock.release()
		# 设定部分全局变量
		global elements		 # 用于存放解析成功的results
		global fail_results  # 解析失败的，需要重跑
		global i			 # index
		fail_results = []
		elements = []
		i = 0

		'''
		# 这里是队列，还没有做，暂时不知道需不需要
		# import queue
		# detail_url_queue = queue.Queue(maxsize=1000)
		'''

		# 这里构造list用于后面线程池，把result和对应的cid传进去，这里其实可以考虑用队列，
		# 就可以等队列来了再处理，处理好了丢进线程池这样，待定
		# TODO
		par_list = []
		for result in results:
			par_list.append([result, cid])


		# 设定result个数，用于调试
		par_list = par_list[0 : 10]

		# 线程池部分
		print('pool start')
		print('Results 个数：', len(par_list))
		pool = threadpool.ThreadPool(5) 

		requests = threadpool.makeRequests(analyze_result, par_list) 
		[pool.putRequest(req) for req in requests] 
		pool.wait() 
		print('pool End')

		# 线程池结束，开始说明目前fail的情况
		print("*----------------------------*")
		print("fail_results个数为: ", len(fail_results))
		print("分别为:")
		for fail_url in fail_results:
			print(fail_url)
		print("*----------------------------*")

		# 重跑次数
		RERUN_TIMES = 2 

		if fail_results:
			for j in range(1, RERUN_TIMES + 1):
				# 如果fail results没有，那就直接跳出循环。
				if not fail_results:
					print("All fail results are done. Congratulations!")
					break

				# 第一次重试
				print('pool start, ', j, 'st retry')
				
				retry = fail_results # 这里也是为了格式，threadpool要求传入的参数为list类型
				fail_results = [] # reset fail results
				pool = threadpool.ThreadPool(5) 

				requests = threadpool.makeRequests(analyze_result, retry) 
				[pool.putRequest(req) for req in requests] 
				pool.wait() 
				print('pool End, ', j, 'st retry')

				# 线程池结束，开始说明目前fail的情况
				print("*----------------------------*")
				print("经过retry, fail_results个数为: ", len(fail_results))
				print("分别为:")
				for fail_url in fail_results:
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
	cid = elements[0]['cid']
	# 获取之前保存的pathname
	path = get_path_from_cid(cid)
	print("cid type: ", type(cid))
	# cid强转str
	filename = str(cid) + '.txt'
	print(filename)
	filename = path + filename
	if not os.path.exists(path):
		print("理论上不可能没有这个文件夹，代码错误")
		os.mkdir(path)
	if not os.path.exists(filename):
		for user in user_list:
			with open(filename,'a') as file:
				file.write(user + '\n')
	else: 
		print('The txt file has exists!')

#将弹幕参数信息存入数据库
#input:解析XML后的数据
#output:插入数据后的danmu_parameter
def save_to_database(elements):	
	for element in elements:
		db = pymysql.connect(host = 'localhost',user='root',password='679243',port=3306, db='spiders')
		cursor = db.cursor()
		table = 'danmu_test'
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

	danmu = get_bullet_xml(url)
	elements = parse_page(danmu)
	# 非空判断，其实可以不加，不过因为elements如果网络爆炸了确实会空。。
	if elements:
		save_data(elements)


def reset_db():
	db = pymysql.connect(host = 'localhost',user='root',password='679243',port=3306, db='spiders')
	cursor = db.cursor()
	table = 'danmu_test'
	sql = 'TRUNCATE ' + table
	cursor.execute(sql)
	db.close()


#使用多进程POOL池
if __name__ == '__main__':

	urls = ['https://www.bilibili.com/bangumi/play/ep258620',
		'https://www.bilibili.com/bangumi/play/ep251076',
		'https://www.bilibili.com/video/av19390801/',
		'https://www.bilibili.com/video/av37866145/']
	# url = urls[0]
	# for url in urls:
	# 	main(url)
		# print(url)

	# 这里清database
	reset_db()

	# 这个是跑单进程
	# main(url)

	# url = 'https://www.baidu.com'
	# response = get_request(url)
	# print(response)

	# 这里跑多进程
	# '''
	pool = Pool(processes = 10)

	pool.map(main, urls)
	pool.close()
	pool.join()
	# '''


