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

db = pymysql.connect(host='localhost', port =13306, user='root', password='5903q1w2e3@Q', db='binance_demo', charset='utf8mb3') #本地
cursor = db.cursor()

cursor.execute("SELECT VERSION()")
 
# 使用 fetchone() 方法获取单条数据.
data = cursor.fetchone()
 
print ("Database version : %s " % data)


@app.route('/')
def hello():
    return 'Hello, Flask!'



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

if __name__ == '__main__':
    host = app.config.get('HOST', '127.0.0.1')  # 默认值为 '127.0.0.1'，如果未找到 'HOST' 配置项
    port = app.config.get('PORT', 5000)  # 默认值为 5000，如果未找到 'PORT' 配置项
    app.run(host=host, port=port)   