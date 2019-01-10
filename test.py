import time
from multiprocessing import Pool
import os

def run(fn) :
  time.sleep(2)
  print (fn)
if __name__ == "__main__" :
    startTime = time.time()
    testFL = [1,2,3,4,5]
    for i in testFL:
        print(i)
    print(len(testFL))

    path = "test"
    os.chdir(path)
  # pool = Pool(10)#可以同时跑10个进程
  # pool.map(run,testFL)
  # pool.close()
  # pool.join()   
  # endTime = time.time()
  # print ("time :", endTime - startTime)



  GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER ON spider.* TO spider@localhost IDENTIFIED BY '679243';

