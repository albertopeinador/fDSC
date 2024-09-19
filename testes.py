import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import txtmod as tx


file_path1 = r'C:\Users\albpe\OneDrive - Universidade da Coruña\Escritorio\fDSC\90816 (Bulk 80kDa)\Annealing30min2kto260\Segment108_120deg.txt'
file_path2 = r'C:\Users\albpe\OneDrive - Universidade da Coruña\Escritorio\fDSC\90816 (Bulk 80kDa)\Annealing30min2kto260\Segment168_240deg.txt'

ax1=plt.gca()
ax2=plt.gca()
'''
df = pd.DataFrame({'T':np.linspace(1, 10, 10), 'c1':np.linspace(10, 80, 10), 'c2':np.logspace(1, 2, 10)})

#df.plot(x='T', y='c2', ax=ax1)
#df.plot(x='T', y='c1', ax=ax1)

while any(df['c1']-df['c2'] - extra < 0) == True:
    print('spacing curve...')
    df['c1'] += 3


df.plot(x='T', y='c1', ax=ax2)
'''
tx.modify_text_file(file_path1)
tx.modify_text_file(file_path2)

data1 = pd.read_csv(file_path1.replace('.txt', '_modified.txt'), sep= '\t', encoding = 'latin1')
data2 = pd.read_csv(file_path2.replace('.txt', '_modified.txt'), sep= '\t', encoding = 'latin1')

margin = data1['Heat Flow'].max() * .1

while any(data2['Heat Flow'] - data1['Heat Flow'] - margin < 0) == True:
    print('spacing curve...')
    data2 += data1['Heat Flow'].max()*.5

data1.plot(x = 'Ts', y = 'Heat Flow', ax=ax1)
data2.plot(x = 'Ts', y = 'Heat Flow', ax=ax2)
plt.show()