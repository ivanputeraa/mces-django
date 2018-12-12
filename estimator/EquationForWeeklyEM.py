import numpy as np
from numpy.linalg import lstsq
# 2x + 3y = 5
# x   + 3y = 3 
# a=np.mat([[2,3,0],[1,3,1]])
# b=np.mat([5,3]).T
# x=lstsq(a,b,rcond=None)
# print(x)
XiShuJuZhen = [[65,40691,4575,839]]
ReSult = [(1-0.999946)* (65+40691+4575+839)]

a=np.mat(XiShuJuZhen)
b=np.mat(ReSult).T
x=lstsq(a,b,rcond=None)

print(x[0])
print(1-x[0][0])
print(1-x[0][1])
print(1-x[0][2])
print(1-x[0][3])