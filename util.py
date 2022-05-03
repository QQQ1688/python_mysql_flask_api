from datetime import datetime


def success(data=None):
    if data is None:
        return {'message': 'success'}, 200

    return {
        'message': 'success',
        'data': data,
        'datatime': datetime.utcnow().isoformat()
    }, 200

def failure(data):
    data["datatime"] = datetime.utcnow().isoformat()
    return data, 500