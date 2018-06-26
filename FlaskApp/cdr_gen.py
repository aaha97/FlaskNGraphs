#cdr_gen
from datetime import datetime, timedelta,date,time
from dateutil import parser
import random
import pandas as pd
import sys
def gen_phone():
    first = str(random.randint(100,999))
    second = str(random.randint(1,888)).zfill(3)
    last = (str(random.randint(1,9998)).zfill(4))
    while last in ['1111','2222','3333','4444','5555','6666','7777','8888']:
        last = (str(random.randint(1,9998)).zfill(4))

    return '{}-{}-{}'.format(first,second, last)
def create_actors(n):
	A = [gen_phone() for _ in xrange(n)]
	return A
def create_relations(date_from,date_to,m):
	date_from = parser.parse(date_from)
	date_to = parser.parse(date_to)
	dx = (date_to - date_from).total_seconds()
	#dx1h = timedelta(seconds=3600).total_seconds()
	#R1 = [(date_from+timedelta(seconds=random.random()*dx)) for _ in xrange(m)]
	#R2 = [(R1[i]+timedelta(seconds=random.random()*dx1h)) for i in xrange(m)]
	R = [(date_from+timedelta(seconds=random.random()*dx)) for _ in xrange(m)]
	R1 = [i.date() for i in R]
	R2 = [i.time() for i in R]
	return [R1,R2]

def create_tuples(n, m, date_from, date_to):
	actors = create_actors(n)
	relations1,relations2 = create_relations(date_from,date_to,m)
	T = []
	for i in xrange(m):
		p = (random.randint(0,n-1))/2
		q = p
		while q==p:
			q = random.randint(0,n-1)
		a = actors[p]
		b = actors[q]
		#T.append([a,b,relations1[i].isoformat(),relations2[i].isoformat()])
		T.append([a,b,str(relations1[i]),str(relations2[i])])
	return T
n = int(sys.argv[3])
m = int(sys.argv[4])
for rec in range(int(sys.argv[2])-int(sys.argv[1])):
	table = create_tuples(n,m,'2017-01-01T00:00:00','2018-01-01T00:00:00')
	df = pd.DataFrame(table)
	#df.columns = ['from','to','call_start','call_end']
	df.columns = ['calling','called','date','time']
	df.to_csv("cdr"+str(int(sys.argv[1])+rec)+".csv",index=False)