from flasgger import swag_from
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os, time

from modules import insitu

insitu_bp = Blueprint('insitu_bp', __name__)

# post pictures
@insitu_bp.route("/picture", methods=['GET'])
@cross_origin()
@swag_from('swagger/insitu/picture.yml')
def upload():
    station_name = request.form.get('station_name')
    file = request.files.get('file')
    
    if not station_name:
        return jsonify({"error": "Please station not found"}), 400
    if not file:
        return jsonify({"error": "No image selected."}), 400

    if file:
        return insitu.post_picture(station_name.strip(), file.read())

# get pictures
@insitu_bp.route("/picture/<station_name>", methods=['GET'])
@cross_origin()
@swag_from('swagger/insitu/get_picture.yml')
def get_picture(station_name):

    if not station_name:
        return jsonify({"error": "station name not found"}), 400
    else:
        return insitu.get_picture(station_name.strip())
    
#get manual station
@insitu_bp.route("/manual_stations", methods=['GET'])
@cross_origin()
@swag_from('swagger/insitu/manual_station.yml')
def manual_station():
    return insitu.list_manual_station()


# insert manual data  -- insitu
@insitu_bp.route("/manual_data", methods=['POST'])
@cross_origin()
@swag_from('swagger/insitu/manual_data.yml')
def manual_data():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    obj_json = request.json.get('obj_json', None)
    return insitu.insert_manual(obj_json)

# insert Investigate Study  -- insitu
@insitu_bp.route("/is_data", methods=['POST'])
@cross_origin()
@swag_from('swagger/insitu/is_data.yml')
def is_data():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    obj_json = request.json.get('obj_json', None)
 

    return insitu.insert_IS(obj_json)

@insitu_bp.route("/upload_db", methods=['POST'])
@cross_origin()
@swag_from('swagger/insitu/upload_db.yml')
def upload_sqlite_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"})

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No selected file"})

        if file:
            filename = file.filename
            file.save(filename)
            data = insitu.process_sqlite_database(filename)
            try:
                # Attempt to delete the file
                time.sleep(1)
                os.remove(filename)
                print(f"File '{filename}' has been deleted.")
            except OSError as e:
                print(f"Error: {e}")

            return jsonify({"obj_json": data})

    except Exception as e:
        return jsonify({"error": str(e)})