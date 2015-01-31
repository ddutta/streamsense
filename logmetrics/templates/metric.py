#
# @StackInsight 2014
# Debo~ Dutta, Abhi~ Das
#

#uses memory based optimization

import json
import os
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
from metrictimeseries import metrictimeseries
import datetime

# define env vars 
# TODO read env vars from config or external overrides
UPLOAD_FOLDER = 'uploads'
TEMPLATE_FOLDER = 'templates'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

# store the last file uploaded as a giant in memory list 
datastore = []
processing_done = 0
raw_data=[]
# initiate a flask app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEMPLATE_FOLDER'] = TEMPLATE_FOLDER
app.config['LAST_FILENAME'] = ""
app.config['NUMHASHBITS'] = 14 #default

def read_lines_from_file(filename):
    lines = []
    for line in open(filename):
        lines.append(line.rstrip('\n'))
    return lines


def write_lines_to_file(lines, filename):
    f = open(fname, "w")
    for line in lines:
        f.writelines(line)


# check whether filename is valid
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# The main root doc
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            app.config['LAST_FILENAME'] = filename
            # save the file in uploads directory
            inputfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(inputfilename)
            datastore = read_lines_from_file(inputfilename)
            app.config['DATA'] = datastore #store the in-memory dump of the log
            # now render the page
            return send_from_directory(app.config['TEMPLATE_FOLDER'],
                               'metrics_mem.html')
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/input.json')
def render_input():
    print "entering input"
    startlines = int(request.values['start'])
    numlines = int(request.values['length'])
    alllines = len(app.config['DATA'])
    jsondata = []
    for line in app.config['DATA'][startlines:startlines+numlines]:
        jsondata.append(json.loads(line))
    return jsonify(data=jsondata,recordsTotal = alllines, recordsFiltered = alllines, draw=int(request.values['draw']))


def create_output():
    #return the file
    numhashbits = app.config['NUMHASHBITS']
    return metrictimeseries(app.config['DATA'], numhashbits)


@app.route('/anomaly', methods = ['GET'])
def anomaly_detection():
    print "entering slider"
    c={}
    d={}
    e={}
    timeseries = create_output()
    timeseriesjson={}
    for key in timeseries.keys():
       indivtimeseries={}
       indivtimeseries["label"]=id
       if "anomaly" in key:
          indivtimeseries["label"]="anomaly"
          indivtimeseries["color"]="#ff0000"
          indivtimeseries["lines"] = {"show":0}
          indivtimeseries["points"] = {'show':1, 'radius':5 ,'fill':'true', 'fillColor':'#ff0000'}
       else:
          indivtimeseries["label"]=1
          indivtimeseries["lines"] = {"show":1}
       indivtimeseries["data"] = timeseries[key]
       timeseriesjson[key]=indivtimeseries
    for key in timeseries.keys():
       if (key+":anomaly" in timeseries.keys()):
          timeseriesjson[key]["label"]=2

    print "printing json timeseries"
    #print timeseriesjson
    return jsonify(timeseriesjson)
    

if __name__ == '__main__':
	app.run()
