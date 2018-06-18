import flask,os,werkzeug,iso8601,base64
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np
import graph_tool.all as gt
from datetime import datetime,date,timedelta
from dateutil.parser import parse

UPLOAD_FOLDER = 'CSVS'
ALLOWED_EXTENSIONS = set(['csv'])

app = flask.Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_frame(df):
    col = df.columns.tolist()
    for c in col:
        if "Unnamed" in c:
            df = df.drop([c],axis=1)
    for c in col:
        s = c.lower()
        if ("calling" in s) or ("a party" in s):
            df['from'] = df[c]
            continue
        if ("called" in s) or ("b party" in s):
            df['to'] = df[c]
            continue
        if ("date" in s):
            df['date'] = df[c]
            continue
        if ("time" in s):
            df['time'] = df[c]
            continue
    rows = len(df.index)
    col = df.columns.tolist()
    for c in col:
        if df[c].isnull().sum() > rows/2:
            df = df.drop(c,axis=1)
    df = df.dropna()
    df = df.reset_index()
    t1 = date(1899,12,31)
    row = df.iloc[1]
    try:
        x = parse(row['time'])
    except Exception as e:
        try:
            df['time'] = df.apply(lambda r:str(timedelta(seconds=r['time']*86400)),axis=1)
        except Exception as ee:
            print "sad ",ee
    try:
        '''if len(row['date'])<=7:
            df['datetime'] = df.apply(lambda row: (datetime.combine(t1+timedelta(int(float(row['date']))),parse(row['time']).time())).isoformat(),axis=1)
        else:
            df['datetime'] = df.apply(lambda row: (datetime.combine(parse(row['date']).date(),parse(row['time']).time())).isoformat(),axis=1)'''
        df['datetime'] = df.apply(lambda row: (datetime.combine(t1+timedelta(int(float(row['date']))),parse(row['time']).time())).isoformat() if len(row['date'])<=7 else (datetime.combine(parse(row['date']).date(),parse(row['time']).time())).isoformat(),axis=1)
    except Exception as e:
        print "Exception: ",e
    keeper = ['from','to','datetime']
    col = df.columns.tolist()
    for c in col:
        if c in keeper:
            continue
        else:
            df = df.drop(c,axis=1)  
    return df

def parse_file(file):
    i=0
    flag=0
    while i>=0:
        try:
            df = pd.read_csv(file,skiprows=i)
            if len(df.columns)<4:
                i=i+1
                flag=1
            for name in df.columns:
                if name==np.nan or name=='' or 'Unnamed: 1' == name or len(name)==2:
                    i=i+1
                    flag=1
                    break
            if flag==0:
                break
            flag=0
        except Exception as e:
            if 'No columns to parse from file' in e:
                raise Exception('inconsistent rows in file')
            i=i+1
            continue
    df = parse_frame(df)
    print df.head()
    df.to_csv(file,index=False)

@app.route("/", methods = ['POST','GET'])
def main():
    if flask.session.get('active') and flask.session['active']==1:
        return flask.redirect(flask.url_for('menu'))
    flask.session['active']=0
    flask.session.modified = True
    return flask.render_template('index.html')
@app.route("/menu",methods=['GET','POST'])
def menu():
    if flask.session.get('chosen_names'):
        flask.session.pop('chosen_names')
        flask.session.pop('chosen_paths')
        flask.session.modified = True
    return flask.render_template("menu.html",filenames=flask.session['filename'])
@app.route("/upload", methods = ['POST','GET'])
def upload():
    if 'file' not in flask.request.files:
        flask.flash('No file part')
        return flask.redirect(flask.url_for("main"))
    filenames=[]
    files = flask.request.files.getlist('file')
    
    for file in files:
        if file.filename == '' and (not allowed_file(file.filename)):
            flash('No selected file')
            return flask.redirect(flask.request.url)    
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
            parse_file(path)
    except Exception as e:
        print "Exception: ",e
        return flask.redirect(flask.request.url)
    flask.session['active']=1
    flask.session.modified = True
    return flask.redirect(flask.url_for("menu"))

@app.route("/deletefile",methods = ['POST','GET'])
def deletefile():
    path = flask.session['filepath']
    os.remove(path)
    flask.session.pop('filepath')
    return flask.redirect(flask.url_for('main'))

@app.route("/process", methods = ['POST','GET'])
def process():
    if flask.request.form['menu_choice'] == 'delete':
        for name in flask.session['filename']:
            if flask.request.form.get(name):
                path = flask.session['filepath'][flask.session['filename'].index(name)]
                os.remove(path)
                flask.session['filepath'].remove(path)
                flask.session['filename'].remove(name)
                flask.session.modified = True
        if len(flask.session['filename'])>0:
            return flask.redirect(flask.url_for('menu'))
        else:
            flask.session['active']=0
            return flask.redirect(flask.url_for('main'))
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
    elif flask.request.form['menu_choice'] == 'network':
        flask.session['chosen_names'] = []
        flask.session['chosen_paths'] = []
        for name in flask.session['filename']:
            if flask.request.form.get(name):
                path = flask.session['filepath'][flask.session['filename'].index(name)]
                flask.session['chosen_paths'].append(path)
                flask.session['chosen_names'].append(name)
                flask.session.modified = True
        return flask.redirect(flask.url_for('network'))
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
    df['datetime'] = df['datetime'].apply(lambda x: iso8601.parse_date(x))
    df['datetime'] = pd.to_datetime(df['datetime'])
    print 'min',df['datetime'].min(axis=1)
    print 'max',df['datetime'].max(axis=1)
    g = df['datetime'].groupby([df["datetime"].dt.year, df["datetime"].dt.month, df["datetime"].dt.day]).count()
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
@app.route("/network",methods = ['GET','POST'])
def network():
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
    df = df.drop(['datetime'],axis=1)

    #actors = df['from'].tolist()+df['to'].tolist()
    #actors = list(set(actors))
    #actor_id = { str(actors[i]): i for i in xrange(len(actors)) }

    #df['from_id'] = df.apply(lambda x: actor_id[str(x['from'])],axis=1)
    #df['to_id'] = df.apply(lambda x: actor_id[str(x['to'])],axis=1)
    #df['label_prop'] = df.apply(lambda x: str(x['from_id'])+"->"+str(x['to_id']),axis=1)
    g = gt.Graph(directed=True)
    #g.add_vertex(n=len(actors))
    #g.add_edge_list(df[['from_id','to_id']].values)
    g.add_edge_list(df.values,hashed=True)
    #labels = g.new_ep(value_type="string",vals=df['label_prop'].tolist())
    pos = gt.arf_layout(g, max_iter=100,dt=1e-4)
    figfile = BytesIO()
    #figdata_png = gt.graphviz_draw(g,edge_text=labels,return_string=True)
    #gt.graph_draw(g,pos=pos,edge_text=labels, output=figfile,fmt='png')
    #print figdata_png[1]
    gt.graph_draw(g,pos=pos,output_size=(1000,1000), output=figfile,fmt='png')
    figfile.seek(0)
    figdata_png = figfile.getvalue()
    figdata_png = base64.b64encode(figdata_png)
    figdict['plot'] = figdata_png
    plt.clf()
    df.to_csv("test_file.csv",index=False)
    return flask.render_template('networkplot.html',imgs=figdict)
if __name__ == "__main__":
    app.run(host='0.0.0.0',debug=True)
