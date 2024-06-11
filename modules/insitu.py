import os
import io
from PIL import Image
from flask import jsonify, make_response
from configparser import ConfigParser
from datetime import datetime
from modules.postgresdb import POSTGRES
from modules.sqlitedb import SqliteDb

import secrets
import string

# config = ConfigParser()
# config.sections()
# config.read('env.ini')

# SECRET_KEY = config['DEFAULT']["SECRET_KEY"]
# ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']


def get_picture(station_name):
    sql = 'SELECT * FROM public.insitu_picture where station_name =%s;'

    try:
        db = POSTGRES()
        result = db.query(sql=sql, args=(station_name,), one=True)
        db.close()

        if result:
            result_picture = f"uploads/{result['picture_file_name']}"
            with open(result_picture, 'rb') as file:
                image_data = file.read()

            response = make_response(image_data)
            response.headers.set('Content-Type', 'image/jpg')
            return response
        else:
            result_picture = f"uploads/no-image.png"
            with open(result_picture, 'rb') as file:
                image_data = file.read()
            response = make_response(image_data)
            response.headers.set('Content-Type', 'image/jpg')
            return response
    except Exception as e:
        return jsonify({"status": False, "message": str(e)}), 500

def post_picture(station_name, file):
    try:
        picture_file_name = generate_random_string(12)
        file_path = os.path.join('uploads', picture_file_name)
        image = Image.open(io.BytesIO(file))
        image.save(file_path, format='PNG', optimize=True)
    except Exception as err:
        return jsonify({'msg': 'invalid format'}),500
    # insert 
    try:
        query = "INSERT INTO  public.insitu_picture  (station_name, picture_file_name) VALUES (%s, %s)"
        db = POSTGRES()
        db.execute(sql=query, args=(station_name, picture_file_name,))
        db.commit()
        db.close()

        return jsonify({
            "status": True,
            "message": "Your image has been uploaded.",
            "datetime": datetime.now()
        }),200
    except Exception as err:
        # update
        try:
            query_update = "UPDATE public.insitu_picture SET picture_file_name = %s WHERE station_name = %s;"
            db_update = POSTGRES()
            # print(picture_file_name)
            db_update.execute(sql=query_update, args=(picture_file_name,station_name, ))
            db_update.commit()
            db_update.close()
            
            return jsonify({
                "status": True,
                "message": "Your image has been uploaded.",
                "datetime": datetime.now()
            }),200
        except Exception as err:
            return jsonify({
                "status": False,
                "error": "Internal server error.",
                "message": str(err)
            }),500

def generate_random_string(length):
    alphabet = string.ascii_letters + string.digits  # You can customize this as needed
    random_string = ''.join(secrets.choice(alphabet) for _ in range(length))
    return random_string

def list_manual_station():
    try:
        sql = 'Select distinct("STATION_ID") from "MANUAL"."MIQIMS_MANSAMPLE_INPUT";'
        db = POSTGRES()
        results = db.query(sql=sql)
        db.close()
        return jsonify({'data': results}),200
    except Exception as err:
        return jsonify({'msg': err}),500
    
    
# # INVESTIGATE_STUDY
# # -----INSITU

def insert_IS(obj_json):
    have_error = False
    for obj in obj_json:
        try:
            sql = '''
            INSERT 
                INTO "INVESTIGATE_STUDY"."MIQIMS_INPUT"("STATION_ID", "SAMPLE_ID", "DATETIME", "DO_CON", "DO_SAT", "pH", "pH_MV", 
            "TEMPERATURE", "TURBIDITY", "ACTUAL_CONDUCTIVITY", "SPECIFIC_CONDUCTIVITY", "SALINITY", "RESISTIVITY", "DENSITY", 
            "TDS", "OXYGEN_PARTIAL_PRESSURE", "ORP", "BAROMETRIC_PRESSURE", "PRESSURE", "DEPTH", "EXTERNAL_VOLTAGE", "BATTERY_CAPACITY", 
            "LATITUDE", "LONGITUDE")
            VALUES(%s, %s , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s, %s, %s, %s, %s, %s, %s);
        
                    '''
            db = POSTGRES()
            db.execute(sql=sql, args=(obj['STATION_ID'], obj['SAMPLE_ID'], obj['DATETIME'], obj['DO_CON'], obj['DO_SAT'], 
                                    obj['pH'] ,obj['pH_MV'], obj['TEMPERATURE'],obj['TURBIDITY'], obj['ACTUAL_CONDUCTIVITY'], 
                                    obj['SPECIFIC_CONDUCTIVITY'], obj['SALINITY'], obj['RESISTIVITY'], obj['DENSITY'], obj['TDS'], 
                                    obj['OXYGEN_PARTIAL_PRESSURE'], obj['ORP'], obj['BAROMETRIC_PRESSURE'], obj['PRESSURE'], 
                                    obj['DEPTH'], obj['EXTERNAL_VOLTAGE'], obj['BATTERY_CAPACITY'], obj['LATITUDE'], obj['LONGITUDE'],))
            db.commit()
            db.close()
        except Exception as err:
            try:
                sql = '''
                    UPDATE "INVESTIGATE_STUDY"."MIQIMS_INPUT"
                    SET "DO_CON" = %s, "DO_SAT" = %s, "pH" = %s, "pH_MV" = %s,
                        "TEMPERATURE" = %s, "TURBIDITY" = %s, "ACTUAL_CONDUCTIVITY" = %s,
                        "SPECIFIC_CONDUCTIVITY" = %s, "SALINITY" = %s, "RESISTIVITY" = %s,
                        "DENSITY" = %s, "TDS" = %s, "OXYGEN_PARTIAL_PRESSURE" = %s, "ORP" = %s,
                        "BAROMETRIC_PRESSURE" = %s, "PRESSURE" = %s, "DEPTH" = %s, "EXTERNAL_VOLTAGE" = %s,
                        "BATTERY_CAPACITY" = %s, "LATITUDE" = %s, "LONGITUDE" = %s
                    WHERE "STATION_ID" = %s AND "SAMPLE_ID" = %s and "DATETIME" = %s;
                '''

                db = POSTGRES()
                db.execute(sql=sql, args=( obj['DO_CON'], obj['DO_SAT'], obj['pH'], obj['pH_MV'],
                                        obj['TEMPERATURE'], obj['TURBIDITY'], obj['ACTUAL_CONDUCTIVITY'],
                                        obj['SPECIFIC_CONDUCTIVITY'], obj['SALINITY'], obj['RESISTIVITY'],
                                        obj['DENSITY'], obj['TDS'], obj['OXYGEN_PARTIAL_PRESSURE'], obj['ORP'],
                                        obj['BAROMETRIC_PRESSURE'], obj['PRESSURE'], obj['DEPTH'],
                                        obj['EXTERNAL_VOLTAGE'], obj['BATTERY_CAPACITY'], obj['LATITUDE'],
                                        obj['LONGITUDE'], obj['STATION_ID'], obj['SAMPLE_ID'],obj['DATETIME'],))
                db.commit()
                db.close()
            except Exception as err:
                print(err)
                have_error = True
                
    if have_error:
        return jsonify({'msg': 'have error in update/insert data'})
    return jsonify({'msg': 'success'})

def insert_manual(obj_json):
    have_error = False
    for obj in obj_json:
        try:
            sql = '''
            INSERT 
                INTO "MANUAL"."MIQIMS_MANSAMPLE_INPUT"("STATION_ID", "SAMPLE_ID", "DATETIME", "DO_CON", "DO_SAT", "pH", "pH_MV", 
            "TEMPERATURE", "TURBIDITY", "ACTUAL_CONDUCTIVITY", "SPECIFIC_CONDUCTIVITY", "SALINITY", "RESISTIVITY", "DENSITY", 
            "TDS", "OXYGEN_PARTIAL_PRESSURE", "ORP", "BAROMETRIC_PRESSURE", "PRESSURE", "DEPTH", "EXTERNAL_VOLTAGE", "BATTERY_CAPACITY", 
            "LATITUDE", "LONGITUDE")
            VALUES(%s, %s , %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s, %s, %s, %s, %s, %s, %s);
        
                    '''
            db = POSTGRES()
            db.execute(sql=sql, args=(obj['STATION_ID'], obj['SAMPLE_ID'], obj['DATETIME'], obj['DO_CON'], obj['DO_SAT'], 
                                    obj['pH'] ,obj['pH_MV'], obj['TEMPERATURE'],obj['TURBIDITY'], obj['ACTUAL_CONDUCTIVITY'], 
                                    obj['SPECIFIC_CONDUCTIVITY'], obj['SALINITY'], obj['RESISTIVITY'], obj['DENSITY'], obj['TDS'], 
                                    obj['OXYGEN_PARTIAL_PRESSURE'], obj['ORP'], obj['BAROMETRIC_PRESSURE'], obj['PRESSURE'], 
                                    obj['DEPTH'], obj['EXTERNAL_VOLTAGE'], obj['BATTERY_CAPACITY'], obj['LATITUDE'], obj['LONGITUDE'],))
            db.commit()
            db.close()
        except Exception as err:
            try:
                sql = '''
                    UPDATE "MANUAL"."MIQIMS_MANSAMPLE_INPUT"
                    SET "DO_CON" = %s, "DO_SAT" = %s, "pH" = %s, "pH_MV" = %s,
                        "TEMPERATURE" = %s, "TURBIDITY" = %s, "ACTUAL_CONDUCTIVITY" = %s,
                        "SPECIFIC_CONDUCTIVITY" = %s, "SALINITY" = %s, "RESISTIVITY" = %s,
                        "DENSITY" = %s, "TDS" = %s, "OXYGEN_PARTIAL_PRESSURE" = %s, "ORP" = %s,
                        "BAROMETRIC_PRESSURE" = %s, "PRESSURE" = %s, "DEPTH" = %s, "EXTERNAL_VOLTAGE" = %s,
                        "BATTERY_CAPACITY" = %s, "LATITUDE" = %s, "LONGITUDE" = %s
                    WHERE "STATION_ID" = %s AND "SAMPLE_ID" = %s and "DATETIME" = %s;
                '''

                db = POSTGRES()
                db.execute(sql=sql, args=( obj['DO_CON'], obj['DO_SAT'], obj['pH'], obj['pH_MV'],
                                        obj['TEMPERATURE'], obj['TURBIDITY'], obj['ACTUAL_CONDUCTIVITY'],
                                        obj['SPECIFIC_CONDUCTIVITY'], obj['SALINITY'], obj['RESISTIVITY'],
                                        obj['DENSITY'], obj['TDS'], obj['OXYGEN_PARTIAL_PRESSURE'], obj['ORP'],
                                        obj['BAROMETRIC_PRESSURE'], obj['PRESSURE'], obj['DEPTH'],
                                        obj['EXTERNAL_VOLTAGE'], obj['BATTERY_CAPACITY'], obj['LATITUDE'],
                                        obj['LONGITUDE'], obj['STATION_ID'], obj['SAMPLE_ID'],obj['DATETIME'],))
                db.commit()
                db.close()
            except Exception as err:
                print(err)
                have_error = True
                
    if have_error:
        return jsonify({'msg': 'have error in update/insert data'})
    return jsonify({'msg': 'success'})

    
def process_sqlite_database(db_filename):
    try:
        db = SqliteDb(path=db_filename)
        sql = '''
        SELECT
            l.id,
            l.cloud_id,
            l.name,
            l.description,
            r.time_offset,
            r.started AS r_started,
            r.stopped AS r_stopped,
            DATETIME(r.started / 65536 + r.time_offset, 'unixepoch') AS started_time,
            DATETIME(r.stopped / 65536 + r.time_offset, 'unixepoch') AS stopped_time,
            m.device_id,
            m.quality,
            m.session_id,
            m.latitude,
            m.longitude,
            DATETIME(m.created / 65536 + r.time_offset, 'unixepoch') AS created,
            MAX(CASE WHEN m.parameter_type = 25 THEN printf("%.6f", m.value) END) AS Turbidity,
            MAX(CASE WHEN m.parameter_type = 9 THEN printf("%.6f", m.value) END) AS Actual_Conductivity,
            MAX(CASE WHEN m.parameter_type = 10 THEN printf("%.6f", m.value) END) AS Specific_Conductivity,
            MAX(CASE WHEN m.parameter_type = 12 THEN printf("%.6f", m.value) END) AS Salinity,
            MAX(CASE WHEN m.parameter_type = 11 THEN printf("%.6f", m.value) END) AS Resistivity,
            MAX(CASE WHEN m.parameter_type = 14 THEN printf("%.6f", m.value) END) AS Density_of_Water,
            MAX(CASE WHEN m.parameter_type = 13 THEN printf("%.6f", m.value) END) AS Total_Dissolved_Solids,
            MAX(CASE WHEN m.parameter_type = 20 THEN printf("%.6f", m.value) END) AS Dissolved_Oxygen_Concentration,
            MAX(CASE WHEN m.parameter_type = 21 THEN printf("%.6f", m.value) END) AS Dissolved_Oxygen_Percentage_Saturation,
            MAX(CASE WHEN m.parameter_type = 30 THEN printf("%.6f", m.value) END) AS Oxygen_Partial_Pressure,
            MAX(CASE WHEN m.parameter_type = 17 THEN printf("%.6f", m.value) END) AS pH,
            MAX(CASE WHEN m.parameter_type = 18 THEN printf("%.6f", m.value) END) AS pH_mV,
            MAX(CASE WHEN m.parameter_type = 19 THEN printf("%.6f", m.value) END) AS ORP,
            MAX(CASE WHEN m.parameter_type = 1 THEN printf("%.6f", m.value) END) AS Temperature,
            MAX(CASE WHEN m.parameter_type = 16 THEN printf("%.6f", m.value) END) AS Barometric_Pressure,
            MAX(CASE WHEN m.parameter_type = 2 THEN printf("%.6f", m.value) END) AS Pressure,
            MAX(CASE WHEN m.parameter_type = 3 THEN printf("%.6f", m.value) END) AS Depth,
            MAX(CASE WHEN m.parameter_type = 32 THEN printf("%.6f", m.value) END) AS External_Voltage,
            MAX(CASE WHEN m.parameter_type = 33 THEN printf("%.6f", m.value) END) AS Battery_Capacity_Remaining
        FROM
            location l
        INNER JOIN recording r ON r.location_id = l.id
        INNER JOIN measurement m ON m.created BETWEEN r.started AND r.stopped 

        GROUP BY
            l.id,
            l.cloud_id,
            l.name,
            l.description,
            started_time,
            stopped_time,
            m.device_id,
            m.quality,
            m.session_id,
            m.latitude,
            m.longitude,
            m.created
        ORDER BY created;
        '''
        results = db.query(sql=sql)
        
        return results

    except Exception as e:
        return {"error": str(e)}

    finally:
        db.close()
