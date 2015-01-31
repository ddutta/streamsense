import sys
import string
import random
import subprocess
import hashlib
import re
import json
import datetime
import time
from collections import defaultdict
import datetime
import numpy
#import msvcrt as m

timeseries={}

def metrictimeseries(inputlist, numhashbits):
  global timeseries 
  numlines=0
  print "entering metrictimeseries:"+ str(datetime.datetime.now().time())
  for line in inputlist:
    temp = json.loads(line.strip())
    timestring = temp["timestamp"]
    timestamp = time.mktime(datetime.datetime.strptime(timestring[:-1], "%Y-%m-%dT%H:%M:%S").timetuple())
    id=str(temp["name"]) + ":"+str(temp["resource_id"])
    if id in timeseries.keys():
        timeseries[id].append([float(timestamp)*1000,float(temp["volume"])])
    else:
        timeseries[id]=[[float(timestamp)*1000,float(temp["volume"])]]
  j=0 
  for key in timeseries.keys():
     anomalyseries=[]
     anomalyseries = anomalydetect(key)
     if (len(anomalyseries) > 0):
       anomalykey = key+":anomaly"
       timeseries[anomalykey]=anomalyseries
       print "timeseries[anomalykey]="
       print timeseries[anomalykey]
     j=j+1
      
  print "finishing logreduce3:"+ str(datetime.datetime.now().time())
  print("completed processing postagged file")
  return timeseries


def anomalydetect(key):
  global timeseries
  anomalypoints=[]
  if (len(timeseries[key]) > 20):
     currtimeseries = []
     ntimeseries = numpy.zeros(len(timeseries[key]))
     currtimeseries.append([timeseries[key][0][0],0])
     for i in range(1,len(timeseries[key])):
        currtimeseries.append([timeseries[key][i][0], timeseries[key][i][1] - timeseries[key][i-1][1]])
        ntimeseries[i] = timeseries[key][i][1] - timeseries[key][i-1][1] 
     
        average = numpy.mean(ntimeseries)
        sd = numpy.std(ntimeseries)    
        DevWindowSize = 2
        RunningWindowSize = 20
        StdDevthresh = 2.5
        PrevWinDiffPercentThresh = 0.4 
     if (sd == 0):
        return anomalypoints 

     for i in range(20,len(ntimeseries)):
           windowaverage = numpy.mean(ntimeseries[i - RunningWindowSize + 1: i + 1]) 
           windowsd = numpy.std(ntimeseries[i - RunningWindowSize + 1: i + 1]) 
           
           devwindowaverage = numpy.mean(ntimeseries[i - DevWindowSize + 1: i + 1])
           prevdevwindowaverage = numpy.mean(ntimeseries[max(0,i - 2*DevWindowSize + 1): i -DevWindowSize + 1])
 
           if ((abs(devwindowaverage - windowaverage) > StdDevthresh*windowsd) and 
             (abs(devwindowaverage - prevdevwindowaverage) > PrevWinDiffPercentThresh*windowaverage) and
             (abs(devwindowaverage - prevdevwindowaverage) > PrevWinDiffPercentThresh*prevdevwindowaverage)):
                print str(i) +" anomaly: dwaverage is:" + str(devwindowaverage) + "avg,std="+str(windowaverage) +","+str(windowsd)
                anomalypoints.append(timeseries[key][i])
     print "avg,std="+str(windowaverage) +","+str(windowsd) 
     #timeseries[key]=currtimeseries
  return anomalypoints 


if __name__ == '__main__':
  if (len(sys.argv) < 5):
    print "python logreducestream.py inputfile stopwordsfile numhashbits"
    sys.exit(0)
  
  inputfile = sys.argv[1]
  outputfile = sys.argv[2]
  stopwordsfile = sys.argv[3]
  numhashbits = int(sys.argv[4])

  sys.exit(0)


 
