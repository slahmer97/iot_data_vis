from flask import Flask, Markup, render_template, redirect
from flask import request
import json
import sqlite3

app = Flask(__name__)

@app.route('/plot_1d_data')
def plot_1d_data():
    data_type = request.args.get("type", "pressure")

    id_cur = sqlite3.connect("example.db").cursor()
    pres_cur = sqlite3.connect("example.db").cursor()

    first = 1
    time_labels = []
    data = []

    id_cur.execute("""SELECT DISTINCT node_id FROM iot_stat""")
    ids = id_cur.fetchall()
    for id in ids:
        row_data = []
        pres_cur.execute("""SELECT val, val_date FROM iot_stat WHERE node_id=? and type=?""", [id[0], data_type])
        records = pres_cur.fetchall()
        for row in records:
            if first:
                time_labels.append(row[1])
            row_data.append(row[0])
        if first:
            first = 0;
        data.append(row_data)
    return render_template('line_chart_1d.html', title='Nodes {}'.format(data_type), labels=time_labels, values=data, id_tab=ids)

@app.route('/plot_3d_data')
def plot_3d_data():
    type = request.args.get("type", "accel")

    id_cur = sqlite3.connect("example.db").cursor()
    data_cur = sqlite3.connect("example.db").cursor()

    first = 1
    time_labels = []
    data_x = []
    data_y = []
    data_z = []

    id_cur.execute("""SELECT DISTINCT node_id FROM iot_stat""")
    ids = id_cur.fetchall()
    for id in ids:
        row_x = []
        row_y = []
        row_z = []
        data_cur.execute("""SELECT val, val_date, type FROM iot_stat WHERE node_id=? and type in (?,?,?)""", [id[0], '{}_x'.format(type), '{}_y'.format(type), '{}_z'.format(type)])
        records = data_cur.fetchall()
        for row in records:
            if row[2] == "{}_x".format(type):
                if first:
                    time_labels.append(row[1])
                row_x.append(row[0])
            elif row[2] == "{}_y".format(type):
                row_y.append(row[0])
            else:
                row_z.append(row[0])
        if first:
            first = 0;
        data_x.append(row_x)
        data_y.append(row_y)
        data_z.append(row_z)

        if(type == "mg"):
            str_type = "magne"
        elif(type == "gr"):
            str_type = "gyros"
        else:
            str_type = type

    return render_template('line_chart_3d.html', title='Nodes {}'.format(str_type), labels=time_labels, val_x=data_x, val_y=data_y, val_z=data_z, id_tab=ids)


@app.route('/')
def home():
    return redirect('/plot_1d_data')

@app.route('/dump')
def dump_data():
    try:
        c = sqlite3.connect("example.db").cursor()
        sqlite_select_query = """SELECT * from iot_stat"""
        c.execute(sqlite_select_query)
        records = c.fetchall()
        ret = ""
        for rec in records:
            ret += "{} {}<br>".format(cnt, str(rec))
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
