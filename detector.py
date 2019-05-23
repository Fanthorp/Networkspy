# -*- coding: utf-8 -*-

'''

author: Fanthorp
function: get Host state by ping check

'''

from db.mydb import Mydb
from icmp.icmp import Icmp
from threading import Thread
import datetime

class RunDetect(object):
    def __init__(self,detectId,dbHost,dbUser,dbPass,dbName):
        self.detectId = detectId
        self.dbHost = dbHost
        self.dbUser = dbUser
        self.dbPass = dbPass
        self.dbName = dbName
        self.targetHost = []
        self.detectResult = []
        self.db = Mydb(self.dbHost,self.dbUser,self.dbPass,self.dbName)

    def getTargetHost(self):
        sql = 'select HostList.IPAddr,PingTaskList.ID from PingTaskList inner join HostList  on HostList.Id=PingTaskList.TargetHost;'
        for row in self.db.get_all(sql):
            self.targetHost.append(row)

    def runPing(self,taskid,host):
        checkObject = Icmp(host,1)
        ctime = datetime.datetime.now().strftime("%Y-%m-%d %X")
        state = checkObject.fping()
        t = (taskid,state,ctime)
        self.detectResult.append(t)
        

    def checkHost(self):
        threads = []
        for row in self.targetHost:
            ID = row[1]
            tHost = row[0]
            thread = Thread(target=self.runPing,args=(ID,tHost))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def updateTask(self):
        for row in self.detectResult:
            sql = 'update PingTaskList set CurrentState=' + str(row[1]) + ',LastDetectTime=' + "'" + row[2] + "'" +  ' where ID=' + str(row[0]) +';'
            #sql = 'update PingTaskList set CurrentState=5 where ID=3;'
            self.db.update(sql)
            #print(sql)



if __name__ == "__main__":
    task = RunDetect(1,"localhost","root","Yskjmonitor365#^%","networkspy")
    res = task.getTargetHost()
    #print(task.targetHost)
    task.checkHost()
    task.updateTask()
    #print(task.detectResult)





