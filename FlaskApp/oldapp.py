import os
import iso8601
import datetime
import random
import StringIO
from flask import Flask, request, redirect, url_for, render_template, make_response
import pandas as pd
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
UPLOAD_FOLDER = 'CSVS'
ALLOWED_EXTENSIONS = set(['csv'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route("/process", methods = ['GET', 'POST'])
def process():
    path = request.form['path']
    name = request.form['name']

    df = pd.read_csv(path)
    print df.head()
    iso8601.parse_date('2012-11-01T04:16:13-04:00')
    df[' START TIME'] = df[' START TIME'].apply(lambda x: iso8601.parse_date(x))
    df[' START TIME'] = pd.to_datetime(df[' START TIME'],utc=True)
    g = df[' START TIME'].groupby([df[" START TIME"].dt.year, df[" START TIME"].dt.month, df[" START TIME"].dt.day]).count()
    g.plot(kind="line")
    plt.savefig('static/plot/'+name+'line.png')
    plt.clf()
    g.plot(kind="bar")
    plt.savefig('static/plot/'+name+'bar.png')
    plt.clf()
    g.plot(kind="barh")
    plt.savefig('static/plot/'+name+'barh.png')
    plt.clf()
    #return ['static/plot/'+name+'line.png','static/plot/'+name+'bar.png','static/plot/'+name+'barh.png']
    #canvas = FigureCanvas(fig)
    #output = StringIO.StringIO()
    #canvas.print_png(output)
    '''response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response'''
    #print file.stream
@app.route("/upload", methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print path
            file.save(path)
            #process(path,file.filename.rsplit('.', 1)[0].lower())
            #res = process(path)
            #return res
            return redirect(url_for('process'))
    return redirect(url_for('main'))

@app.route("/")
def main():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
