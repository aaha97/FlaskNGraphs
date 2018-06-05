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
    if flask.session.get('active') and flask.session['active']==1:
        return flask.redirect(flask.url_for('menu'))
    flask.session['active']=0
    flask.session.modified = True
    return flask.render_template('index.html')
@app.route("/menu",methods=['GET','POST'])
def menu():
    print flask.session['filename']
    if flask.session.get('chosen_names'):
        flask.session.pop('chosen_names')
        flask.session.pop('chosen_paths')
        flask.session.modified = True
    return flask.render_template("menu.html",filenames=flask.session['filename'])
@app.route("/upload", methods = ['POST'])
def upload():
    if 'file' not in flask.request.files:
        flash('No file part')
        return flask.redirect(request.url)
    filenames=[]
    files = flask.request.files.getlist('file')
    
    for file in files:
        if file.filename == '' and (not allowed_file(file.filename)):
            flash('No selected file')
            return flask.redirect(request.url)    
        else:
            filename = werkzeug.utils.secure_filename(file.filename)
            filenames.append(filename)
    flask.session['filepath'] = []
    flask.session['filename'] = []
    flask.session.modified = True
    try:
        for file in files:
            filename = werkzeug.utils.secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path)
            flask.session['filepath'].append(path)
            flask.session['filename'].append(filename)
            flask.session.modified = True
    except OSError as err:
        return flask.redirect(request.url)
    flask.session['active']=1
    flask.session.modified = True
    return flask.redirect(flask.url_for("menu"))

@app.route("/deletefile",methods = ['GET'])
def deletefile():
    path = flask.session['filepath']
    os.remove(path)
    flask.session.pop('filepath')
    return flask.redirect(flask.url_for('main'))

@app.route("/process", methods = ['POST'])
def process():
    if flask.request.form['menu_choice'] == 'delete':
        print flask.session['filename']
        for name in flask.session['filename']:
            if flask.request.form.get(name):
                path = flask.session['filepath'][flask.session['filename'].index(name)]
                os.remove(path)
                flask.session['filepath'].remove(path)
                flask.session['filename'].remove(name)
                flask.session.modified = True
        print flask.session['filename']
        return flask.redirect(flask.url_for('menu'))
    elif flask.request.form['menu_choice'] == 'histogram':
        flask.session['chosen_names'] = []
        flask.session['chosen_paths'] = []
        for name in flask.session['filename']:
            if flask.request.form.get(name):
                path = flask.session['filepath'][flask.session['filename'].index(name)]
                flask.session['chosen_paths'].append(path)
                flask.session['chosen_names'].append(name)
                flask.session.modified = True
        return flask.redirect(flask.url_for('histogram'))
@app.route("/histogram",methods = ['GET','POST'])
def histogram():
    path = flask.session['chosen_paths']
    name = flask.session['chosen_names']
    figdict={}
    df=''
    i1 = flask.session['filepath'][0]
    for path in flask.session['filepath']:
        DF = pd.read_csv(path)
        if path==i1:
            df = DF
        else:
            df = pd.concat([df,DF])
    #iso8601.parse_date('2012-11-01T04:16:13-04:00')
    df['call_start'] = df['call_start'].apply(lambda x: iso8601.parse_date(x))
    df['call_start'] = pd.to_datetime(df['call_start'],utc=True)
    g = df['call_start'].groupby([df["call_start"].dt.year, df["call_start"].dt.month, df["call_start"].dt.day]).count()
    if flask.request.form.get('lineplot'):
        g.plot(kind='line')
        figfile2 = BytesIO()
        plt.savefig(figfile2, format='png')
        figfile2.seek(0)  # rewind to beginning of file
        figdata_png = figfile2.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        figdict['line'] = figdata_png
        plt.clf()
    if flask.request.form.get('barplot'):
        g.plot(kind='bar')
        figfile3 = BytesIO()
        plt.savefig(figfile3, format='png')
        figfile3.seek(0)  # rewind to beginning of file
        figdata_png = figfile3.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        figdict['bar'] = figdata_png
        plt.clf()
    if flask.request.form.get('barhplot'):
        g.plot(kind='barh')
        figfile4 = BytesIO()
        plt.savefig(figfile4, format='png')
        figfile4.seek(0)  # rewind to beginning of file
        figdata_png = figfile4.getvalue()
        figdata_png = base64.b64encode(figdata_png)
        figdict['barh'] = figdata_png
        plt.clf()
    return flask.render_template('uploading.html',imgs=figdict)
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
    app.run(debug=True)
