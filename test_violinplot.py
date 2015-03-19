import random
import numpy as np
import matplotlib.pyplot as plt
plt.ion()
fs=10
pos=[1,2,4,5,7,8]
data =[np.random.normal(size=100) for i in pos]
ax=plt.subplot(111)
result = ax.violinplot(data,pos, points=20, widths=0.5, showmeans=True, showextrema=True, showmedians=True)
plt.show()
