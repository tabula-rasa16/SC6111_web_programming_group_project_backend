from functools import wraps
from pyexpat.errors import messages

from flask import Flask, request, render_template
import json
import pymysql
from typing import Optional

from flask_pydantic import validate

from config import Config

from common.utils import *
from common.jsontools import *

# 引入实体类
from entityModels import *

app = Flask(__name__)
app.config.from_object(Config)

# Create a MySQL connector

db = pymysql.connect(
    host='localhost',
    port=3306,
    user='root',
    password='Pyh019026',
    database='binance_demo',
    cursorclass=pymysql.cursors.DictCursor)  # 本地 账密替换
cursor = db.cursor()


@app.route('/')
def hello():
    return 'Hello, Flask!'


@app.route('/buy', methods=['POST'])
@validate()
def buy(body: Order):
    buyOrder = body

    selectSellOrderSql = "select id, order_price, order_amount, processed_amount from order_book where order_price <= %s and status = 0 and type = %s order by order_price asc"
    updateSellOrderSql = "update order_book set processed_amount = %s, status = %s where id = %s"
    createBuyOrderSql = "insert into order_book (type, order_price, order_amount) values (%s, %s, %s)"
    createTradeSql = "insert into trade_record (trade_price, trade_amount) values (%s, %s)"

    cursor.execute(db.escape_string(selectSellOrderSql), (buyOrder.price, 'sell'))
    orders = cursor.fetchall()

    try:
        for order in orders:
            sellAmount = order['order_amount'] - order['processed_amount']
            buyOrder.amount -= sellAmount
            if buyOrder.amount > 0:
                cursor.execute(db.escape_string(updateSellOrderSql), (order['order_amount'], 1, order['id']))
                cursor.execute(db.escape_string(createTradeSql), (order['order_price'], sellAmount))
            else:
                cursor.execute(db.escape_string(updateSellOrderSql),
                               (order['order_amount'] + buyOrder.amount, 0, order['id']))
                cursor.execute(db.escape_string(createTradeSql), (order['order_price'], sellAmount + buyOrder.amount))
                break

        if buyOrder.amount > 0:
            cursor.execute(db.escape_string(createBuyOrderSql), ('buy', buyOrder.price, buyOrder.amount))

        db.commit()

        return response(code=200, message="Order Success")

    except pymysql.Error as e:
        db.rollback()
        return response(code=500, message=f"Database error: {e}")


@app.route('/sell', methods=['POST'])
@validate()
def sell(body: Order):
    sellOrder = body

    selectBuyOrderSql = "select id, order_price, order_amount, processed_amount from order_book where order_price <= %s and status = 0 and type = %s order by order_price desc"
    updateBuyOrderSql = "update order_book set processed_amount = %s, status = %s where id = %s"
    createSellOrderSql = "insert into order_book (type, order_price, order_amount) values (%s, %s, %s)"
    createTradeSql = "insert into trade_record (trade_price, trade_amount) values (%s, %s)"

    cursor.execute(db.escape_string(selectBuyOrderSql), (sellOrder.price, 'buy'))
    orders = cursor.fetchall()

    try:
        for order in orders:
            buyAmount = order['order_amount'] - order['processed_amount']
            sellOrder.amount -= buyAmount
            if sellOrder.amount > 0:
                cursor.execute(db.escape_string(updateBuyOrderSql), (order['order_amount'], 1, order['id']))
                cursor.execute(db.escape_string(createTradeSql), (order['order_price'], buyAmount))
            else:
                cursor.execute(db.escape_string(updateBuyOrderSql),
                               (order['order_amount'] + sellOrder.amount, 0, order['id']))
                cursor.execute(db.escape_string(createTradeSql), (order['order_price'], buyAmount + sellOrder.amount))
                break

        if sellOrder.amount > 0:
            cursor.execute(db.escape_string(createSellOrderSql), ('buy', sellOrder.price, sellOrder.amount))

        db.commit()

        return response(code=200, message="Order Success")

    except pymysql.Error as e:
        db.rollback()
        return response(code=500, message=f"Database error: {e}")


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
    try:
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
        db.rollback()
        return response(code=500, message=f"an error occurred: Database error: {e}")


if __name__ == '__main__':
    host = app.config.get('HOST', '127.0.0.1')  # 默认值为 '127.0.0.1'，如果未找到 'HOST' 配置项
    port = app.config.get('PORT', 5000)  # 默认值为 5000，如果未找到 'PORT' 配置项
    app.run(host=host, port=port)
