# Created by Askar @202230201
# Modified in 2

"""
General functions for all system
"""
import numpy as np
import os,time,sys
from matplotlib import pyplot as plt
from typing import Any, Iterable, Mapping, Optional, Tuple, Union

RUNTIME = time.time()
FIG_FOLDER = "./IMG/"
DATA_FOLDER = "./IMG/"
FIG_SIZE = (12.8,8.00)#(19.2,10.8)
FONTSIZE = 18

class Logger(object):
    def __init__(self, filename=[]):
        if filename is not None:
            filename =  FIG_FOLDER+time.strftime("_%b%d_%H.%M.%S",time.localtime(RUNTIME))+'.txt'

        self.terminal = sys.stdout
        self.log = open(filename, "a")
 
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
        pass
    
    def _eg_codes():
        path = os.path.abspath(os.path.dirname(__file__))
        type = sys.getfilesystemencoding()
        sys.stdout = Logger()

def saveData(data,file_name,labels,f_type:str="csv",**kwargs: Mapping[str, Any]):
 
    # file_name = time.strftime("_%b%d_%H.%M",runtime)+str(dutys)+str(intervals)
    
    if f_type not in file_name: file_url= FIG_FOLDER+ file_name  +'.' + f_type
    else : file_url= FIG_FOLDER+ file_name  
    if os.path.exists(file_url): file_url= FIG_FOLDER+ file_name+"2"+'.' + f_type
    header = str(labels).replace("'",'').replace("]",'').replace("[",'')
    if "csv" in f_type:
        np.savetxt(file_url,data, fmt='%.18e', delimiter=',', 
            newline='\n', header=header, footer='', comments='# ', encoding=None)

    return file_url

def saveFigure(data,file_name,labels,show_img=False,**kwargs: Mapping[str, Any]):
    data_np = np.array(data)
    data_size = data_np.shape
    print("Saving figure for sampled data:",data_size)
        
    figsize=FIG_SIZE
    if not data_size[1] >3 : 
        figsize = (FIG_SIZE[1]*2.35,FIG_SIZE[1])
 
    plt.rcParams.update({'font.size': FONTSIZE}) # 改变所有字体大小，改变其他性质类似

    plt.figure(figsize=figsize)
    plt.clf()
    # plt.xticks(fontsize=FONTSIZE)
    # plt.yticks(fontsize=FONTSIZE)

    # # 设置坐标标签字体大小
    # ax.set_xlabel( fontsize=FONTSIZE)
    # ax.set_ylabel( fontsize=FONTSIZE)
    # ax.legend(fontsize=FONTSIZE)


    if data_size[1] > 3 : # Muti-Dim(a,b,...,t)
        ax = plt.subplot(211)
        # plt.xticks(fontsize=FONTSIZE); plt.yticks(fontsize=FONTSIZE)
        # ax.legend(fontsize=FONTSIZE)
        
        for _i in range(3): i = _i+1; plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
        plt.legend(loc='upper center', ncol=3,frameon=False,shadow=False,framealpha=0)
        
        ax = plt.subplot(212)
        # plt.xticks(fontsize=FONTSIZE); plt.yticks(fontsize=FONTSIZE)
        for _i in range(3): i = _i+4; plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
        # ax.legend(fontsize=FONTSIZE)
        plt.legend(loc='upper center', ncol=3,frameon=False,shadow=False,framealpha=0)


    else:
        # One dim (x,t)
        ax = plt.subplot(111)
        plt.plot(data_np[:,-1],data_np[:,0],label =labels[0])
        plt.legend()


    f_type = "pdf"
    if f_type not in file_name: file_url= FIG_FOLDER+ file_name  +'.' + f_type
    else : file_url= FIG_FOLDER+ file_name  
    if os.path.exists(file_url): file_url= FIG_FOLDER+ file_name+"2"+'.' + f_type

    print("Figure saving as: ",FIG_FOLDER+file_name)
    # plt.margins(0,0)
    plt.savefig(file_url, dpi=1000,bbox_inches = 'tight',pad_inches=0.1)
    if show_img: plt.show()
    
    return file_url

