# -*- coding: utf-8 -*-
"""
Created on Fri Jan 11 17:50:29 2019

@author: levin
"""
__date__ = '2018/5/31 22:27'

import time
import struct
import socket
import select
import sys
from threading import Thread

class Icmp(object):
    def __init__(self,host,count=5):
        self.host = host
        self.count = count 

    def chesksum(self,data):
        """
        校验
        """
        n = len(data)
        m = n % 2
        sum = 0 
        for i in range(0, n - m ,2):
            sum += (data[i]) + ((data[i+1]) << 8)
        if m:
            sum += (data[-1])
        #将高于16位与低16位相加
        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16) #如果还有高于16位，将继续与低16位相加
        answer = ~sum & 0xffff
        #主机字节序转网络字节序列（参考小端序转大端序）
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer 

        '''
        连接套接字,并将数据发送到套接字
        '''
    def raw_socket(self,dst_addr,imcp_packet):
        rawsocket = socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.getprotobyname("icmp"))
        send_request_ping_time = time.time()
        #send data to the socket
        rawsocket.sendto(imcp_packet,(dst_addr,80))
        return send_request_ping_time,rawsocket,dst_addr

        '''
        request ping
        '''
    def request_ping(self,data_type,data_code,data_checksum,data_ID,data_Sequence,payload_body):
        #把字节打包成二进制数据
        imcp_packet = struct.pack('>BBHHH32s',data_type,data_code,data_checksum,data_ID,data_Sequence,payload_body)
        icmp_chesksum = self.chesksum(imcp_packet)#获取校验和
        imcp_packet = struct.pack('>BBHHH32s',data_type,data_code,icmp_chesksum,data_ID,data_Sequence,payload_body)
        return imcp_packet

        '''
        reply ping
        '''
    def reply_ping(self,send_request_ping_time,rawsocket,data_Sequence,timeout = 1.5):
        while True:
            started_select = time.time()
            what_ready = select.select([rawsocket], [], [], timeout)
            wait_for_time = (time.time() - started_select)
            if what_ready[0] == []:  # Timeout
                return -1
            time_received = time.time()
            received_packet, addr = rawsocket.recvfrom(1024)
            icmpHeader = received_packet[20:28]
            type, code, checksum, packet_id, sequence = struct.unpack(
                ">BBHHH", icmpHeader
            )
            if type == 0 and sequence == data_Sequence:
                return time_received - send_request_ping_time
            timeout = timeout - wait_for_time
            if timeout <= 0:
                return -1

        '''
        实现 ping 主机/ip
        '''
    def ping(self,host):
        ping_time_list = []
        data_type = 8 # ICMP Echo Request
        data_code = 0 # must be zero
        data_checksum = 0 # "...with value 0 substituted for this field..."
        data_ID = 0 #Identifier
        data_Sequence = 1 #Sequence number
        payload_body = b'abcdefghijklmnopqrstuvwabcdefghi' #data
        dst_addr = socket.gethostbyname(host)
        #
        for i in range(0,self.count):
            icmp_packet = self.request_ping(data_type,data_code,data_checksum,data_ID,data_Sequence + i,payload_body)
            send_request_ping_time,rawsocket,addr = self.raw_socket(dst_addr,icmp_packet)
            times = self.reply_ping(send_request_ping_time,rawsocket,data_Sequence + i)
            if times > 0:
                print("来自 {0} 的回复: 字节=32 时间={1}ms".format(addr,int(times*1000)))
                #ping_time_list.append(int(times*1000))
                time.sleep(0.1)
            else:
                print("time out")
                ping_time_list.append(0)
        return ping_time_list

    def fping(self):
        ping_time_list = []
        data_type = 8
        data_code = 0
        data_checksum = 0
        data_ID = 0
        data_Sequence = 1
        payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'
        dst_addr = socket.gethostbyname(self.host)
        
        icmp_packet = self.request_ping(data_type,data_code,data_checksum,data_ID,data_Sequence ,payload_body)
        send_request_ping_time,rawsocket,addr = self.raw_socket(dst_addr,icmp_packet)
        times = self.reply_ping(send_request_ping_time,rawsocket,data_Sequence)
        if times > 0:
            return 1 
        else:
            return 0


    def runping(host):
        global dict1
        res = ping(host)
        return dict1.update({host:res})



if __name__ == "__main__":
    list1 = ["202.85.215.3","202.85.215.2","202.85.215.1","202.85.215.147"]
    p = Icmp("202.85.215.1")
    dict1 = {}
    stime = time.time()
    res = p.fping()
    print(res)
'''    
    threads = []
    for i in list1:
        thread = Thread(target=p.runping, args=(i,))
        thread.start()   
        threads.append(thread)
    
    for thread in threads:
        thread.join()
    
    
    print(time.time() - stime)
    
    print(dict1)
'''
