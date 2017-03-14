import time

class Timer(object):

   def __init__(self):
       self.start_time = time.time()
       self.stop_time = self.start_time
       self.elapsed = 0
       self.running = True

   def start(self):
       self.resume()

   def stop(self):
       self.stop_time = time.time()
       self.running = False
       self.elapsed = self.elapsed + (self.stop_time - self.start_time)

   def time(self):
       if (self.running):
           return self.elapsed + (time.time() - self.start_time)
       else:
           return self.elapsed

   def reset(self):
       self.elapsed = 0
       self.start_time = time.time()
       self.running = True

   def resume(self):
       if (self.running):
           #do nothing
           pass
       else:
           self.start_time = time.time()
           self.stop_time = time.time()
           self.running = True



if __name__ == '__main__':
    
    print "Starting timer..."
    t = Timer()
    time.sleep(20)

    print "Elapsed time after sleep of 20 secs : %s" %(t.time())
    t.stop()
    time.sleep(20)


    t.resume()
    time.sleep(5)
    print "Elapsed time after sleep of 20 + 5 secs : %s" %(t.time())
