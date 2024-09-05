# !pip install pysnowflake


import time
from datetime import datetime

import snowflake.client

# 定义常量
DEL_FLAG = 0  # 删除标志位默认值

# 链接服务端并初始化一个pysnowflake客户端
host = 'localhost'
port = 8910
snowflake.client.setup(host, port)

    

# 主键id生成器
def generate_id(worker_id = 1, data_center_id = 1, sequence = 0):
    return snowflake.client.get_guid()
    # worker = IdWorker(worker_id, data_center_id, sequence)
    # return worker.get_id()
    
    # # 获取当前时间戳
    # current_timestamp = int(time.time_ns())
    # return current_timestamp

    # # # 将时间戳转换为16进制字符串,并删除前两个字符"0x"
    # # id_str = hex(current_timestamp)[2:]
    # # # 如果长度不足16位,则在前面补0
    # # id_str = id_str.zfill(20)
    # # return int(id_str, 20)


# 时间戳生成器
def generate_time():
    # 格式: YY-MM-DD HH:MM:SS
    form_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    # print(form_time)
    return form_time



# 数据插入前预处理 -- 主键由smowflake生成版
# def pre_insert(item):
#     item.id, item.create_time, item.del_flag = generate_id(), generate_time(), DEL_FLAG
#     return item

# 数据插入前预处理--主键自增版
def pre_insert(item):
    item.create_time, item.del_flag = generate_time(), DEL_FLAG
    return item


# 将datetime类型的数据转换为字符串，以便后续json格式化
def datetime_serializer(obj):
    if isinstance(obj, datetime):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
    