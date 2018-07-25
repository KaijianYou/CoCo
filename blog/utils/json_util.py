from flask import jsonify


def generate_success_json(result=None):
    result = {} if result is None else result
    data = {
        'status': 'OK',
        'data': result
    }
    return jsonify(data)


def generate_error_json(error):
    data = {
        'status': 'ERROR',
        'errorCode': error.code,
        'errorMessage': error.message
    }
    return jsonify(data)

