from flask import Flask, request
import sys
import json
import dataProc
import datetime 
import os
import webbrowser, threading

'''
Origin: Vikram Melapudi, 14-Feb-2018
Change log:
  14/02/2018: Initial version
  15/02/2018:
    v1:
    - JSON to pass in plot data
    - storing selections
    v1p1:
    - way to maintain original column order after exchanging
    v1p2:
    - tag based filtering pf column for easier selection
    - saving a session (stores selection-sets, tags, columns, data file)
    - start from a pre-saved session
    - added closing of session to stop the server cleanly
  16/02/2018:
    v1p3
    - added ability to take port as cmd input
    - change column display based on selection-set used
  20/02/2018:
    v1p4
    - added port as cmd line input
    - automatically start webbrowser
    - intial page of help/hints
ToDo:
 - get cmd line options to enable disable features (e.g. FFT, X-scale, etc.)
'''

print('Usage:')
print('>>python '+sys.argv[0]+' <csv file> [options]')
print('Options:')
print('  -port:<no>')
print('--------------------\n')
dataProc.log(str(datetime.datetime.now()),'w')

port = 4555;
session = ''
datafile = '';
if len(sys.argv)>1:
  arg = sys.argv[1]
  if arg.find('.csv')>0:
    datafile = os.path.normpath(os.path.abspath(arg))
  elif arg.find('.sess')>0:
    session = json.load( open(arg,'r') )
    datafile = session['datafile'].replace('|','\\')
  dataProc.loadData(datafile)
for m in range(2,len(sys.argv)):
  if sys.argv[m].find('-port:')>=0:
    port = int( sys.argv[0].split(':')[1] )

app = Flask(__name__)

@app.route('/')
def index():
  fd = open('dataFrameExplorer.html','r')
  txt = fd.readlines()
  for n in range(len(txt)):
    if txt[n].find('{{datafile}}')>=0:
      txt[n] = txt[n].replace('{{datafile}}',datafile.replace('\\','|'))
    elif txt[n].find('{{port}}')>=0:
      txt[n] = txt[n].replace('{{port}}',str(port))
  txt = ''.join(txt)
  fd.close()
  return txt

@app.route('/script/<inp>')
def getScript(inp):
  fd = open(inp,'r')
  txt = ''.join(fd.readlines())
  fd.close()
  return txt
  
@app.route('/options')
def fileOptions():
  if type(session)==dict:
    return json.dumps(session)
  else:  
    return json.dumps(dataProc.getCols())
    
@app.route('/close')
def close():
  func = request.environ.get('werkzeug.server.shutdown')
  if func is None:
    raise RuntimeError('Not running with the Werkzeug Server')
  func()
  
@app.route('/plot/<inp>')
def plotData(inp):
  return json.dumps( dataProc.getPlotData(json.loads(inp)) )

@app.route('/savesession/<inp>')
def saveSession(inp):
  inp = json.loads(inp)
  fil = inp['name']+'-'+datetime.datetime.now().strftime('%Y_%m_%d_%H_%M')+'.sess'
  json.dump(inp, open(fil,'w'))
  txt = 'Session saved :'+os.path.abspath(fil)
  return json.dumps(txt)

if __name__ == '__main__':
  threading.Timer(2, lambda: webbrowser.open('http://localhost:'+str(port))).start()
  app.run(host='localhost',port=port) #,debug=True)
