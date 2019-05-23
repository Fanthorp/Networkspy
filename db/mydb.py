# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 11:07:29 2019

@author: levin
"""

import pymysql

class Mydb(object):
    def __init__(self, host, user, passwd, dbName):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbName = dbName
    
    def connect(self):
        self.db = pymysql.Connect(self.host, self.user, self.passwd, self.dbName)
        self.cursor = self.db.cursor()
    
    def close(self):
        self.cursor.close()
        self.db.close()
        
    def get_one(self, sql):
        res = None
        try:
            self.connect()
            self.cursor.execute(sql)
            res = self.cursor.fetchone()
            self.close()
        except:
            print("查询失败")
        return res
    
    def get_all(self, sql):
        res = ()
        try:
            self.connect()
            self.cursor.execute(sql)
            res = self.cursor.fetchall()
            self.close()
        except:
            print("查询失败")
        return res    
    
    def __edit(self, sql):
        count = 0
        try:
            self.connect()
            count = self.cursor.execute(sql)
            self.db.commit()
            self.close()
        except:
            print("提交失败")
            self.db.rollback()
    
    def insert(self, sql):
        return self.__edit(sql)
    
    def delete(self, sql):
        return self.__edit(sql)
    
    def update(self, sql):
        return self.__edit(sql)
    
