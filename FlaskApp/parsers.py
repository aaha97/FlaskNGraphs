import pandas as pd
import numpy as np
i=0
flag=0
while i>=0:
    try:
        df = pd.read_csv('samples/sample5.csv',skiprows=i)
        if len(df.columns)<4:
            i=i+1
            flag=1
        for name in df.columns:
            if name==np.nan or name=='' or 'Unnamed: 1' == name:
                i=i+1
                flag=1
                break
        if flag==0:
            break
        flag=0
    except:
        i=i+1
        continue

#for sameple2
def parse_sample2(df):
    cname = df.iloc[9].tolist()
    cname[0] = 'From'
    cname[1] = 'To'
    cname[-1]="todel"
    df.columns = cname
    df = df.drop(df.index[0:11])
    df = df.dropna()
    df = df.reset_index()
    df = df.drop(['index','todel'],axis=1)
    df['DateTime'] = df.apply(lambda row: (datetime.combine(parse(row[2]).date(),parse(row[3]).time())).isoformat(),axis=1)
    return df
#for sameple3
def parse_sample3(df):
    cname = df.iloc[5].tolist()
    cname[0] = 'From'
    cname[1] = 'To'
    df = df.drop(df.index[0:11])
    df = df.dropna()
    df = df.reset_index()
    df = df.drop(['index'],axis=1)
    t1 = date(1899,12,31)
    df.columns = cname
    df['xFrom'] = df.apply(lambda row: row[1] if (row['CALL TYPE(IN /OUT/SMS IN/SMS OUT)'] in ['MTC','SMMT','MT3','SMMT3','VDOMTC']) else row[0],axis=1)
    df['xTo'] = df.apply(lambda row: row[0] if (row['CALL TYPE(IN /OUT/SMS IN/SMS OUT)'] in ['MTC','SMMT','MT3','SMMT3','VDOMTC']) else row[1],axis=1)
    df[['From','To']] = df[['xFrom','xTo']]
    df = df.drop(['xFrom','xTo'],axis=1)
    df['DateTime'] = df.apply(lambda row: (datetime.combine(t1+timedelta(int(float(row[2]))),parse(row[3]).time())).isoformat(),axis=1)
    return df