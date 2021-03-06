import tensorflow as tf
import numpy as np

def MinMaxScaler(data):

    scale=  [ 4949.,        200.,         200.,       200.,       200.,
    100.,   10000.  ,10000.    ]
    print('scale: ',scale)
    # noise term prevents the zero division
    return data / scale

with tf.device('/cpu:0'):

    xy = np.loadtxt('TESTdata.csv', delimiter=',', dtype=np.float32)
    xy = MinMaxScaler(xy)
    print(xy)
    x_data = xy[:3, 1:-2]
    y_data = xy[:3, -2:]

    
    # Make sure the shape and data are OK
    # print(x_data.shape, x_data, len(x_data))
    # print(y_data.shape, y_data)

    # placeholders for a tensor that will be always fed.
    X = tf.placeholder(tf.float32, shape=[None, 5]) #3:input개수 
    Y = tf.placeholder(tf.float32, shape=[None, 2]) #1:output개수

    W = tf.Variable(tf.random_normal([5,2]), name='weight')
    b = tf.Variable(tf.random_normal([2]),name='bias')

    # # Hypothesis

    hypothesis = tf.matmul(X, W) + b

    # # Simplified cost/loss function

    cost = tf.reduce_mean(tf.square(hypothesis - Y))

    # # Minimize
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1e-2)
    train = optimizer.minimize(cost)

    # Launch the graph in a session.
    sess = tf.Session()
    # Initializes global variables in the graph.
    sess.run(tf.global_variables_initializer())
    step=0
    while(True):
        step=step+1
        cost_val,W_val,B_val,H_val,_= sess.run([cost,W,b,hypothesis,train], feed_dict={X: x_data, Y: y_data})
        if step % 2000 == 0:
            step=0            
            print("Cost: ", cost_val)
            # print("Weight:")
            # print(W_val)
            # print("Bias:",B_val)
            print("htpothesis:")
            print(H_val)
            print("ans : ")
            print(y_data)
            # ss_predict=(116/200)*W_val[0][0]+(-65)/200*W_val[1][0]+139/200*W_val[2][0]+218/200*W_val[3][0]+64.71577/100*W_val[4][0]+B_val[0]
            # ac_predict=(116/200)*W_val[0][1]+(-65)/200*W_val[1][1]+139/200*W_val[2][1]+218/200*W_val[3][1]+64.71577/100*W_val[4][1]+B_val[1]
            # print('s: ',ss_predict*10000,' answer: 16958.17908224')
            # print('ac: ',ac_predict*10000,' answer: 627.2343736319999')
# 116,-65,139,218,,16958.17908224,627.2343736319999

