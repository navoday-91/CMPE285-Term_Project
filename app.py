import json, random
import datetime
import requests
import math
from flask import Flask, request, render_template

app = Flask(__name__)


@app.route("/")
def input():
    return render_template('index.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/contact")
def contact():
    return render_template('contact.html')


@app.route("/suggestion")
def suggestion():
    return render_template('suggestion.html')


@app.route("/test_suggestion")
def test_suggestion():
    return render_template('investment_suggestions.html')


@app.route("/map_stocks", methods=['POST'])
def mapStock():
    amount = request.form.get('amount')
    strategy = request.form.get('strategy')
    name = request.form.get('name')
    email = request.form.get('email')
    amount = float(amount)

    stockAmounts = []
    percentages = [80]
    while sum(percentages) > 70:
        percentages = []
        for _ in range(2):
            percentages.append(random.randint(20, 75))
    stockAmounts.append(round(amount*(percentages[0]/100)))
    stockAmounts.append(round(amount*(percentages[1]/100)))
    stockAmounts.append(amount - (stockAmounts[0] + stockAmounts[1]))

    stocks = getMapStocks(strategy)
    stock1Symbol = stocks[0]
    stock2Symbol = stocks[1]
    stock3Symbol = stocks[2]

    print('stock1Symbol = ' + stock1Symbol);
    print('stock2Symbol = ' + stock2Symbol);
    print('stock3Symbol = ' + stock3Symbol);

    amounts = [0,0,0]
    amounts[0]= stockAmounts[0]
    amounts[1]= stockAmounts[1]
    amounts[2]= stockAmounts[2]

    stock1Amount = float(stockAmounts[0])
    stock2Amount = float(stockAmounts[1])
    stock3Amount = float(stockAmounts[2])

    print('stock1Amount = ' + str(stock1Amount));
    print('stock2Amount = ' + str(stock2Amount));
    print('stock3Amount = ' + str(stock3Amount));

    # get buy number of each stock
    stock1 = {'symbol': stock1Symbol, 'amount': stock1Amount, 'buyNumber': 0}
    stock2 = {'symbol': stock2Symbol, 'amount': stock2Amount, 'buyNumber': 0}
    stock3 = {'symbol': stock3Symbol, 'amount': stock3Amount, 'buyNumber': 0}
    getBuyNumber(stock1, stock2, stock3)

    print('buyNumber1 = ' + str(stock1['buyNumber']));
    print('buyNumber2 = ' + str(stock2['buyNumber']));
    print('buyNumber3 = ' + str(stock3['buyNumber']));

    # get historic data
    history = getHistoricData(stock1Symbol, stock2Symbol, stock3Symbol)

    print(history)

    stock1['history'] = history[stock1Symbol]['chart']
    stock2['history'] = history[stock2Symbol]['chart']
    stock3['history'] = history[stock3Symbol]['chart']

    print('======= history of three stocks =========')
    print(stock1['history'])
    print(stock2['history'])
    print(stock3['history'])

    setHistoryTodayValue(stock1, stock2, stock3)
    print('======= TOTAL VALUE of three stocks =========')
    js_return_stock1 = []
    js_return_stock2 = []
    js_return_stock3 = []
    js_stock_total = []
    js_return_stock1_30d = []
    js_return_stock2_30d = []
    js_return_stock3_30d = []
    js_stock_total_30d = []
    for i in range(5, 0, -1):
        js_return_stock1.append(stock1['history'][-i]['total'])
        js_return_stock2.append(stock2['history'][-i]['total'])
        js_return_stock3.append(stock3['history'][-i]['total'])
        js_stock_total.append(stock1['history'][-i]['total']+ stock2['history'][i]['total'] + stock3['history'][i]['total'])

    len1 = len(stock1['history'])
    len2 = len(stock2['history'])
    len3 = len(stock3['history'])
    max_len = max([len1, len2, len3])
    for i in range(max_len):
        if len1 > i:
            js_return_stock1_30d.append(stock1['history'][i]['total'])
        else:
            js_return_stock1_30d.append(js_return_stock1_30d[-1])
        if len2 > i:
            js_return_stock2_30d.append(stock2['history'][i]['total'])
        else:
            js_return_stock2_30d.append(js_return_stock2_30d[-1])
        if len3 > i:
            js_return_stock3_30d.append(stock3['history'][i]['total'])
        else:
            js_return_stock3_30d.append((js_return_stock3_30d[-1]))
        js_stock_total_30d.append(js_return_stock3_30d[i] + js_return_stock1_30d[i] + js_return_stock2_30d[i])



    # output
    totalValueNow = stock1Amount + stock2Amount + stock3Amount

    print('totalValueNow = ' + str(totalValueNow))

    date1 = stock1['history'][0]['date']
    date2 = stock1['history'][1]['date']
    date3 = stock1['history'][2]['date']
    date4 = stock1['history'][3]['date']
    date5 = stock1['history'][4]['date']

    print('date1 = ' + date1)
    print('date2 = ' + date2)
    print('date3 = ' + date3)
    print('date4 = ' + date4)
    print('date5 = ' + date5)

    date1Total = stock1['history'][0]['total'] + stock2['history'][0]['total'] + stock3['history'][0]['total']
    date2Total = stock1['history'][1]['total'] + stock2['history'][1]['total'] + stock3['history'][1]['total']
    date3Total = stock1['history'][2]['total'] + stock2['history'][2]['total'] + stock3['history'][2]['total']
    date4Total = stock1['history'][3]['total'] + stock2['history'][3]['total'] + stock3['history'][3]['total']
    date5Total = stock1['history'][4]['total'] + stock2['history'][4]['total'] + stock3['history'][4]['total']
    print('date1Total = ' + str(date1Total))
    print('date2Total = ' + str(date2Total))
    print('date3Total = ' + str(date3Total))
    print('date4Total = ' + str(date4Total))
    print('date5Total = ' + str(date5Total))
    print(js_return_stock1_30d)
    print(js_return_stock2_30d)
    print(js_return_stock3_30d)
    print(js_stock_total_30d)
    return render_template('investment_suggestions.html',
                           totalValueNow=totalValueNow,
                           stock1Symbol=stock1Symbol,
                           stock2Symbol=stock2Symbol,
                           stock3Symbol=stock3Symbol,
                           stock1Amount=stock1Amount,
                           stock2Amount=stock2Amount,
                           stock3Amount=stock3Amount,
                           date1=date1,
                           date2=date2,
                           date3=date3,
                           date4=date4,
                           date5=date5,
                           date1Total=round(date1Total, 4),
                           date2Total=round(date2Total, 4),
                           date3Total=round(date3Total, 4),
                           date4Total=round(date4Total, 4),
                           date5Total=round(date5Total, 4),
                           buynumber1=round(stock1['buyNumber']),
                           buynumber2=round(stock2['buyNumber']),
                           buynumber3=round(stock3['buyNumber']),
                           stock1cost=stock1['history'][-1]['close'],
                           stock2cost=stock2['history'][-1]['close'],
                           stock3cost=stock3['history'][-1]['close'],
                           stock1history=js_return_stock1,
                           stock2history=js_return_stock2,
                           stock3history=js_return_stock3,
                           stockTotalHistory=js_stock_total,
                           stock1history30d=js_return_stock1_30d,
                           stock2history30d=js_return_stock2_30d,
                           stock3history30d=js_return_stock3_30d,
                           stockTotalHistory30d=js_stock_total_30d,
                           maxlen=max_len
                           )


############################ FUNCTIONS ############################
def getMapStocks(strategy, substrategy = None):
    result = {"Ethical Investing": {
                        "alt_energy": ["NYLD", "PEGI", "AY","NEE","FSLR","SEDG","REGI","GPRE","TOT"],
                        "zero_waste": ["WM", "RSG", "CVA"], "water": ["DHR", "XYL", "PNR"],
                        "reduce": ["BIP","USCR"], "reuse": ["IP"],
                        "sustain": ["WY"]},
            "index": ["VOO", "SCHA", "VYM", "FSTMX", "VTSMX", "VEU", "SCHZ", "BLV", "GAMR", "VSS"],
            "growth": ["SBUX", "NXPI", "FB","SFIX","JNJ","BRK.B","BRK.A","CNC","AAPL","SFM","DWDP"],
            "quality": ["GOOG","AMZN","AWK","AAPL","DIS","FB","NKE","MSFT","BAC","ADP"],
            "value": ["AAL","ALL","AZO","DHI","KHC","MPC","NFX","PHM","UAL","URI"]}

    if strategy == "Ethical Investing":
        #return result[strategy][substrategy]
        result = result[strategy]["alt_energy"]
    else:
        result = result[strategy]
    l = len(result)
    index_list = []
    while len(index_list) < 3:
        num = random.randint(0, l-1)
        if num not in index_list:
            print(num)
            index_list.append(num)

    return [result[i] for i in index_list]

def getHistoricData(symbol1, symbol2, symbol3):
    url = 'https://api.iextrading.com/1.0/stock/market/batch?symbols=' + symbol1 + ',' + symbol2 + ',' + symbol3 + '&types=chart&range=1m&last=5&filter=date,close'
    json_str = requests.get(url)
    print(json_str.content)
    data = json.loads(json_str.content);
    return data;


def getBuyNumber(obj1, obj2, obj3):
    url1 = 'https://api.iextrading.com/1.0/stock/' + obj1['symbol'] + '/price'
    response1 = requests.get(url1)
    obj1['price'] = float(response1.content)
    obj1['buyNumber'] = obj1['amount'] / obj1['price']

    url2 = 'https://api.iextrading.com/1.0/stock/' + obj2['symbol'] + '/price'
    obj2['price'] = float(requests.get(url2).content)
    obj2['buyNumber'] = obj2['amount'] / obj2['price']

    url3 = 'https://api.iextrading.com/1.0/stock/' + obj3['symbol'] + '/price'
    obj3['price'] = float(requests.get(url3).content)
    obj3['buyNumber'] = obj3['amount'] / obj3['price']


def setHistoryTodayValue(obj1, obj2, obj3):
    for i in range(len(obj1['history'])):
        obj1['history'][i]['total'] = obj1['buyNumber'] * obj1['history'][i]['close']
    for i in range(len(obj2['history'])):
        obj2['history'][i]['total'] = obj2['buyNumber'] * obj2['history'][i]['close']
    for i in range(len(obj3['history'])):
        obj3['history'][i]['total'] = obj3['buyNumber'] * obj3['history'][i]['close']


if __name__ == '__main__':
    app.run(debug=True)