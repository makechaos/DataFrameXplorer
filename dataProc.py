import numpy as np
from pandas import DataFrame as df
import sys, re, os

dd = []
def loadData(fil):
  global dd, datafile
  dd = df.from_csv(fil)
  
def log(msg,mode='a'):
  fd = open('log.txt',mode)
  fd.write(msg+'\n')
  fd.close()

def tagifyList(cols):
  btags = set()
  for col in cols:
    tt = re.split(',|-|_| ', os.path.splitext(col)[0])
    for t in tt:
      if len(t)<=2: # omit short ones len<=2
        continue
      btags.add(t)
  
  tags = {}
  for tag in btags:
    tags[tag] = [0,[]]
  ncol = -1
  for col in cols:
    ncol += 1
    for tag in tags:
      if col.find(tag)>=0:
        tags[tag][0] += 1
        tags[tag][1] += [ncol]
  
  hh = []
  for tag in tags:
    if tags[tag][0]<=2: # omit ones occuring few times <=2
      continue
    hh += [[tag, tags[tag]]]
  hh.sort(key=lambda(x):x[1],reverse=True)
  return hh
  
def getCols():
  opt = {}
  opt['tags'] = tagifyList(dd.columns)
  opt['data'] = list(dd.columns)
  return opt
  
def getPlotData(config):
  log(str(config));
  try:
    ref = np.zeros(dd.shape[0]);
    if len(config['ref'])>0:
      ref = np.array(dd[config['ref']])
    
    xaxis = range(dd.shape[0])
    if len(config['xcol'])>0:
      xaxis = np.array(dd[config['xcol']])

    FFTon = False
    if 'ffton' in config:
      FFTon = True
    
    data = []
    for col in config['data']:
      if len(col.strip())==0:
        continue
      
      pl = { 'name':col, 'type': "line", 'legendText':col, 'showInLegend': True, 'lineThickness': 1, 'dataPoints': []}
      
      cdata = np.array(dd[col]) - ref
      if FFTon:
        cdata = np.abs(np.fft.fft(cdata))
      
      for m in range(dd.shape[0]):
        pl['dataPoints'] += [{'x':xaxis[m], 'y':cdata[m]}]
      data += [pl]
    log('success '+str(len(data)))
    return data
  except:
    log('failed')
    log(sys.exc_info()[0])
    return sys.exc_info()[0]
