import json, random
import datetime
import requests
from flask import Flask, request, render_template, session
import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
    if 'username' in session:
        with open("history.json", 'r') as hist_file:
            history = json.loads(hist_file.read())
        if session['email'] in history:
            hist_data = history[session['email']]
            return render_template('suggestion.html', history=hist_data)
        else:
            return render_template('suggestion.html')
    else:
        return render_template('login.html')


@app.route("/login")
def login():
    return render_template('login.html')


@app.route("/signup")
def signup():
    return render_template('signup.html')


@app.route("/logout")
def logout():
    session.pop('username', None)
    return render_template('login.html')


@app.route("/register_user", methods=['POST'])
def register():
    email = request.form.get('username')
    password = request.form.get('pass')
    password1 = request.form.get('pass1')
    name = request.form.get('name')
    if password != password1:
        return render_template('signup.html', error_code=1)
    with open('data.json', 'r') as outfile:
        user_data = json.loads(outfile.read())
    if email in user_data:
        return render_template('signup.html', error_code=2)
    user_data[email] = [password, name]
    with open('data.json', 'w') as outfile:
        json.dump(user_data, outfile)
    return render_template('login.html', error_code=1)


@app.route("/validate_user", methods=['POST'])
def validate():
    email = request.form.get('username')
    password = request.form.get('pass')
    with open('data.json', 'r') as outfile:
        user_data = json.loads(outfile.read())
    if email not in user_data:
        return render_template('login.html', error_code=2)
    elif user_data[email][0] != password:
        return render_template('login.html', error_code=3)
    else:
        session['username'] = user_data[email][1]
        session['email'] = email
        return render_template('index.html', user_data=[user_data[email][1], email])


@app.route("/map_stocks", methods=['POST', 'GET'])
def mapStock():
    if 'username' not in session:
        return render_template('login.html')
    if request.method == 'POST':
        amount = request.form.get('amount')
        strategy = request.form.get('strategy')
        amount = float(amount)
    name = session['username']
    email = session['email']

    if request.method == 'POST':
        stockAmounts = []
        percentages = [80]
        while sum(percentages) > 70:
            percentages = []
            for _ in range(2):
                percentages.append(random.randint(20, 75))
        stockAmounts.append(round(amount * (percentages[0] / 100)))
        stockAmounts.append(round(amount * (percentages[1] / 100)))
        stockAmounts.append(amount - (stockAmounts[0] + stockAmounts[1]))

        stocks = getMapStocks(strategy)
    else:
        stockAmounts = [request.args.get('amount1'), request.args.get('amount2'), request.args.get('amount3')]
        stocks = [request.args.get('name1'), request.args.get('name2'), request.args.get('name3')]

    stock1Symbol = stocks[0]
    stock2Symbol = stocks[1]
    stock3Symbol = stocks[2]
    amounts = [0, 0, 0]
    amounts[0] = stockAmounts[0]
    amounts[1] = stockAmounts[1]
    amounts[2] = stockAmounts[2]

    stock1Amount = float(stockAmounts[0])
    stock2Amount = float(stockAmounts[1])
    stock3Amount = float(stockAmounts[2])

    # get buy number of each stock
    stock1 = {'symbol': stock1Symbol, 'amount': stock1Amount, 'buyNumber': 0}
    stock2 = {'symbol': stock2Symbol, 'amount': stock2Amount, 'buyNumber': 0}
    stock3 = {'symbol': stock3Symbol, 'amount': stock3Amount, 'buyNumber': 0}
    getBuyNumber(stock1, stock2, stock3)

    # get historic data
    history = getHistoricData(stock1Symbol, stock2Symbol, stock3Symbol)

    stock1['history'] = history[stock1Symbol]['chart']
    stock2['history'] = history[stock2Symbol]['chart']
    stock3['history'] = history[stock3Symbol]['chart']

    setHistoryTodayValue(stock1, stock2, stock3)
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
        js_stock_total.append(
            stock1['history'][-i]['total'] + stock2['history'][i]['total'] + stock3['history'][i]['total'])

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

    date1 = stock1['history'][0]['date']
    date2 = stock1['history'][1]['date']
    date3 = stock1['history'][2]['date']
    date4 = stock1['history'][3]['date']
    date5 = stock1['history'][4]['date']

    date1Total = stock1['history'][0]['total'] + stock2['history'][0]['total'] + stock3['history'][0]['total']
    date2Total = stock1['history'][1]['total'] + stock2['history'][1]['total'] + stock3['history'][1]['total']
    date3Total = stock1['history'][2]['total'] + stock2['history'][2]['total'] + stock3['history'][2]['total']
    date4Total = stock1['history'][3]['total'] + stock2['history'][3]['total'] + stock3['history'][3]['total']
    date5Total = stock1['history'][4]['total'] + stock2['history'][4]['total'] + stock3['history'][4]['total']

    if request.method == 'POST':
        with open("history.json", 'r') as hist_file:
            history = json.loads(hist_file.read())
            if email in history:
                history[email].append([stock1Amount, stock2Amount, stock3Amount,
                                       stock1Symbol, stock2Symbol, stock3Symbol,
                                       totalValueNow, "{:%B %d, %Y}".format(datetime.datetime.now())])
            else:
                history[email] = [[stock1Amount, stock2Amount, stock3Amount,
                                   stock1Symbol, stock2Symbol, stock3Symbol,
                                   totalValueNow, "{:%B %d, %Y}".format(datetime.datetime.now())]]
        with open("history.json", 'w') as hist_file:
            sendmail(name, email, history[email][-1])
            json.dump(history, hist_file)

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


def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """

    names = ['Navoday']
    emails = ['navoday.91@gmail.com']
    return names, emails


def read_template(filename):
    """
    Returns a Template object comprising the contents of the
    file specified by filename.
    """

    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def sendmail(name, email, quote_data):
    message_template = read_template('message.txt')
    # set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    MY_ADDRESS = 'cmpe285spartans@gmail.com'
    PASSWORD = 'test@cmpe285'
    s.login(MY_ADDRESS, PASSWORD)
    # For each contact, send the email:
    msg = MIMEMultipart()  # create a message

    # add in the actual person name to the message template
    message = message_template.substitute(PERSON_NAME=name.title(),
                                          stockamount1=quote_data[0],
                                          stockamount2=quote_data[1],
                                          stockamount3=quote_data[2],
                                          stockname1=quote_data[3],
                                          stockname2=quote_data[4],
                                          stockname3=quote_data[5],
                                          total_amount=quote_data[6])

    # setup the parameters of the message
    msg['From'] = MY_ADDRESS
    msg['To'] = email
    msg['Subject'] = "Your recent query at CMPE285 Invest"

    # add in the message body
    msg.attach(MIMEText(message, 'plain'))

    # send the message via the server set up earlier.
    s.send_message(msg)
    del msg

    # Terminate the SMTP session and close the connection
    s.quit()


############################ FUNCTIONS ############################
def getMapStocks(strategy, substrategy=None):
    result = {"Ethical Investing": {
        "alt_energy": ["NYLD", "PEGI", "AY", "NEE", "FSLR", "SEDG", "REGI", "GPRE", "TOT"],
        "zero_waste": ["WM", "RSG", "CVA"], "water": ["DHR", "XYL", "PNR"],
        "reduce": ["BIP", "USCR", "REGI", "GPRE"], "reuse": ["IP", "NYLD", "PEGI", "AY"],
        "sustain": ["WY", "PEGI", "AY", "NEE"]},
        "Index Investing": ["VOO", "SCHA", "VYM", "FSTMX", "VTSMX", "VEU", "SCHZ", "BLV", "GAMR", "VSS"],
        "Growth Investing": ["SBUX", "NXPI", "FB", "SFIX", "JNJ", "BRK.B", "BRK.A", "CNC", "AAPL", "SFM", "DWDP"],
        "Quality Investing": ["GOOG", "AMZN", "AWK", "AAPL", "DIS", "FB", "NKE", "MSFT", "BAC", "ADP"],
        "Value Investing": ["AAL", "ALL", "AZO", "DHI", "KHC", "MPC", "NFX", "PHM", "UAL", "URI"]}

    if strategy == "Ethical Investing":
        index = random.randint(0, 3)
        list_ethics = ["alt_energy",
                       "zero_waste",
                       "reduce",
                       "sustain"
                       ]
        result = result[strategy][list_ethics[index]]
    else:
        result = result[strategy]
    l = len(result)
    index_list = []
    while len(index_list) < 3:
        num = random.randint(0, l - 1)
        if num not in index_list:
            index_list.append(num)

    return [result[i] for i in index_list]


def getHistoricData(symbol1, symbol2, symbol3):
    url = 'https://api.iextrading.com/1.0/stock/market/batch?symbols=' + symbol1 + ',' + symbol2 + ',' + symbol3 + '&types=chart&range=1m&last=5&filter=date,close'
    json_str = requests.get(url)
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
    app.secret_key = 'NRRACMPE285'
    app.run(port=80, host='0.0.0.0')
