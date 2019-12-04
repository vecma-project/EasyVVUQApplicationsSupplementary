import pandas as pd
import sys
import numpy as np
print 'start'  

data_columns = ['Step', 'Lx', 'Ly', 'Lz', 
                'v_xstress', 'v_ystress', 'v_zstress',
                'Temp', 'KinEng', 'PotEng', 'Press']

#assumes data blocks start with Step, end with Loop, and the only interuptions are Shake read-outs
# assumes there are 9 data blocks, sample relaxed conformation, straining, and sample strained conformation
relaxed   = {'X': [], 'Y': [], 'Z': []}
straining = {'X': [], 'Y': [], 'Z': []}
strained  = {'X': [], 'Y': [], 'Z': []}

block = 0
with open('log.lammps','r') as f:
  while True:
    line = f.readline().split()
    if len(line) == 0: continue
    if line[0] == 'Step':
      block += 1
      print block
      rawdata = []
      while True:
        line = f.readline().split()
        if line[0] == 'Loop': break
        if len(line) == 11: rawdata += [line]
  
      if block == 1:   relaxed['X'] = rawdata
      elif block == 2: straining['X'] = rawdata
      elif block == 3: strained['X'] = rawdata
      elif block == 4: relaxed['Y'] = rawdata
      elif block == 5: straining['Y'] = rawdata
      elif block == 6: strained['Y'] = rawdata
      elif block == 7: relaxed['Z'] = rawdata
      elif block == 8: straining['Z'] = rawdata
      elif block == 9: strained['Z'] = rawdata

    if line[0:3] == ['Total','wall','time:']: break

for i in ['X','Y','Z']:
  relaxed[i] = pd.DataFrame(relaxed[i],columns=data_columns,dtype=float)
  straining[i] = pd.DataFrame(straining[i],columns=data_columns,dtype=float)
  strained[i] = pd.DataFrame(strained[i],columns=data_columns,dtype=float)

alldata = pd.concat([
                     relaxed['X'],straining['X'],strained['X'],
                     relaxed['Y'],straining['Y'],strained['Y'],
                     relaxed['Z'],straining['Z'],strained['Z']])

relax_mean  = [ relaxed['X']['v_xstress'].mean(), 
                relaxed['Y']['v_ystress'].mean(),
                relaxed['Z']['v_zstress'].mean()]

strain_mean = [strained['X']['v_xstress'].mean(),
               strained['Y']['v_ystress'].mean(),
               strained['Z']['v_zstress'].mean()]

ym = np.array(strain_mean) - np.array(relax_mean)
ym = ym / 0.005

result = pd.DataFrame(columns=['X', 'Y', 'Z'])
result['X'] = [ym[0]]
result['Y'] = [ym[1]]
result['Z'] = [ym[2]]

result.to_csv('out.dat')

