#%%
import json
import time

# fundcode=open('fr.txt').read()
# fundcode=json.loads(fundcode)

# Use your picked fundcode file here. An example is provided.
fundcode=list(set(open('mfl2.txt').read().splitlines()))

import requests
import re

# http://fund.eastmoney.com/pingzhongdata/***.js

def getNetValue(fcode):
    url="http://fund.eastmoney.com/pingzhongdata/"+fcode+".js"
    count=3
    while count>0:
        try:
            res=requests.get(url).text
            break
        except:
            time.sleep(3)
            count-=1
    temp=re.search("(?<=Data_ACWorthTrend = ).*?(?=;)",res)
    if(temp):
        netValue=temp.group()
        return json.loads(netValue)
    else:
        return "[]"

def getValueSeries(data, st, et):
    stepDict={}
    for netValueKey in data:
        time=netValueKey[0]//86400000
        if(time>=st):
            stepDict[time]=netValueKey[1]
    for i in range(st, et):
        if(stepDict.get(i)):
            temp=stepDict[i]
            break

    #print(temp)
    for i in range(st, et):
        if(stepDict.get(i)):
            temp=stepDict[i]
        else:
            stepDict[i]=temp
    output=[]
    for i in range(st,et):
        output.append(stepDict[i])
    return output

def logGapRate(series,gap,rate):
    x=numpy.zeros(len(series)-gap)
    for i in range(len(series)-gap):
        x[i]=math.log(series[i+gap]/series[i])-math.log(rate)*gap/365
    return x

#%%
import numpy
import time
import math
import random

# Hyper parameters are set here
loopBackTime=1600
startTime=int(time.time()/86400-loopBackTime)
endTime=int(time.time()/86400)
gap=16

seriesArr=[]
fundcode_new=[]
for i in range(len(fundcode)):
    a=getNetValue(fundcode[i])
    if(a[0][0]//86400000<startTime):
        fundcode_new.append(fundcode[i])
        seriesArr.append(logGapRate(getValueSeries(a,startTime,endTime),gap,1.03))

fundcode=fundcode_new
#%%
n=len(seriesArr)
presevered=list(range(n))
Data=numpy.array(seriesArr)


test=1
while n>0 and test:
    test=0
    Cov=numpy.cov(Data)
    Mean=numpy.mean(Data,axis=1)
    L=numpy.linalg.cholesky(Cov)
    a0=numpy.dot(numpy.linalg.inv(L),Mean)
    tl=list(range(n))
    random.shuffle(tl)
    for i in tl:
        L1=numpy.delete(L,i,axis=0)
        u,s,vt=numpy.linalg.svd(L1)
        v=vt[-1,:]
        if(numpy.dot(a0,v)*numpy.dot(v,L[i,:])<0):
            presevered.pop(i)
            Data=numpy.delete(Data,i,axis=0)
            n-=1
            test=1
            break

Y=numpy.dot(numpy.linalg.inv(L),Mean)
X=numpy.dot(numpy.linalg.inv(L.T),Y)

Sharp=numpy.dot(Mean,X)/math.sqrt(numpy.dot(numpy.dot(X.T,Cov),X))
X=X/numpy.linalg.norm(X,ord=1)
print(n,numpy.dot(Mean,X)*365/gap,Sharp*math.sqrt(365/gap))
#%%

output={}
for i in range(len(presevered)):
    output[fundcode[presevered[i]]]=X[i]
Pa=sorted(output.items(), key=lambda d:d[1], reverse = True)
#Pa=output.items()


def str_count2(str):
    ans=0
    for s in str:
        # 中文字符范围
        if '\u4e00' <= s <= '\u9fff':
            ans+=1
    return ans

def printspace(n):
    for i in range(n):
        print(' ',end="")

fundfile=json.loads(open("fr.txt").read())
fundname={}
for fund in fundfile:
    fundname[fund[0]]=fund[2]
fundname['000000']="定期存款"

for x in list(Pa):
    name=fundname[str(x[0])]
    print('|',x[0],'|',name,end="")
    printspace(35-len(name)-str_count2(name))
    print('|', format(x[1]*100,' >5.2f'),'|')


# %%
