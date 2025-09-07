from flask import jsonify

def success_response(data, code=200):
    return jsonify({"status": "success", "data": data}), code

def fail_response(reason, code=400):
    return jsonify({"status": "fail", "reason": reason}), code

def error_response(e, code=500):
    return jsonify({"status": "error", "reason": str(e)}), code