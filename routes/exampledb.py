from flasgger import swag_from
from flask import Blueprint, jsonify, request
from flask_cors import cross_origin

from modules import exampledb


dbconnect = Blueprint('dbconnect', __name__)


@dbconnect.route("/getdata", methods=['GET'])
@cross_origin()
@swag_from('swagger/insitu/picture.yml')
def getdata():
    return  jsonify(exampledb.getdata()),200

@dbconnect.route("/insert_data", methods=['POST'])
@cross_origin()
@swag_from('swagger/exampledb/insert_data.yml')
def insert_data():
    try:
        if not request.is_json:
            return jsonify({"msg": "Missing JSON in request"}), 400

        data = request.json.get('data', None)

        return  jsonify( exampledb.insert_data(data)),200
    except Exception as err:
        return  jsonify({
            "msg" :err
        }),500