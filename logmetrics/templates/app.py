#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import datetime
import os
import json
from flask import Flask, session, redirect, url_for, escape, request, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from forms import *
from werkzeug.utils import secure_filename
from flask import send_from_directory
from logcluster import log_cluster
from logreduce import log_reduce
from metrictimeseries import metrictimeseries
from datetime import datetime
from search import Search

datastore = []
processing_done = 0
raw_data=[]
es = None

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


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
es = Search()
app.config('es') = es

# Automatically tear down SQLAlchemy.
#@app.teardown_request
#def shutdown_session(exception=None):
#    db_session.remove()

# Login required decorator.
'''
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap
'''
#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route('/')
def index():
    return redirect(url_for('login'))

#----------------------------------------------------------------------------#
# Stream sense stuff
#----------------------------------------------------------------------------#

@app.route('/home', methods=['GET', 'POST'])
def home():
    return render_template('pages/placeholder.home.html', dataLoaded=app.config['LAST_FILENAME'])

@app.route('/_input.json')
def render_input():
    jsondata = []
    for line in app.config['DATA']:
        jsondata.append(json.loads(line))
    return jsonify(data=jsondata)


@app.route('/_input_serverside.json')
def render_input_serverside():
    print "entering input"
    startlines = int(request.values['start'])
    numlines = int(request.values['length'])
    alllines = len(app.config['DATA'])
    jsondata = []
    for line in app.config['DATA'][startlines:startlines+numlines]:
        jsondata.append(json.loads(line))
    return jsonify(data=jsondata,recordsTotal = alllines, recordsFiltered = alllines, draw=int(request.values['draw']))


def create_metrics_output():
    #return the file
    numhashbits = app.config['NUMHASHBITS']
    return metrictimeseries(app.config['DATA'], numhashbits)


def create_cluster_output():
    #return the file
    stopwords = "etc/stopwords.txt"
    numhashbits = app.config['NUMHASHBITS']
    # TODO - speed it up in memory
    return log_cluster(app.config['DATA'], stopwords, numhashbits)


@app.route('/_logcluster.output.json')
def render_cluster_output():
    raw_data = create_cluster_output()
    jsondata = []
    for line in raw_data:
        jsondata.append(json.loads(line))
    return jsonify(data=jsondata)


@app.route('/_logcluster_serverside.output.json')
def render_cluster_serverside_output():
    global processing_done
    global raw_data
    print "entering output.json:"+ str(datetime.datetime.now().time())
    if (processing_done == 0):
       raw_data = create_cluster_output()
       raw_data.sort(key=lambda x: float(json.loads(x)["sortfield"]))
       processing_done = 1
    print "finished output.json:"+ str(datetime.datetime.now().time())
    startlines = int(request.values['start'])
    numlines = int(request.values['length'])
    alllines = len(raw_data)
    print "raw_data[0]="+str(raw_data[0])
    print "raw_data[1]="+str(raw_data[1])
    print "raw_data[2]="+str(raw_data[2])
    print "raw_data[3]="+str(raw_data[3])
    print "raw_data[4]="+str(raw_data[4])
    jsondata = []
    for line in raw_data[startlines:startlines+numlines]:
        jsondata.append(json.loads(line))
    return jsonify(data=jsondata,recordsTotal = alllines, recordsFiltered = alllines, draw=int(request.values['draw']))


def create_reduce_output():
    #return the file
    stopwords = "etc/stopwords.txt"
    numhashbits = app.config['NUMHASHBITS']
    # TODO - speed it up in memory
    return log_reduce(app.config['DATA'], stopwords, numhashbits)


@app.route('/_logreduce.output.json')
def render_reduce_output():
    raw_data = create_reduce_output()
    jsondata = []
    for line in raw_data:
        jsondata.append(json.loads(line))
    return jsonify(data=jsondata)


@app.route('/_logreduce_serverside.output.json')
def render_reduce_serverside_output():
    global processing_done
    global raw_data
    print "entering output.json:"+ str(datetime.datetime.now().time())
    if (processing_done == 0):
        raw_data = create_reduce_output()
        processing_done = 1
    print "finished output.json:"+ str(datetime.datetime.now().time())
    startlines = int(request.values['start'])
    numlines = int(request.values['length'])
    alllines = len(raw_data)
    jsondata = []
    for line in raw_data[startlines:startlines+numlines]:
        jsondata.append(json.loads(line))
    return jsonify(data=jsondata,recordsTotal = alllines, recordsFiltered = alllines, draw=int(request.values['draw']))



@app.route('/_slider', methods = ['POST'])
def slider_change():
    value = int(request.form['value'])
    app.config['NUMHASHBITS'] = value
    return jsonify(result={"status": 200})


@app.route('/anomaly', methods = ['GET'])
def anomaly_detection():
    print "entering slider"
    c={}
    d={}
    e={}
    timeseries = create_metrics_output()
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


@app.route('/metricsanomaly', methods=['GET', 'POST'])
def metrics_anomaly():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            inputfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(inputfilename)
            datastore = read_lines_from_file(inputfilename)
            app.config['DATA'] = datastore
            app.config['LAST_FILENAME'] = inputfilename
    return render_template('pages/metrics_anomaly.html', dataLoaded=app.config['LAST_FILENAME'])



@app.route('/logcluster', methods=['GET', 'POST'])
def logcluster():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            inputfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(inputfilename)
            datastore = read_lines_from_file(inputfilename)
            app.config['DATA'] = datastore
            app.config['LAST_FILENAME'] = inputfilename
    return render_template('pages/logcluster.html', dataLoaded=app.config['LAST_FILENAME'])


@app.route('/logreduce', methods=['GET', 'POST'])
def logreduce():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            inputfilename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print "in logreduce and about to save file", inputfilename
            file.save(inputfilename)
            datastore = read_lines_from_file(inputfilename)
            #insert into elastic search
            for line in datastore:
                Search.insert(jsonify(line))
            app.config['DATA'] = datastore
            app.config['LAST_FILENAME'] = inputfilename
    return render_template('pages/logreduce.html', dataLoaded=app.config['LAST_FILENAME'])


#----------------------------------------------------------------------------#

@app.route('/about')
def about():
    return render_template('pages/placeholder.about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    form = LoginForm()
    if request.method == 'POST':
        if form.name.data == 'admin' and form.password.data == 'admin':
            return redirect(url_for('home'))
        else:
            error = "Wrong username/password, try again!"
            return render_template('forms/login.html', form=form, error=error)
    return render_template('forms/login.html', form=form, error=error)


@app.route('/register')
def register():
    form = RegisterForm(request.form)
    return render_template('forms/register.html', form=form)


@app.route('/forgot')
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form=form)

# Error handlers.


@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
