from flask import jsonify


def gen_success_json(result=None):
    result = {} if result is None else result
    data = {
        'success': True,
        'data': result
    }
    return jsonify(data)


def gen_error_json(error):
    data = {
        'success': False,
        'errorCode': error.code,
        'errorMessage': error.message
    }
    return jsonify(data)

