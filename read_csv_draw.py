import numpy as np
import time, csv,pandas as pd
from matplotlib import pyplot as plt

DUTYS =  [1,0.2]   # [预热 响应 维持]c
INTERVALS = [0.2,1]
FIG_FOLDER = "./IMG/"
TIME_OUT = 5
RUNTIME = time.localtime()
DO_PLOT = False
 
FIG_SIZE = (10,6) #(12.8,7.2)#(19.2,10.8)


def saveFigure(data,labels,show_img=False):
    data_np = np.array(data)
    plt.clf() 
    plt.figure(figsize=FIG_SIZE)

    plt.subplot(2,1,1)

    for _i in range(3): 
        i = _i+1
        plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
    plt.legend()

    plt.subplot(2,1,2)
    for _i in range(3): 
        i = _i+4
        plt.plot(data_np[:,-1],data_np[:,i],label = labels[i])
    plt.legend()
    
    file_name = time.strftime("_%b%d_%H.%M",RUNTIME)+str(DUTYS)+str(INTERVALS) 

    print("Figure saving as: ",FIG_FOLDER+file_name +'.pdf')
    # print("Figure saving as: ",FIG_FOLDER+file_name +'.pdf')
    # plt.margins(0,0)
    plt.savefig(FIG_FOLDER+file_name+'.pdf',dpi=1000,bbox_inches = 'tight',pad_inches=0.1)
    plt.savefig(FIG_FOLDER+file_name+'.png',dpi=10 0,bbox_inches = 'tight',pad_inches=0.1)
    if show_img: plt.show()

def read_file(url):
    LABELS = ['Temp','AR_X','AR_Y','AR_Z','LA_X','LA_Y','LA_Z','Time']
    # csv.

    data = []

    # with open(url) as _f:
    #     f_csv = csv.reader(_f)
    #     for row in f_csv:data.append(row)
    # print(np.array(data))

    df = pd.read_csv(url)
    d_np = df.to_numpy()
    df.head()
    # print(d_np)
    saveFigure(d_np,LABELS,show_img=False)

    pass

def saveData(data,labels):
    file_url=FIG_FOLDER+ time.strftime("_%b%d_%H.%M",RUNTIME)+str(DUTYS)+str(INTERVALS)  +'.csv'
    np.savetxt(file_url,data, fmt='%.18e', delimiter=',', 
        newline='\n', header=str(labels), footer='', comments='# ', encoding=None)
    pass

if __name__=='__main__': # Test codes # Main process
    
    # url = "C:\Users\Liu\Desktop\20210721SMAFinger\Code\SMA_FT232\IMG\ForJEMS"
    url = 'C:/Users/Liu/Desktop/20210721SMAFinger/Code/SMA_FT232/IMG/ForJEMS/' + '_Oct26_23.02[1, 0.2][0.2, 1].csv'
    read_file(url)

    pass