import tensorflow as tf
import numpy as np

# def MinMaxScaler(data):
#     scale=  [ 1.,        200.,         200.,       200.,       200.,
#     100.,   10000.  ,10000.    ]
#     print('scale: ',scale)
#     # noise term prevents the zero division
#     return data / scale

def MinMaxScaler(data):
    numerator = data - np.min(data, 0)
    denominator = np.max(data, 0) - np.min(data, 0)

    # noise term prevents the zero division
    return numerator / (denominator + 1e-7), denominator,np.min(data,0)


# def MinMaxScaler(data):
#     numerator = data - np.min(data, 0)
#     denominator = np.max(data, 0) - np.min(data, 0)
#     # noise term prevents the zero division
#     return numerator / (denominator + 1e-7)
# 
# original minMax scaler
# re back => return * denominator + min = data

with tf.device('/cpu:0'):

    xy = np.loadtxt('dataSET1.csv', delimiter=',', dtype=np.float32)
    xy, denominator, Min = MinMaxScaler(xy)
    print('denominator')
    print(denominator)
    print("min value")
    print(Min)

    x_data = xy[0:4500, 1:-2]
    y_data = xy[0:4500, -2:]

    
    # Make sure the shape and data are OK
    # print(x_data.shape, x_data, len(x_data))
    # print(y_data.shape, y_data)

    # placeholders for a tensor that will be always fed.
    X = tf.placeholder(tf.float32, shape=[None, 5]) #3:input개수 
    Y = tf.placeholder(tf.float32, shape=[None, 2]) #1:output개수

    W = tf.Variable(
[[ 0.13244879 ,-0.35996214],
 [-0.17254227 ,-0.06763747],
 [ 0.55679744 , 0.25918636],
 [-0.24862184 ,-0.09673724],
 [ 0.03230236 , 0.01645175]], name='weight')
    b = tf.Variable([0.3112805, 0.3964208],name='bias')

    # # Hypothesis

    hypothesis = tf.matmul(X, W) + b

    # # Simplified cost/loss function

    cost = tf.reduce_mean(tf.square(hypothesis - Y))

    # # Minimize
    optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.00)
    train = optimizer.minimize(cost)

    prediction = tf.arg_max(hypothesis, 1)
    is_correct = tf.equal(prediction, tf.arg_max(Y, 1))
    accuracy = tf.reduce_mean(tf.cast(is_correct, tf.float32))

    # Launch the graph in a session.
    sess = tf.Session()
    # Initializes global variables in the graph.
    sess.run(tf.global_variables_initializer())
    step=0
    for i in range(2000):
        step=step+1
        cost_val,W_val,B_val,_= sess.run([cost,W,b,train], feed_dict={X: x_data, Y: y_data})
        if step % 2000 == 0:
            step=0            
            print("Cost: ", cost_val)
            print("Weight:")
            print(W_val)
            print("Bias:",B_val)
    print("Prediction:", sess.run(prediction, feed_dict={X: x_data}))
    # Calculate the accuracy
    print("Accuracy: ", sess.run(accuracy, feed_dict={X: x_data, Y: y_data}))

            
