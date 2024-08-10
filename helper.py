import pandas as pd
import unicodedata


#class Data():
dic_begin_country={"ita":"Italy","port":"Portugal","pays":"Netherlands","nether":"Netherlands","sp":"Spain","espa":"Spain","belg":"Belgium","fra":"France","lux":"Luxembourg","sw":"Sweden","ger":"Germany","all":"Germany","br":"Brazil","dan":"Danemark","ind":"India","bulg":"Bulgaria","au":"Austria","uk":"United Kingdom","usa":"United States","mea":"MEA","glo":"Global"}
def cleaning_pipeline(data):
    df=data.copy()
    df.dropna(axis=1,how='all',inplace=True)
    if (df.columns[0].rfind("Unnam")==0):
        df.columns=df.iloc[0]
        df=df.drop(0,axis=0)
        df.dropna(axis=1,how='all',inplace=True)
    df.reset_index(drop=True,inplace=True)
    df.to_csv('clean_data.csv')
    return df

prefix_mapping={"unnamed":"presents","nombre":"presents","nom":"contact","sujets discutes":"output","feedback":"feedback","relance":"relance","meeting":"date_prise_contact","prise":"date_prise_contact","next":"next","call":"call","stat":"status"}
def normalize_columns(df, prefix_mapping:dict):
    # Strip whitespace from column names
    df.columns = df.columns.str.strip()
    
    # Normalize accents and lowercase the column names
    #df.columns = df.columns.map(lambda col: unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8').lower())
    df.columns = [unicodedata.normalize('NFKD', col).encode('ascii', 'ignore').decode('utf-8').lower() if str(col)!='nan' else 'unnamed' for col in list(df.columns)]
    
    
    # Rename columns based on the mapping
    #df = df.rename(columns=column_mapping)
    
    # Handle columns that contains certain prefixes
    for col in df.columns:
        for prefix, new_name in prefix_mapping.items():
            if (col.rfind(prefix)>=0):
                df = df.rename(columns={col: new_name})
                break
                
    return df

def normalize_countries(df):
    for key in dic_begin_country.keys():
        df["Pays"][df["Pays"].str.lower().str.rfind(key)>=0]=dic_begin_country[key]
    return df
def normalize_status(df):
    if (type(df.status.iloc[0])==int):
        return df
    else:
        stat_list=[]
        for i in range(len(df.status)):
            stat=df.status.iloc[i]
            try:
                if (stat.lower().startswith("done")):
                    stat_list.append(1)
                else:
                    if (stat.lower().startswith("ongoing")):
                        stat_list.append(0)
            except Exception as e:
                # print(e)
                output=df.output.iloc[i]
                if str(output)=="nan":
                    stat_list.append(-1)
                else:
                    stat_list.append(0)
        df.status=stat_list
        return df

def excel_pipeline(excel):
    df_list=[]
    num_sheets=len(excel.sheet_names)
    for i in range(num_sheets):
        data=pd.read_excel(excel,i)
        data=cleaning_pipeline(data)
        data=normalize_countries(data)
        data= normalize_columns(data,prefix_mapping)
        data.to_csv('clean_data.csv')
        data=data[["pays","contact","role","output","next","date_prise_contact","status","presents"]]
        data=normalize_status(data)
        df_list.append(data)
    if num_sheets==1:
        data.to_csv('clean_data.csv')
        return data
    else:
        df=pd.concat(df_list)
        df.reset_index(inplace=True)
        df.to_csv('clean_data.csv')
        return df



def date_to_datetime(data,country='all'):
    if country=='all':
        data["date_prise_contact"]=pd.to_datetime(data["date_prise_contact"],dayfirst=True,format='mixed')
        history=data[["date_prise_contact","contact"]].groupby("date_prise_contact").count()
    else:   
        to_country=data[data['pays']==country]
        to_country["date_prise_contact"]=pd.to_datetime(to_country["date_prise_contact"],dayfirst=True,format='mixed')
        history=to_country[["date_prise_contact","contact"]].groupby("date_prise_contact").count()
    return history

iso=pd.read_csv("country_with_iso.csv",index_col='country')

def successful_calls(data,country="all"):
    if country=="all":
        unsuccessful=sum(data.presents.isna())
        return len(data)-unsuccessful
    else:
        to_country=data[data['pays']==country]
        unsuccessful=sum(to_country.presents.isna())
        return len(to_country)-unsuccessful

def sum_presents(data,country="all"):
    if country=="all":
        presents=list(data.presents)
        filtred=[i for i in presents if str(i)!="nan"]
    else:
        to_country=data[data['pays']==country]
        presents=list(to_country.presents)
        filtred=[i for i in presents if str(i)!="nan"]
    return sum(filtred)

def count_contacts_per_country(data):
    df=data[["pays","contact"]]
    df=df.groupby('pays').count().reset_index()
    L=[]
    for p in df.pays:
        try:
            L.append(iso['iso_alpha'].loc[p])
        except:
            L.append(None)
    df['iso_alpha']=L
    return df

# add model that gives if client is satisfied or not

from model import pretrained_sentiment
def satisfaction(df:pd.DataFrame)->pd.DataFrame:
    df=df[['contact','output']]
    df.dropna(inplace=True)
    comments=df.output
    contacts=list(df.contact)
    satisfaction_list=list(comments.apply(lambda x:pretrained_sentiment(x)[1]))
    satisfaction_list=['satisfied' if x=='POSITIVE' else 'unsatisfied' for x in satisfaction_list]
    return pd.DataFrame({'contact':contacts,'satisfaction':satisfaction_list,'details':comments})

# to filter satisfaction table

def filter_satisfaction(satisfaction_dt:pd.DataFrame,details,satisfied):
    if details:
        if satisfied in ['all',None]:
            return satisfaction_dt
        else:
            return satisfaction_dt[satisfaction_dt.satisfaction==satisfied]
    else:
        if satisfied=='all':
            return satisfaction_dt.drop('details',axis=1)
        else:
            dt=satisfaction_dt[satisfaction_dt.satisfaction==satisfied]
            return dt.drop('details',axis=1)
