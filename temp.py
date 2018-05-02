import numpy as np
def mean_value(LIST):
    sum=np.array([0,0,0,0,0])
    
    for i in range(len(LIST)):
        temp=sum+LIST[i]
        sum=temp
    print(sum)
    return temp/len(LIST)

# a='12\n'

# print(int(a))
# print(1)

a=[1.,2.,3.,4.,5.]
na=np.array(a)
print(na.dtype)

# b=[10,20,30,40,50]
# nb=np.array(b)

# c=[100,200,300,400,500]
# nc=np.array(c)

# temp=[]
# temp.append(na)
# temp.append(nb)
# temp.append(nc)

# result=mean_value(temp)
# print(result)

# temp=np.array([0,0,0,0,0])
# sum=np.array([])

# result=sum+bb
# print(result)



# a=[1,2,3,4,5]
# na=np.array(a)
# # b=[10,20,30,40,50]
# # nb=np.array(b)


# k=[]
# k.append(na)
# k.append(nb)
# # print(k[0]+k[1])
# # print(len(k))

# print(sum(k))