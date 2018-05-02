
import numpy as np
import csv


def MinMaxScaler(data):
    numerator = data - np.min(data, 0)
    denominator = np.max(data, 0) - np.min(data, 0)

    # noise term prevents the zero division
    return numerator / (denominator + 1e-7), denominator,np.min(data,0)

xy = np.loadtxt('dataSET1.csv', delimiter=',', dtype=np.float32)
xy, denominator, Min = MinMaxScaler(xy)

print(xy[0])
for i in range(4500):    
    with open('dataSET_normal.csv', 'a') as f2:
        writer = csv.writer(f2)
        writer.writerow(xy[i])   

# x_data = xy[0:4500, 1:-2]
# y_data = xy[0:4500, -2:]

# while True:
#     line = f.readline()
#     if not line: break
#     items = line.split(",")
#     if (count%2)==0 and count>2000 and count <8000:
#         items = np.array(items,np.float32)
#         if len(mean_data)==10:
#             mean_data.pop(0)
#         mean_data.append(items)

#         fields=mean_value(mean_data)
#         # print(fields)
#         with open('dataSET_arr_s10.csv', 'a') as f2:
#             writer = csv.writer(f2)
#             writer.writerow(fields)       
#     count=count+1

# def mean_value(LIST):
#     sum=np.array([0,0,0,0,0,0,0,0])
    
#     for i in range(len(LIST)):
#         temp=sum+LIST[i]
#         sum=temp
#     return sum/len(LIST)

# f = open("dataSET1.csv", "r")
# mean_data=[]
# count=0
# while True:
#     line = f.readline()
#     if not line: break
#     items = line.split(",")
#     if (count%2)==0 and count>2000 and count <8000:
#         items = np.array(items,np.float32)
#         if len(mean_data)==10:
#             mean_data.pop(0)
#         mean_data.append(items)

#         fields=mean_value(mean_data)
#         # print(fields)
#         with open('dataSET_arr_s10.csv', 'a') as f2:
#             writer = csv.writer(f2)
#             writer.writerow(fields)       
#     count=count+1
#     if count%1000==0:
#         print(count/1000)

# print('finshed')