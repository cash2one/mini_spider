#coding=utf-8
import os,sys
import threading
import Queue
import time

job_queue = Queue.Queue()
job_queue.put('http://www.baidu.com')
job_queue.put('http://www.baidu.com')
job_queue.put('http://www.baidu.com')
job_queue.put('http://www.baidu.com')
job_queue.put('http://www.baidu.com')
job_queue.put('http://www.baidu.com')
job_queue.put('http://www.baidu.com')

class WorkManager(object):
	def __init__(self, thread_num):
		self.threads = []
		self.__init_thread_pool(thread_num)
	
	def __init_thread_pool(self, thread_num):
		global job_queue
		for i in range(thread_num):
			self.threads.append(WorkThread(i, job_queue))
	
	def wait_all_complete(self):
		for work in self.threads:
			if work.isAlive():
				work.join()

class WorkThread(threading.Thread):
	def __init__(self, thread_idx, job_queue):
		threading.Thread.__init__(self)
		print "Initiate thread %s"%(thread_idx)
		self._queue = job_queue
		self.idx = thread_idx
		self.start()

	def run(self):
		retry = 5
		while retry:
			try:
				print "Thread_num:%s, Getting data"%(self.idx)
				job = self._queue.get(block=True,timeout=5)
				
				print "Thread_num:%s, Doing job:%s"%(self.idx, job)
				self._queue.task_done()
			except:
				print "THread_num:%s, Sleep 5 seconds"%(self.idx)
				retry -= 1
				time.sleep(5)
				

manager = WorkManager(8)
manager.wait_all_complete()
print "All_job_done"
