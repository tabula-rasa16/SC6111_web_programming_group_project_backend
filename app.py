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

db = pymysql.connect(host='localhost', port =13306, user='root', password='admin', db='binance_demo', charset='utf8mb3') #本地 账密替换
cursor = db.cursor()

cursor.execute("SELECT VERSION()")

# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()

print ("Database version : %s " % data)


@app.route('/')
def home():
    # Passing dynamic content to the Jinja template
    return render_template('index.html', 
                           title="My Flask App", 
                           heading="Welcome to My Flask App", 
                           content="This is a sample Jinja page.",
                           items=['Flask', 'Jinja2', 'Python'], 
                           user="John Doe")



@app.route('/order',methods = ['POST'])
@validate()
def order(body: OrderBook):

    order_info = body

    # Add your code here to handle the order route
    user_id = 1

    order_info = pre_insert(order_info)

    # Generate SQL string to insert data into "order_book" table
    sql = "INSERT INTO order_book (user_id, order_price, order_amount, type, create_time, del_flag) VALUES (%s, %s, %s, %s, %s, %s)"
    values = (user_id, order_info.order_price, order_info.order_amount,order_info.order_type,order_info.create_time,order_info.del_flag)

    try:
        # Execute the SQL query
        cursor.execute(sql, values)

        # Commit the changes to the database
        db.commit()
    except pymysql.Error as e:
        db.rollback()
        return response(code = 500, message = f"Database error: {e}")

    # Close the cursor and database connection
    return response(code = 200, message = "Order success!")
    
# get chart data
@app.route('/getChart',methods = ['GET'])
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
        if(db_list is not None):
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
        return response(code = 200, message = "get chart data success", data = result)
    except pymysql.Error as e:
        db.rollback()
        return response(code = 500, message = f"an error occurred: Database error: {e}")

if __name__ == '__main__':
    host = app.config.get('HOST', '127.0.0.1')  # 默认值为 '127.0.0.1'，如果未找到 'HOST' 配置项
    port = app.config.get('PORT', 5000)  # 默认值为 5000，如果未找到 'PORT' 配置项
    app.run(host=host, port=port)
