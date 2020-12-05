from flask import Flask, Markup, render_template
from flask import request
import json
import sqlite3

app = Flask(__name__)

labels = [
    'JAN', 'FEB', 'MAR', 'APR',
    'MAY', 'JUN', 'JUL', 'AUG',
    'SEP', 'OCT', 'NOV', 'DEC'
]

values = [
    967.67, 1190.89, 1079.75, 1349.19,
    2328.91, 2504.28, 2873.83, 4764.87,
    4349.29, 6458.30, 9907, 16297
]

colors = [
    "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
    "#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
    "#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


@app.route('/temps')
def line():
    line_labels=labels
    line_values=values
    return render_template('line_chart.html', title='Nodes Temprature', max=17000, labels=line_labels, values=line_values)

@app.route('/dump')
def dump_data():
    try:
        c = sqlite3.connect("example.db").cursor()
        sqlite_select_query = """SELECT * from iot_stat"""
        c.execute(sqlite_select_query)
        records = c.fetchall()
        ret = ""
        for rec in records:
             ret += "{}<br>".format(str(rec))
        return ret 
    except Exception as inst:
        return inst
@app.route('/post_data',methods=["POST"])
def post_data():
    try:
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        for elm in request.json:
            nd_id = elm["node_id"]
            nd_type = elm["type"]
            nd_time = elm["time"]
            nd_val = elm["value"]
            query = """INSERT INTO 'iot_stat'
              ('type', 'val', 'node_id', 'val_date')
                          VALUES (?, ?, ?, ?);"""
            data = (nd_type, nd_val, nd_id, nd_time)
            c.execute(query, data)
            conn.commit()
            #print(elm["node_id"])
        #print("Received : {}".format(data))
        return "Good"
    except Exception as inst:
        return {"details" : "{}".format(inst)}



if __name__ == '__main__':
    try:
        conn = sqlite3.connect('example.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE iot_stat
             (
             id INTEGER PRIMARY KEY,
             type TEXT,
             val REAL,
             node_id TEXT,
             val_date timestamp
             );
             '''
             )
    except Exception as inst:
        print("E : {}".format(inst))
    app.run(host='0.0.0.0', port=9999)

