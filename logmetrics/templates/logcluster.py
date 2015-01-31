import sys
import string
import random
import subprocess
import hashlib
import re
import json
from collections import defaultdict
import datetime
import time

def simhash(tokens, hashbits=64):
   if hashbits > 64: hashbits = 64

   v = [0]*hashbits

   #for t in [x.__hash__() for x in tokens]:
   for t in [string_hash(x) for x in tokens]:
       bitmask = 0
       for i in xrange(hashbits):
           bitmask = 1 << i
           if t & bitmask:
               v[i] += 1
           else:
               v[i] -= 1

   fingerprint = 0

   for i in xrange(hashbits):
       if v[i] >= 0:
           fingerprint += 1 << i

   return fingerprint



def similarity(a, b, hashbits=64):
   # Use Hamming Distance to return % of similar bits
   x = (a ^ b) & ((1 << hashbits) - 1)
   tot = 0
   while x:
       tot += 1
       x &= x-1
   return float(hashbits-tot)/hashbits

def string_hash(v):
   #return int(hashlib.sha384(v).hexdigest(), 16)
   return int(hashlib.md5(v).hexdigest(), 16)

def logcluster(inputfile, outputfile, stopwords, numhashbits):
  slist = open(stopwords,"r")
  stopwords = {}
  lines = slist.readlines()
  for line in lines:
    words = line.rstrip('\n')
    stopwords[words]=1
    slist.close()

  unigrams=[]
  numlines=0
  clusterid=0
  clusterdict={}
  lshlist = defaultdict(list)

  inputf = open(inputfile, "r")
  outputf = open(outputfile,"w")
  line = inputf.readline()
  while line:
    unigrams=[]
    log = line.rstrip('\n').rstrip('\r')
    js = json.loads(log)
    message = js["message"]
    timestamp = js["@timestamp"]
    host = js["path"]
    path = js["path"]
    words = re.split(' ',message)
    for x in words:
      y = x.lower().rstrip('?,!,.,:,;,\',\",\,').lstrip('?,!,.,:,;,\',\",\,')
      if ((str(y) != "") and (y not in stopwords)):
          unigrams.append(y)

    origlog = " ".join(unigrams)
    #hashval = simhash(origlog, 48)
    hashval = simhash(origlog, numhashbits)
    if hashval not in clusterdict:
        clusterdict[hashval]=clusterid
        clusterid = clusterid + 1
    newlog = log[:-1]+',"clusterid":"'+str(clusterdict[hashval])+'"}'
    outputf.write(newlog +"\n")
    line = inputf.readline()
    numlines = numlines + 1
    #if (numlines > 10000):
    #    print("numlines is"+str(numlines))
    #if (numlines%1000 == 0):
    #print("finished batch of 1000:" + str(numlines))
  outputf.close()
  print("completed processing postagged file")
  print("size of lshlist is "+str(len(clusterdict)))

def log_cluster_old(inputlist, stopwords, numhashbits):
  slist = open(stopwords,"r")
  stopwords = {}
  lines = slist.readlines()
  for line in lines:
    words = line.rstrip('\n')
    stopwords[words]=1
    slist.close()

  unigrams=[]
  numlines=0
  clusterid=0
  clusterdict={}
  lshlist = defaultdict(list)


  output = []
  for line in inputlist:
    unigrams=[]
    log = line.rstrip('\n').rstrip('\r')
    js = json.loads(log)
    message = js["message"]
    timestamp = js["@timestamp"]
    host = js["path"]
    path = js["path"]
    words = re.split(' ',message)
    for x in words:
      y = x.lower().rstrip('?,!,.,:,;,\',\",\,').lstrip('?,!,.,:,;,\',\",\,')
      if ((str(y) != "") and (y not in stopwords)):
          unigrams.append(y)

    origlog = " ".join(unigrams)
    #hashval = simhash(origlog, 48)
    hashval = simhash(origlog, numhashbits)
    if hashval not in clusterdict:
        clusterdict[hashval]=clusterid
        clusterid = clusterid + 1
    newlog = log[:-1]+',"clusterid":"'+str(clusterdict[hashval])+'"}'
    output.append(newlog)
    numlines = numlines + 1
    #if (numlines > 10000):
    #    print("numlines is"+str(numlines))
    #if (numlines%1000 == 0):
    #print("finished batch of 1000:" + str(numlines))
  print("completed processing postagged file")
  print("size of lshlist is "+str(len(clusterdict)))
  return output


def log_cluster(inputlist, stopwords, numhashbits):
  slist = open(stopwords,"r")
  stopwords = {}
  lines = slist.readlines()
  for line in lines:
    words = line.rstrip('\n')
    stopwords[words]=1
    slist.close()

  unigrams=[]
  numlines=0
  clusterid=0
  clusterdict={}
  lshlist = defaultdict(list)
  print "entering logreduce2:"+ str(datetime.datetime.now().time())
  output = []
  for line in inputlist:
    unigrams=[]
    log = line.rstrip('\n').rstrip('\r')
    js = json.loads(log)
    message = js["message"]
    timestamp = js["@timestamp"]
    timeval = time.mktime(datetime.datetime.strptime(timestamp[:-1], "%Y-%m-%dT%H:%M:%S.%f").timetuple())
    host = js["path"]
    path = js["path"]
    #words = re.split(' ',message)
    words = re.split('[ ()\-:,]',message)
    for x in words:
      y = x.lower().rstrip('?,!,.,:,;,\',\",\,').lstrip('?,!,.,:,;,\',\",\,')
      if ((str(y) != "") and (y not in stopwords)):
          unigrams.append(y)

    #origlog = " ".join(unigrams)
    #hashval = simhash(origlog, 48)
    #hashval = simhash(origlog, numhashbits)
    hashval = simhash(unigrams, numhashbits)
    if hashval not in clusterdict:
        clusterdict[hashval]=clusterid
        clusterid = clusterid + 1
    sortval = str(clusterdict[hashval])+"."+str(int(timeval))
    #newlog = log[:-1]+',"clusterid":"'+str(clusterdict[hashval])+'"}'
    newlog = log[:-1]+',"clusterid":"'+str(clusterdict[hashval])+'"' +',"sortfield":"'+sortval +'"}'
    output.append(newlog)
    numlines = numlines + 1
    #if (numlines > 10000):
    #    print("numlines is"+str(numlines))
    #if (numlines%1000 == 0):
    #print("finished batch of 1000:" + str(numlines))
  print "finishing logreduce3:"+ str(datetime.datetime.now().time())
  print("completed processing postagged file")
  print("size of lshlist is "+str(len(clusterdict)))
  return output



if __name__ == '__main__':
  if (len(sys.argv) < 5):
    print "python logreducestream.py inputfile stopwordsfile numhashbits"
    sys.exit(0)
  
  inputfile = sys.argv[1]
  outputfile = sys.argv[2]
  stopwordsfile = sys.argv[3]
  numhashbits = int(sys.argv[4])

  logreduce(inputfile, outputfile, stopwordsfile, numhashbits)
  sys.exit(0)


 
