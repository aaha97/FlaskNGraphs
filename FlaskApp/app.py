import flask,os,werkzeug,iso8601,base64
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

UPLOAD_FOLDER = 'CSVS'
ALLOWED_EXTENSIONS = set(['csv'])

app = flask.Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main():
    return flask.render_template('index.html')

@app.route("/upload", methods = ['GET', 'POST'])
def upload():
    if flask.request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in flask.request.files:
            flash('No file part')
            return redirect(request.url)

        file = flask.request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return flask.redirect(request.url)

        if file and allowed_file(file.filename):
            filename = werkzeug.utils.secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print path
            file.save(path)
            flask.session['filepath'] = path
            flask.session['filename'] = filename
            return flask.render_template("uploading.html",name=filename,status="Success")

    return flask.render_template("uploading.html",name=filename,status="Failure")

@app.route("/deletefile",methods = ['GET'])
def deletefile():
    path = flask.session['filepath']
    os.remove(path)
    flask.session.pop('filepath')
    return flask.redirect(flask.url_for('main'))

@app.route("/process", methods = ['GET', 'POST'])
def process():
    path = flask.session['filepath']
    name = flask.session['filename']
    plottype = flask.request.form['plottype']
    figdict={}
    df = pd.read_csv(path)
    print df.head()
    iso8601.parse_date('2012-11-01T04:16:13-04:00')
    df[' START TIME'] = df[' START TIME'].apply(lambda x: iso8601.parse_date(x))
    df[' START TIME'] = pd.to_datetime(df[' START TIME'],utc=True)
    g = df[' START TIME'].groupby([df[" START TIME"].dt.year, df[" START TIME"].dt.month, df[" START TIME"].dt.day]).count()
    g.plot(kind=plottype)
    imgpath = 'static/plot/'+name+plottype+'.png'
    figfile1 = BytesIO()
    plt.savefig(figfile1, format='png')
    figfile1.seek(0)  # rewind to beginning of file
    figdata_png = figfile1.getvalue()
    figdata_png = base64.b64encode(figdata_png)
    figdict['selectmenu'] = figdata_png
    plt.clf()
    if flask.request.form.get('lineplot'):
        g = df[' START TIME'].groupby([df[" START TIME"].dt.year, df[" START TIME"].dt.month, df[" START TIME"].dt.day]).count()
        g.plot(kind='line')
        figfile2 = BytesIO()
        plt.savefig(figfile2, format='png')
        figfile2.seek(0)  # rewind to beginning of file
        figdata_png = figfile2.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        figdict['line'] = figdata_png
        plt.clf()
    if flask.request.form.get('barplot'):
        g = df[' START TIME'].groupby([df[" START TIME"].dt.year, df[" START TIME"].dt.month, df[" START TIME"].dt.day]).count()
        g.plot(kind='bar')
        figfile3 = BytesIO()
        plt.savefig(figfile3, format='png')
        figfile3.seek(0)  # rewind to beginning of file
        figdata_png = figfile3.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        figdict['bar'] = figdata_png
        plt.clf()
    if flask.request.form.get('barhplot'):
        g = df[' START TIME'].groupby([df[" START TIME"].dt.year, df[" START TIME"].dt.month, df[" START TIME"].dt.day]).count()
        g.plot(kind='barh')
        figfile4 = BytesIO()
        plt.savefig(figfile4, format='png')
        figfile4.seek(0)  # rewind to beginning of file
        figdata_png = figfile4.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        figdict['barh'] = figdata_png
        plt.clf()
    return flask.render_template('plot.html',imgpath=imgpath,imgs=figdict)
    #plt.savefig(imgpath)
    #plt.clf()
    #g.plot(kind="bar")
    #plt.savefig('static/plot/'+name+'bar.png')
    #plt.clf()
    #g.plot(kind="barh")
    #plt.savefig('static/plot/'+name+'barh.png')
    #plt.clf()
    #return ['static/plot/'+name+'line.png','static/plot/'+name+'bar.png','static/plot/'+name+'barh.png']
    #canvas = FigureCanvas(fig)
    #output = StringIO.StringIO()
    #canvas.print_png(output)
    '''response = make_response(output.getvalue())
    response.mimetype = 'image/png'
    return response'''
    #print file.stream
if __name__ == "__main__":
    app.run()
