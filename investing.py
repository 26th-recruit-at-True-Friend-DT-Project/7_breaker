import pandas as pd
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import fredpy as fp
from datetime import datetime, timedelta
import FinanceDataReader as fdr

# Firebase database 인증 및 앱 초기화
cred = credentials.Certificate('./mykey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://breaker-a66d4-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

enddate = (datetime.now() + timedelta(days=-1)).strftime('%Y-%m-%d')
fp.api_key = '7075573c867961525db950833780fc8a'

# 미국 지표
us_corecpi = fp.series('CPILFESL', enddate)  # CPI
us_cpiyoy = us_corecpi.apc().data  # corecpi 전년동기대비 변화율 '57.1.1 - '22.12.1 1개월단위 #결측치 0
spy = fdr.DataReader('SPY', '2017-10-1', enddate)['Close'] * 10  # S&P500 '93.1.29 - 오늘 1일단위(주말 제외)
us_unemploy = fp.series('UNRATE', enddate)  # 실업률 '48.1.1 - '22.12.1 1개월단위 #결측치 0
us_tb = fp.series('BOPGSTB', enddate)  # 미국무역수지 '92.1.1 - '22.11.1 1개월단위 #결측치 0
dollar = fp.series('RTWEXBGS', enddate)  # 달러인덱스 '06.1.1 - '22.12.1 1개월단위 #결측치 0
us_retail = fp.series('MRTSSM44X72USS', enddate)  # 소매판매지수 '92.1.1 - '22.11.1 1개월단위 #결측치 0

# 중국 지표
ssec = pd.read_csv('./Shanghai.csv')
dt = []
for i in range(len(ssec['Date'])):
    Y = ssec['Date'][i][6:]
    M = ssec['Date'][i][0:2]
    D = ssec['Date'][i][3:5]
    my_date = Y + '-' + M + '-' + D
    dt.append(my_date)
ssec['date'] = dt

ssec = ssec.sort_index(axis=0, ascending=False)
ssec = ssec.set_index(keys='date')
ssec = ssec[['Price']]

temp = []
for i in range(len(ssec['Price'])):
    a = float(ssec['Price'][i][:1] + ssec['Price'][i][2:5] + ssec['Price'][i][5:])
    temp.append(a)
ssec['Price'] = temp

ch_cpi = fp.series('CPALTT01CNM659N', enddate)  # 중국 cpi 전간동기대비 변화율 '57.1.1 - '22.12.1 1개월단위 #결측치 0
ch_unem = fp.series('LMUNRRTTCNQ156S', enddate)  # 실업률 '03.1.1 - '11.7.1 3개월단위 #결측치 0
ch_tb = fp.series('BPBLTD01CNQ637S', enddate)  # 무역수지 '98.1.1 - '13.4.1 3개월단위
yuan = fp.series('DEXCHUS', enddate)  # 위안화지수 '81.1.1 - '23.1.20 1일 단위
ch_retail = fp.series('CHNSLRTTO02MLM', enddate)  # 소매판매지수 '93.1.1 - '22.7.1 1개월 단위

print(ch_cpi.data.index)
print(ch_unem.data.index)
print(ch_tb.data.index)
print(yuan.data.index)
print(ch_retail.data.index)

# 유럽 지표
stoxx = pd.read_csv('./Euro.csv')
stoxx = stoxx.set_index(keys='날짜')
stoxx = stoxx.sort_values('날짜')
stoxx = stoxx[['종가']]
temp = []
for i in range(len(stoxx['종가'])):
    a = float(stoxx['종가'][i][:1] + stoxx['종가'][i][2:5] + stoxx['종가'][i][5:])
    temp.append(a)
stoxx['종가'] = temp
eu_cpi = fp.series('CP0000EZ19M086NEST', enddate)
eu_cpiyoy = eu_cpi.apc().data  # cpi '96.1.1 - '22.12.1 1개월단위
eu_unem = fp.series('LRHUTTTTEZM156S', enddate)  # 실업률 '90.7.1 - '22.10.1 3개월단위
eu_tb = fp.series('BPBLTD01EZQ636S', enddate)  # 무역수지 '97.1.1 - '12.10.1 3개월단위
euro = fp.series('DEXUSEU', enddate)  # 유로화지수 '99.1.4 - '23.1.10 1일단위
eu_retail = fp.series('EA19SLRTTO02IXOBSAM', enddate)  # 소매판매지수 '95.1.1 - '22.10.1 1개월 단위

# cpi, unem, tb, dollar(yuan,euro), retail

# 데이터 가공 및 합치기
X = pd.concat([us_cpiyoy, us_unemploy.data, us_tb.data, dollar.data, us_retail.data], axis=1)
Y = pd.concat([ch_cpi.data, ch_unem.data, ch_tb.data, yuan.data, ch_retail.data], axis=1)
Z = pd.concat([eu_cpiyoy, eu_unem.data, eu_tb.data, euro.data, eu_retail.data], axis=1)

X_1 = pd.concat([spy, X], axis=1, join='outer')
X_1 = X_1.loc['2022-02-01':'2022-08-01']

Y_1 = pd.concat([ssec, Y], axis=1, join='outer')
Z_1 = pd.concat([stoxx, Z], axis=1, join='outer')

X_2 = X_1.fillna(method='ffill')
X_3 = X_2.fillna(method='bfill')

Y_2 = Y_1.fillna(method='ffill')
Y_3 = Y_2.fillna(method='bfill')

Z_2 = Z_1.fillna(method='ffill')
Z_3 = Z_2.fillna(method='bfill')

X_3.columns = ['spy', 'us_cpi', 'us_unemployment', 'us_trade_balance', 'dollar_index', 'us_retail']
Y_3.columns = ['ssec', 'ch_cpi', 'ch_unemployment', 'ch_trade_balance', 'yuan_index', 'ch_retail']
Z_3.columns = ['stoxx', 'eu_cpi', 'eu_unemployment', 'eu_trade_balance', 'euro_index', 'eu_retail']

print(X_3.corr())
print(Y_3.corr())

A1 = X_3.corr()[['spy']]
A1.reset_index(inplace=True)
del A1['index']
A1 = A1.to_dict(orient='index')
#
# A2 = Y_3.corr()[['ssec']]
# A2.reset_index(inplace=True)
# del A2['index']
# A2 = A2.to_dict(orient='index')
#
# A3 = Z_3.corr()[['stoxx']]
# A3.reset_index(inplace=True)
# del A3['index']
# A3 = A3.to_dict(orient='index')
#
ref = db.reference('spy')
for i in range(len(A1)):
    ref.update({i: A1[i]})
#
# ref = db.reference('ssec')
# for i in range(len(A2)):
#     ref.update({i: A2[i]})
#
# ref = db.reference('stoxx')
# for i in range(len(A3)):
#     ref.update({i: A3[i]})
