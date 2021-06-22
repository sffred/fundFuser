#%%
import json

# fundcode=open('fr.txt').read()
# fundcode=json.loads(fundcode)

# Use your picked fundcode file here. An example is provided.
manualFundcode=open('mfl3.txt').read().splitlines()

fundcode=[]
for fc in manualFundcode:
    fundcode.append([fc])

import requests
import re
# http://fund.eastmoney.com/pingzhongdata/***.js

def getNetValue(fcode):
    url="http://fund.eastmoney.com/pingzhongdata/"+fcode+".js"
    res=requests.get(url).text
    temp=re.search("(?<=Data_ACWorthTrend = ).*?(?=;)",res)
    if(temp):
        netValue=temp.group()
        return netValue
    else:
        return "[]"

# Produce net-value dict

netValueDict={}

#%%
for fund in fundcode:
    netValueDict[fund[0]]=json.loads(getNetValue(fund[0]))
    print(fund[0],len(netValueDict[fund[0]]))
#    time.sleep(0.3)


#%%
import numpy
import time
import math

# Hyper parameters are set here
loopBackTime=400
startTime=int(time.time()/86400-loopBackTime)
endTime=int(time.time()/86400)
gap=16

def pretreatment(netValueList):
    stepDict={}
    for netValueKey in netValueList:
        time=int((netValueKey[0]+gap*3600000)/86400000)
        if(time>=startTime):
            stepDict[time]=netValueKey[1]
    for i in range(startTime, endTime):
        if(stepDict.get(i)):
            temp=stepDict[i]
            break

    #print(temp)
    for i in range(startTime, endTime):
        if(stepDict.get(i)):
            temp=stepDict[i]
        else:
            stepDict[i]=temp
    stepDict=dict(sorted(stepDict.items(), key=lambda d:d[0]))
    return stepDict


def stepData(stepDict):
    data={}
    for i in range(startTime, endTime-gap):
        temp=math.log(stepDict[i+gap]/stepDict[i])
        data[i]=temp
    return data

fundlist={}
for fund in netValueDict.items():
    if(len(fund[1])>loopBackTime):
        fundlist[fund[0]]=stepData(pretreatment(fund[1]))

seriesArr=[]

for fund in fundlist.items():
    temp=[]
    for time in range(startTime, endTime-gap):
        temp.append(fund[1][time])
    seriesArr.append(numpy.array(temp))

#%%
finalData=numpy.array(seriesArr)
dataCov=numpy.cov(finalData)
dataMean=numpy.mean(finalData,axis=1)-math.log(1.0323)*gap/365
L=numpy.linalg.cholesky(dataCov)
Y=numpy.dot(numpy.linalg.inv(L.T),numpy.dot(numpy.linalg.inv(L),dataMean))
Y=Y+abs(Y)
Y=Y/numpy.linalg.norm(Y,ord=1)

output={}
for i in range(len(fundlist)):
    output[list(fundlist.keys())[i]]=Y[i]
Pa=sorted(output.items(), key=lambda d:d[1], reverse = True)
#Pa=output.items()
#%%

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
