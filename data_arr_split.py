
import numpy as np
import csv

def mean_value(LIST):
    sum=np.array([0,0,0,0,0,0,0,0])
    
    for i in range(len(LIST)):
        temp=sum+LIST[i]
        sum=temp
    return sum/len(LIST)

f = open("dataSET1.csv", "r")
mean_data=[]
count=0
while True:
    line = f.readline()
    if not line: break
    items = line.split(",")
    if (count%2)==0 and count>2000 and count <8000:
        items = np.array(items,np.float64)
        mean_data.append(items)

        if len(mean_data)==5:
            fields=mean_value(mean_data)
            # print(fields)
            with open('dataSET_arr_s5_split.csv', 'a') as f2:
                writer = csv.writer(f2)
                writer.writerow(fields)
            mean_data=[]       
    count=count+1
    if count%1000==0:
        print(count/1000)

print('finshed')