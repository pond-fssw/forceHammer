# -*- coding: utf-8 -*-
"""
Created on Fri Sep  4 12:26:57 2020

@author: nicol
"""


# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 19:49:56 2020

@author: nicol
"""


import numpy as np
import time
import os
import tqdm as _tqdm
import pyvisa as _visa
import serial 
import nidaqmx

#Notes
#1. Axis pattern - 01 for X axis, 03 for XY and 07 for XYZ 
#rc3 = TTA.write('!9923307000000@@') #Notes: 07 stands for 111 on the axis pattern, Origin Return 
#rc4 = TTA.write('!9923403001E001E012C000493E0000493E0@@') #Move axis 1 and Axis 2 to 300 mm 
#'!      99      234   03               001E          001E          012C        000493E0    000493E0    @@' #Move axis 1 and Axis 2 to 300 mm
#'Header Station  ID   Axis Pattern  Acceleration   Deceleration   Velocity    X location  Y location  Checksum 
#'Header Station  ID   Axis Pattern       30            30           300         300 000      300 000  Checksum 

#Notes on axis status 
#status2 = Move_XY(TTA,30,30,300,300000,300000)
# When not in use '#9921207 1C000000    000493E01C000000000493E01C0000000000C35032\r\n'
# When in use     '#9921207 0D000000    000382F50D000000000383070D0000000000C35025\r\n' 


def padhexa4(s):
    return s.zfill(4)

def padhexa8(s):
    return s.zfill(8)

def Servo_on(inst):
    servo_stat = inst.query('!99232071@@')
    time.sleep(1)
    
def Servo_off(inst):
    servo_stat = inst.query('!99232070@@')
    time.sleep(1)

def Move_XYZ_laser(inst,acc,dcl,vel,X_start,Y_start,X_end,Y_end,Z,delay,CL3000,divisions):
   
    resultList = []
    timer = 0
    total = 0
    Xlist = np.linspace(X_start, X_end,4)
    Ylist = np.linspace(Y_start, Y_end,4)
    for i in range(divisions):
        acc_str = padhexa4(hex(acc).split('x')[-1])
        dcl_str = padhexa4(hex(dcl).split('x')[-1])
        vel_str = padhexa4(hex(vel).split('x')[-1])
        X_str = padhexa8(hex(int(Xlist[i])).split('x')[-1])
        Y_str = padhexa8(hex(int(Ylist[i])).split('x')[-1])
        Z_str = padhexa8(hex(Z).split('x')[-1])
        move_str = '!9923407'+acc_str+dcl_str+vel_str+X_str+Y_str+Z_str+'@@'
        move_stat = inst.query(move_str)
        axis_status = inst.query('!9921207@@')
        
        d1 = time.time()
        CL3000.write(b'NS,0,10000000\r')
        while axis_status[40] == '0':
            axis_status = inst.query('!9921207@@')
            if axis_status[40] == '1':
                break
        
        CL3000.write(b'NT\r')
        d2 = time.time()
        timer = timer + d2 - d1
        while True:
            total = total + 1
            resultList.append(CL3000.read_until(b'\r'))
            try:
                if 'NT' in resultList[-1].decode('UTF-8'):
                    break
                if resultList[-1].decode('UTF-8') == '':
                    break
            except:
                continue
    time.sleep(delay)
    return resultList, timer, total

def Move_XYZ(inst,acc,dcl,vel,X,Y,Z,delay):

    acc_str = padhexa4(hex(acc).split('x')[-1])
    dcl_str = padhexa4(hex(dcl).split('x')[-1])
    vel_str = padhexa4(hex(vel).split('x')[-1])
    X_str = padhexa8(hex(X).split('x')[-1])
    Y_str = padhexa8(hex(Y).split('x')[-1])
    Z_str = padhexa8(hex(Z).split('x')[-1])
    move_str = '!9923407'+acc_str+dcl_str+vel_str+X_str+Y_str+Z_str+'@@'
    move_stat = inst.query(move_str)
    axis_status = inst.query('!9921207@@')

    while axis_status[40] == '0':
        axis_status = inst.query('!9921207@@')
        if axis_status[40] == '1':
            break

    time.sleep(delay)
       
def Home(inst):
    move_stat = inst.query('!9923307000000@@')
    axis_status = inst.query('!9921207@@')
    while axis_status[40] == '0':
        axis_status = inst.query('!9921207@@')
        if axis_status[40] == '1':
            break
    
    

def Move_XY(inst,acc,dcl,vel,X,Y,delay):

    acc_str = padhexa4(hex(acc).split('x')[-1])
    dcl_str = padhexa4(hex(dcl).split('x')[-1])
    vel_str = padhexa4(hex(vel).split('x')[-1])
    X_str = padhexa8(hex(X).split('x')[-1])
    Y_str = padhexa8(hex(Y).split('x')[-1])
    move_str = '!9923403'+acc_str+dcl_str+vel_str+X_str+Y_str+'@@'
    move_stat = inst.query(move_str)
    axis_status = inst.query('!9921207@@')

    while axis_status[40] == '0':
        axis_status = inst.query('!9921207@@')
        if axis_status[40] == '1':
            break

    time.sleep(delay)

def Single(inst,acc,dcl,vel,X,Y,Z1,Z2,delay,num): 
    while num>=0:
        num = num-1
        Move_XYZ(inst,acc,dcl,vel,X,Y,Z1,delay)
        Move_XYZ(inst,acc,dcl,vel,X,Y,Z2,delay)
        
        
def SingleX(inst,acc,dcl,vel,X1,X2,Y,Z,delay,num): 
    while num>=0:
        num = num-1
        Move_XYZ(inst,acc,dcl,vel,X1,Y,Z,delay)
        Move_XYZ(inst,acc,dcl,vel,X2,Y,Z,delay)
        
def SingleY(inst,acc,dcl,vel,X,Y1,Y2,Z,delay,num): 
    while num>=0:
        num = num-1
        Move_XYZ(inst,acc,dcl,vel,X,Y1,Z,delay)
        Move_XYZ(inst,acc,dcl,vel,X,Y2,Z,delay)

def Single_with_charge_collection(inst1,inst2,acc,dcl,vel,X,Y,Z1,Z2,delay,num,Gain,Cap,horiz_scale,force_scale,charge_scale): 
    
    Force_Con = 19.31e-3 
    run_rigol(inst2)
    trigger_mode(inst2,'SINGle') #Set trigger mode 
    trigger_type(inst2,'EDGE') #Set Edge trigger mode 
    trigger_source(inst2,2) #Set Trigger on Channel #2                 
    time_base_scale(inst2, horiz_scale) #Set Horizontal Timebase 
    channel_scale(inst2,1,force_scale)
    channel_scale(inst2,2,charge_scale)

    while num>=0:
        num = num-1
        Move_XYZ(inst1,acc,dcl,vel,X,Y,Z1,delay)
        Move_XYZ(inst1,acc,dcl,vel,X,Y,Z2,delay)

    (time_ch1, V1) = get_data(inst2,1) 
    (time_ch2, V2) = get_data(inst2,2) 

    Force = (V1[1:-1]-V1[0])/Force_Con
    Q = V2[1:-1]*Cap/Gain

    return time_ch1[0:-1],Force,time_ch2[0:-1],Q

def Array(inst,acc,dcl,vel,C1_X,C2_X,C1_Y,C2_Y,Z1,Z2,delta_X,delta_Y,delay):
    num_X = (C2_X-C1_X)/delta_X +1
    num_Y = (C2_Y-C1_Y)/delta_Y +1 
    X_arr = np.linspace(C1_X,C2_X,num_X)
    Y_arr = np.linspace(C1_Y,C2_Y,num_Y)
    print(int(X_arr[0]))

    for i in range(len(X_arr)):
        for j in range(len(Y_arr)):
             Move_XYZ(inst,acc,dcl,vel,int(X_arr[i]),int(Y_arr[j]),Z1,delay)
             Move_XYZ(inst,acc,dcl,vel,int(X_arr[i]),int(Y_arr[j]),Z2,delay)
             Move_XYZ(inst,acc,dcl,vel,int(X_arr[i]),int(Y_arr[j]),Z1,delay)
             
def scanning_peak_detect(inst1,inst2,inst3,acc,dcl,vel,X,Y,Z,delay,freq,V_app,deltaY,step):
    min_Y = Y-deltaY
    max_Y = Y+deltaY
    Y_list = np.arange(min_Y,max_Y,step)
    V_list = []
    channel_on(inst3,1)
    time.sleep(5)
    for i in range(len(Y_list)):
        channel_scale(inst2,1,V_app/6)
        channel_scale(inst2,2,0.2)
        Servo_on(inst1)
        Move_XYZ(inst1,acc,dcl,vel,X,Y_list[i],Z,delay)
        Servo_off(inst1)
        run_rigol(inst2)
        wave(inst3,1,'SINE',freq,V_app)
        channel_on(inst3,1)
        time.sleep(0.2)
        trigger_mode(inst2,'SINGle') #Set trigger mode 
        (time_ch2, data_ch2) = get_data(inst2,2)
        Vpp = np.max(data_ch2[1:-1])-np.min(data_ch2[1:-1])
        V_list.append(Vpp)
        
    channel_off(inst3,1)
    scan_peak = Y_list[np.argmax(V_list)]
    Servo_on(inst1)
    return scan_peak 
        
def Meas_displacement(inst1,inst2,inst3,acc,dcl,vel,X,Y,Z,delay,freq_list,V_app):
    V_list = []
    Move_XYZ(inst1,acc,dcl,vel,X,Y,Z,delay)
    scan_peak = scanning_peak_detect(inst1,inst2,inst3,acc,dcl,vel,X,Y,Z,delay,10000,V_app,700,100)
    Move_XYZ(inst1,acc,dcl,vel,X,scan_peak,Z,delay)
    Servo_off(inst1)
    channel_on(inst3,1)
    time.sleep(5)
    for i in range(len(freq_list)): 
        channel_scale(inst2,1,V_app/6)
        if i == 0: 
            channel_scale(inst2,2,0.1)
        else:
            channel_scale(inst2,2,3)
        run_rigol(inst2)
        wave(inst3,1,'SINE',freq_list[i],V_app)
        channel_on(inst3,1)
        time.sleep(0.2)
        trigger_mode(inst2,'SINGle') #Set trigger mode 
        (time_ch2, data_ch2) = get_data(inst2,2)
        Vpp = np.max(data_ch2[1:-1])-np.min(data_ch2[1:-1])
        V_list.append(Vpp)
    
    channel_off(inst3,1)
    Servo_on(inst1)
    return V_list 
                 
def scanning_peak_detect_PDUS(inst1,inst2,inst3,acc,dcl,vel,X,Y,Z,delay,freq,V_app,deltaY,step):
    min_Y = Y-deltaY
    max_Y = Y+deltaY
    Y_list = np.arange(min_Y,max_Y,step)
    V_list = []
    output_enable(inst3)
    set_output_p2p(inst3,V_app)
    load_power(inst3,210000)
    set_output_freq(inst3,freq)
    time.sleep(5)
    channel_scale(inst2,1,2)
    channel_scale(inst2,2,0.2)
    for i in range(len(Y_list)):
        Servo_on(inst1)
        Move_XYZ(inst1,acc,dcl,vel,X,Y_list[i],Z,delay)
        Servo_off(inst1)
        run_rigol(inst2)
        time.sleep(0.2)
        trigger_mode(inst2,'SINGle') #Set trigger mode 
        (time_ch2, data_ch2) = get_data(inst2,2)
        Vpp = np.max(data_ch2[1:-1])-np.min(data_ch2[1:-1])
        V_list.append(Vpp)

    output_disable(inst3)
    scan_peak = Y_list[np.argmax(V_list)]
    Servo_on(inst1)
    return scan_peak 

def Meas_displacement_PDUS(inst1,inst2,inst3,acc,dcl,vel,X,Y,Z,delay,freq_list,V_app):
    V_list = []
    Move_XYZ(inst1,acc,dcl,vel,X,Y,Z,delay)
    scan_peak = scanning_peak_detect_PDUS(inst1,inst2,inst3,acc,dcl,vel,X,Y,Z,delay,25000,V_app,700,100)
    Move_XYZ(inst1,acc,dcl,vel,X,scan_peak,Z,delay)
    Servo_off(inst1)
    output_enable(inst3)
    set_output_p2p(inst3,V_app)
    load_power(inst3,210000)
    time.sleep(5)
    for i in range(len(freq_list)): 
        channel_scale(inst2,1,2)
        if i == 0: 
            channel_scale(inst2,2,0.1)
        else:
            channel_scale(inst2,2,3)
        run_rigol(inst2)
        set_output_freq(inst3,freq_list[i])
        time.sleep(0.2)
        trigger_mode(inst2,'SINGle') #Set trigger mode 
        (time_ch2, data_ch2) = get_data(inst2,2)
        Vpp = np.max(data_ch2[1:-1])-np.min(data_ch2[1:-1])
        V_list.append(Vpp)
    
    output_disable(inst3)
    Servo_on(inst1)
    return V_list 


