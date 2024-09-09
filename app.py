from flask import Flask, request, render_template

from flask_pydantic import validate

from config import Config

from common.jsontools import *

# 引入实体类
from entityModels import *

app = Flask(__name__)
app.config.from_object(Config)

import pymysql
from pymysql import cursors
from dbutils.pooled_db import PooledDB

pool = PooledDB(
    creator=pymysql,
    # 创建最大连接
    maxconnections=6,
    mincached=2,
    maxcached=3,
    maxshared=4,
    blocking=True,
    maxusage=None,
    setsession=[],
    ping=0,
    # 这一坨会传给上面的 pymysql
    host='localhost',
    port=3306,
    user='root',
    passwd='',
    database='binance_demo',
    charset='utf8',
    # 让查询结果是一个 dict
    cursorclass=cursors.DictCursor
)


@app.route('/')
def home():
    # Passing dynamic content to the Jinja template
    return render_template('index.html',
                           title="My Flask App",
                           heading="Welcome to My Flask App",
                           content="This is a sample Jinja page.",
                           items=['Flask', 'Jinja2', 'Python'],
                           user="John Doe")


@app.route('/buy', methods=['POST'])
@validate()
def buy(body: Order):
    buyOrder = body
    try:
        trade(buyOrder.price, buyOrder.amount, 'buy')
        return response(code=200, message="Sell Success")
    except pymysql.Error as e:
        return response(code=500, message=f"Database error: {e}")


@app.route('/sell', methods=['POST'])
@validate()
def sell(body: Order):
    sellOrder = body
    try:
        trade(sellOrder.price, sellOrder.amount, 'sell')
        return response(code=200, message="Sell Success")
    except pymysql.Error as e:
        return response(code=500, message=f"Database error: {e}")


def trade(price, amount, type):
    selectBuyOrderSql = "select id, order_price, order_amount, processed_amount from order_book where order_price <= %s and status = 0 and type = %s order by order_price asc"
    selectSellOrderSql = "select id, order_price, order_amount, processed_amount from order_book where order_price >= %s and status = 0 and type = %s order by order_price asc"

    updateOrderSql = "update order_book set processed_amount = %s, status = %s where id = %s"
    createOrderSql = "insert into order_book (type, order_price, order_amount) values (%s, %s, %s)"
    createTradeSql = "insert into trade_record (trade_price, trade_amount) values (%s, %s)"

    selectType = 'sell' if type == 'buy' else 'buy'
    selectOrderSql = selectBuyOrderSql if type == 'buy' else selectSellOrderSql

    conn = pool.connection()

    try:
        cursor = conn.cursor()
        cursor.execute(selectOrderSql, (price, selectType))
        orders = cursor.fetchall()
        if orders is not None:
            for order in orders:
                restAmount = order['order_amount'] - order['processed_amount']
                amount -= restAmount
                if amount > 0:
                    cursor.execute(updateOrderSql, (order['order_amount'], 1, order['id']))
                    cursor.execute(createTradeSql,
                                   (order['order_price'] if type == 'buy' else price, restAmount))
                else:
                    cursor.execute(updateOrderSql,
                                   (order['order_amount'] + amount, 0, order['id']))
                    cursor.execute(createTradeSql,
                                   (order['order_price'] if type == 'buy' else price, restAmount + amount))
                    break

        if amount > 0:
            cursor.execute(createOrderSql, (type, price, amount))

        conn.commit()
        conn.close()
    except pymysql.Error as e:
        conn.rollback()
        return response(code=500, message=f"Database error: {e}")


@app.route('/getOrderList', methods=['GET'])
def getOrderList():
    try:
        sellList, buyList = getOrders('sell'), getOrders('buy')
        orderList = {
            'sellList': sellList,
            'buyList': buyList,
            'maxBuyPrice': 0 if buyList is None else buyList[0]['price']
        }
        return response(code=200, message="Order List", data=orderList)
    except pymysql.Error as e:
        return response(code=500, message=f"an error occurred: Database error: {e}")


def getOrders(type):
    getOrderListSql = "select order_price, order_amount, processed_amount from order_book where type = %s and status = 0 order by order_price desc"
    orderList = []

    conn = pool.connection()

    try:
        cursor = conn.cursor()
        cursor.execute(getOrderListSql, (type,))
        orders = cursor.fetchall()
        if orders is not None:
            for order in orders:
                orderList.append({
                    'price': order['order_price'],
                    'amount': order['order_amount'] - order['processed_amount']
                })
        conn.close()
        return orderList
    except pymysql.Error as e:
        conn.rollback()


@app.route('/getTradeList', methods=['GET'])
def getTradeList():
    # endTime = datetime.now()
    # startTime = endTime - timedelta(minutes=10)
    sql = "select trade_price, trade_amount, create_time from trade_record order by create_time desc limit 50"
    # sql = "select trade_price, trade_amount, create_time from trade_record where create_time between %s and %s order by create_time desc limit 50"

    conn = pool.connection()

    try:
        tradeList = []

        cursor = conn.cursor()
        cursor.execute(sql)
        # cursor.execute(conn.escape_string(sql), (startTime, endTime))
        trades = cursor.fetchall()
        if trades is not None:
            for trade in trades:
                tradeList.append({
                    'price': trade['trade_price'],
                    'amount': trade['trade_amount'],
                    'create_time': trade['create_time'].strftime("%H:%M:%S")
                })
        res = {'tradeList': tradeList}
        conn.close()
        return response(code=200, message="Trade List", data=res)
    except pymysql.Error as e:
        conn.rollback()
        return response(code=500, message=f"an error occurred: Database error: {e}")


# get chart data
@app.route('/getChart', methods=['GET'])
@validate()
def getChart(query: Interval):
    interval = query.interval
    sql = '''
            SELECT 
                UNIX_TIMESTAMP(DATE_FORMAT(DATE_SUB(create_time, INTERVAL SECOND(create_time) SECOND), '%%Y-%%m-%%d %%H:%%i:00'))*1000 AS `timestamp`,
                MIN(trade_price) AS min_price,
                MAX(trade_price) AS max_price,
                (SELECT trade_price FROM trade_record t2 
                WHERE DATE_FORMAT(t2.create_time, '%%Y-%%m-%%d %%H:%%i') = DATE_FORMAT(t1.create_time, '%%Y-%%m-%%d %%H:%%i')
                ORDER BY t2.create_time ASC LIMIT 1) AS first_price,
                (SELECT trade_price FROM trade_record t2 
                WHERE DATE_FORMAT(t2.create_time, '%%Y-%%m-%%d %%H:%%i') = DATE_FORMAT(t1.create_time, '%%Y-%%m-%%d %%H:%%i')
                ORDER BY t2.create_time DESC LIMIT 1) AS last_price,
                SUM(trade_amount) AS total_amount
            FROM 
                trade_record t1
            WHERE 
                create_time >= NOW() - INTERVAL %s HOUR
                AND del_flag = '0'
            GROUP BY 
                DATE_FORMAT(create_time, '%%Y-%%m-%%d %%H:%%i')
            ORDER BY 
                `timestamp`;'''

    conn = pool.connection()

    try:
        cursor = conn.cursor()
        cursor.execute(sql, (interval,))
        db_list = cursor.fetchall()
        temp = {}
        result = []
        if (db_list is not None):
            for db in db_list:
                temp = {
                    "timestamp": db[0],
                    "low": float(db[1]),
                    "high": float(db[2]),
                    "open": float(db[3]),
                    "close": float(db[4]),
                    "volume": float(db[5]),
                }
                result.append(temp.copy())
            print("result:", result)
        return response(code=200, message="get chart data success", data=result)
    except pymysql.Error as e:
        conn.rollback()
        return response(code=500, message=f"an error occurred: Database error: {e}")


if __name__ == '__main__':
    host = app.config.get('HOST', '127.0.0.1')  # 默认值为 '127.0.0.1'，如果未找到 'HOST' 配置项
    port = app.config.get('PORT', 5000)  # 默认值为 5000，如果未找到 'PORT' 配置项
    app.run(host=host, port=port)
