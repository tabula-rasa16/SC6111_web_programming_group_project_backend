from flask import jsonify
from typing import Union

# 对返回内容进行封装
def response(*, code=200, data: Union[list, dict, str] = None, message="Success"):
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    }), code