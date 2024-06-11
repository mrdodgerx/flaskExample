from modules.postgresdb import POSTGRES
from flask import jsonify

def getdata():
    db = POSTGRES()
    results = db.query(sql='select * from newtable n ;')
    db.close()
    return results

def insert_data(data):
    db = POSTGRES()
    try:
        for d in data:
            print(d['column1'], d['column2'])
            sql_insert = '''
            INSERT INTO newtable
                    (column1, column2)
            VALUES(%s, %s);
            '''
            db.execute(sql=sql_insert, args=(d['column1'], d['column2'], ))
        db.commit() 
        db.close()
        # print(xx)
        return {
                "msg": "success"
            }
    except Exception as err:
        return{
                "msg": err
            }