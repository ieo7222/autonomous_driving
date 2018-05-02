from scipy import stats, polyval
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf

f = open("dataSET_arr_nor_s5.csv", "r")
num = 0
L_x_up=[]
L_x_down=[]
R_x_up=[]
R_x_down=[]
speed=[]
count=0
while True:
    line = f.readline()
    if not line: break
    if (count%2)==0:
        
        items = line.split(",")
        L_x_up.append([float(items[1]), float(items[6])])
        L_x_down.append([float(items[2]), float(items[6])])
        R_x_up.append([float(items[3]), float(items[6])])
        R_x_down.append([float(items[4]), float(items[6])])
        speed.append([float(items[5]), float(items[6])])
    
    count=count+1
f.close()

x_data = [v[0] for v in L_x_up]
y_data = [v[1] for v in L_x_up]
x1_data = [v[0] for v in L_x_down]
y1_data = [v[1] for v in L_x_down]
x2_data = [v[0] for v in R_x_up]
y2_data = [v[1] for v in R_x_up]
x3_data = [v[0] for v in R_x_down]
y3_data = [v[1] for v in R_x_down]
x_spd_data = [v[0] for v in speed]
y_spd_data = [v[1] for v in speed]



# plt.plot(x_data, y_data, '.')
plt.plot(x1_data, y1_data, 'r.')
# plt.plot(x2_data, y2_data, 'g.')
# plt.plot(x3_data, y3_data, 'y.')
# plt.plot(x_spd_data, y_spd_data, 'k.')
plt.legend()
plt.show()

# W = tf.Variable(tf.random_uniform([1], -1.0, 0.0))
# b = tf.Variable(tf.zeros([1]))
# y = W * x_data + b

# loss = tf.reduce_mean(tf.square(y - y_data))
# optimizer = tf.train.GradientDescentOptimizer(0.05)
# train = optimizer.minimize(loss)

# init = tf.initialize_all_variables()

# sess = tf.Session()
# sess.run(init)

# for step in xrange(8):
#      sess.run(train)
#      print(step, sess.run(W), sess.run(b))
#      print(step, sess.run(loss))

#      #Graphic display
#      plt.plot(x_data, y_data, '.')
#      plt.plot(x_data, sess.run(W) * x_data + sess.run(b))

#      plt.show()