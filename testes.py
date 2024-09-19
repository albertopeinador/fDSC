import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import txtmod as tx


file_path1 = r'C:\Users\albpe\OneDrive - Universidade da Coruña\Escritorio\fDSC\90816 (Bulk 80kDa)\Annealing30min2kto260\Segment108_120deg.txt'
file_path2 = r'C:\Users\albpe\OneDrive - Universidade da Coruña\Escritorio\fDSC\90816 (Bulk 80kDa)\Annealing30min2kto260\Segment168_240deg.txt'

ax1=plt.gca()
ax2=plt.gca()

tx.modify_text_file(file_path1)
tx.modify_text_file(file_path2)

data1 = pd.read_csv(file_path1.replace('.txt', '_modified.txt'), sep= '\t', encoding = 'latin1')
data2 = pd.read_csv(file_path2.replace('.txt', '_modified.txt'), sep= '\t', encoding = 'latin1')

margin = data1['Heat Flow'].max() * .1

while any(data2['Heat Flow'] - data1['Heat Flow'] - margin < 0) == True:
    print('spacing curve...')
    data2 += margin

data1.plot(x = 'Ts', y = 'Heat Flow', ax=ax1)
data2.plot(x = 'Ts', y = 'Heat Flow', ax=ax2)
plt.show()