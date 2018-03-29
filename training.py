import tensorflow as tf
import numpy as np
with tf.device('/cpu:0'):
    xy = np.loadtxt('dataSET1.csv', delimiter=',', dtype=np.float32)
    x_data = xy[0:4500, 1:-2]
    y_data = xy[0:4500, -2:]

    # Make sure the shape and data are OK
    # print(x_data.shape, x_data, len(x_data))
    # print(y_data.shape, y_data)

    # placeholders for a tensor that will be always fed.
    X = tf.placeholder(tf.float32, shape=[None, 5]) #3:input개수 
    Y = tf.placeholder(tf.float32, shape=[None, 2]) #1:output개수

    W = tf.Variable(
[[  15.295133,  -107.41519  ],
 [  -7.117806,   -11.16824  ],
 [  54.396526,   108.938995 ],
 [   2.9447942,   -1.3366497],
 [   5.2830844,   10.336983 ]], name='weight')
    b = tf.Variable( [5902.659 ,8192.   ], name='bias')

    # # Hypothesis

    hypothesis = tf.matmul(X, W) + b

    # # Simplified cost/loss function

    cost = tf.reduce_mean(tf.square(hypothesis - Y))

    # # Minimize
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.000003)
    train = optimizer.minimize(cost)

    # Launch the graph in a session.
    sess = tf.Session()
    # Initializes global variables in the graph.
    sess.run(tf.global_variables_initializer())
    step=0
    while(True):
        step=step+1
        cost_val,W_val,B_val,_= sess.run([cost,W,b,train], feed_dict={X: x_data, Y: y_data})
        if cost_val<50:
            break
        if step % 2000 == 0:
            step=0            
            print("Cost: ", cost_val)
            print("Weight:")
            print(W_val)
            print("Bias:",B_val)
