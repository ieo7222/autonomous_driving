import tensorflow as tf
import numpy as np

def MinMaxScaler(data):
    numerator = data - np.min(data, 0)
    denominator = np.max(data, 0) - np.min(data, 0)
    # noise term prevents the zero division
    return numerator / (denominator + 1e-7)

with tf.device('/cpu:0'):

    xy = np.loadtxt('dataSET1.csv', delimiter=',', dtype=np.float32)
    xy = MinMaxScaler(xy)
    x_data = xy[0:4500, 1:-2]
    y_data = xy[0:4500, -2:]

    
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
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.1e-5)
    train = optimizer.minimize(cost)

    # Launch the graph in a session.
    sess = tf.Session()
    # Initializes global variables in the graph.
    sess.run(tf.global_variables_initializer())
    step=0
    while(True):
        step=step+1
        cost_val,W_val,B_val,_= sess.run([cost,W,b,train], feed_dict={X: x_data, Y: y_data})
        if step % 2000 == 0:
            step=0            
            print("Cost: ", cost_val)
            print("Weight:")
            print(W_val)
            print("Bias:",B_val)
