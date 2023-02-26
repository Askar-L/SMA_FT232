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
    plt.clf() 

    if data_size[1] >3 : # Muti-Dim(a,b,...,t)
        plt.subplot(2,1,1)
        for _i in range(3): i = _i+1; plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
        plt.legend()

        plt.subplot(2,1,2)
        for _i in range(3): i = _i+4; plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
        plt.legend()
    else:
        # One dim (x,t)
        plt.plot(data_np[:,-1],data_np[:,0])
        # for _i in range(data_size[1]): plt.plot(data_np[:,-1],data_np[:,_i],label = labels[_i])

    f_type = "pdf"
    if f_type not in file_name: file_url= FIG_FOLDER+ file_name  +'.' + f_type
    else : file_url= FIG_FOLDER+ file_name  
    if os.path.exists(file_url): file_url= FIG_FOLDER+ file_name+"2"+'.' + f_type

    print("Figure saving as: ",FIG_FOLDER+file_name)
    # plt.margins(0,0)
    plt.savefig(file_url, dpi=1000,bbox_inches = 'tight',pad_inches=0.1)

    if show_img: plt.show()
    
    return file_url

