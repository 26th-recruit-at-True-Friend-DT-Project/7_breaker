import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import fredpy as fp
from datetime import datetime, timedelta
import pandas as pd
import FinanceDataReader as fdr


# Firebase database 인증 및 앱 초기화
cred = credentials.Certificate('./mykey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://breaker-a66d4-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

ref = db.reference()  # db 위치 지정

fp.api_key = '7075573c867961525db950833780fc8a'
enddate = (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%d')
spy = fdr.DataReader('SPY', '2017-10-01', enddate)  # S&P500 '93.1.29 - 오늘 1일단위(주말 제외)
corecpi = fp.series('CPILFESL',enddate)             # CPI
cpiyoy = corecpi.apc().data
unemploy = fp.series('UNRATE',enddate)              # 실업률 '48.1.1 - '22.12.1 1개월단위 #결측치 0
realgdp = fp.series('gdpc1',enddate)                # 미국 실질 GDP '47.1.1 - '22.7.1 3개월단위 #결측치 0
manufac = fp.series('PCUOMFGOMFG',enddate)          # 미노동부 제조업 생산자물가지수(PPI) '84.12.1 - '22.12.1 1개월단위 #결측치 12, ffill로 결측치 처리
nonfarm = fp.series('PAYEMS',enddate)               # 비농업고용지수 '39.1.1 - '22.12.1 1개월단위 #결측치 0
hpi = fp.series('USSTHPI',enddate)                  # 미국주택가격지수 '75.1.1 - '22. 7.1 3개월단위 #결측치 0
tb = fp.series('BOPGSTB', enddate)                  # 미국무역수지 '92.1.1 - '22.11.1 1개월단위 #결측치 0
dollar = fp.series('RTWEXBGS', enddate)             # 달러인덱스 '06.1.1 - '22.12.1 1개월단위 #결측치 0
retail = fp.series('MRTSSM44X72USS', enddate)       # 소매판매지수 '92.1.1 - '22.11.1 1개월단위 #결측치 0
wti = fp.series('WTISPLC', enddate)                 # WTI '46.1.1 - '22.12.1 1개월단위 #결측치 0


#결측치 처리
manufac_2 = manufac.data.fillna(method='ffill')

X = pd.concat([cpiyoy, unemploy.data, manufac_2, nonfarm.data, tb.data, dollar.data, retail.data, wti.data], axis = 1)
X_0 = pd.concat([spy, X], axis=1, join='inner')
X_1 = X_0.loc['2017-10-01':enddate]
X_2 = X_1.fillna(method='ffill')
X_3 = X_2.fillna(method='bfill')
X_3.columns = ['sp_open', 'sp_high', 'sp_low', 'sp_close', 'sp_adj', 'sp_volume', 'cpi', 'unem', 'manufac', 'nonfarm', 'tb', 'dollar', 'retail', 'wti']

X_3.reset_index(inplace=True)
df_date = []
for d in X_3['index']:
    df_date.append(pd.to_datetime(d).value)
del X_3['index']
X_3.insert(0, 'date', df_date)

df_spy = spy
df_spy = df_spy.fillna(method='ffill')
df_spy.reset_index(inplace=True)
spy_date = []
for d in df_spy['Date']:
    spy_date.append(pd.to_datetime(d).value)
del df_spy['Date']
df_spy.insert(0, 'date', spy_date)

data1 = df_spy.to_dict(orient='index')
data2 = X_3.to_dict(orient='index')

ref = db.reference('S&P500')
for i in range(len(data1)):
    ref.update({i: data1[i]})
#
# ref = db.reference('Indicator')
# for i in range(len(data2)):
#     ref.update({i: data2[i]})


