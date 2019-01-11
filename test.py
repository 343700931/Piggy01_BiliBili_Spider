import time
from multiprocessing import Pool
import os
import requests

def run() :

	response = requests.get("https://www.baidu.com")
	print(response)
	time.sleep(2)

if __name__ == "__main__" :
	# startTime = time.time()
	# testFL = [1,2,3,4,5]
	# for i in testFL:
	# 	print(i)
	# print(len(testFL))
	run()

	# a = []
	# b = [a]
	# if a:
	# 	print("hello")

	# if b:
	# 	print('hi')

	# if b[0]:
	# 	print("c")







	'''
	path = "test"
	# os.chdir(path)
	if not os.path.exists("test"):
		os.mkdir('test')
	xml_name = 'test/bilibili_cid_1' + '.xml'
	string = 'hello'
	string = string.encode()
	with open(xml_name,'wb') as f:
		f.write(string)
		f.close()
	# pool = Pool(10)#可以同时跑10个进程
	# pool.map(run,testFL)
	# pool.close()
	# pool.join()   
	'''
	'''

	time_local = time.localtime(time.time())
	dt = time.strftime("%m-%d %H-%M-%S",time_local)
	print(dt)
	dir_name = "build_results"
	path_name = "build_results/" + dt
	cid = '11111'
	# xml名字由bilibili + cid 组成
	xml_name = dir_name + '/' + 'bilibili_cid_' + cid + '.xml'
	# 创建文件夹
	if not os.path.exists(dir_name):
		os.mkdir(dir_name)
	if not os.path.exists(path_name):
		os.mkdir(path_name)

	# print ("time :", endTime - startTime)


	'''