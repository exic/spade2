
import stack_thread
#import thread
import time
#import mymod

def run():
	while 1:
		print "run"
		time.sleep(1)

#print thread.start_new_thread(run,())
#print stack_thread._start_new_thread(run,(),1024)
#print mymod.snt(run,(), 10204)
i = 0
#while 1:
stack_thread.start_new_thread(run,(),10240000)
print i
i = i+1

while 1:
	time.sleep(1)

