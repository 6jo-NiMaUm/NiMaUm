from gevent import monkey;

monkey.patch_all()
from flask import Flask, Response, render_template, stream_with_context, request, jsonify
from gevent.pywsgi import WSGIServer
import json
import time

from pymongo import MongoClient
import certifi

app = Flask(__name__)
counter = 100

client = MongoClient('mongodb+srv://test:sparta@cluster0.i7caukz.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=certifi.where())
db = client.dbsparta


# ##############################
@app.route("/")
def render_index():
    return render_template("SSE.html")


@app.route("/test", methods=["POST"])
def test():
    te_receive = request.form['te_give']
    star_receive = request.form['star_give']

    doc = {
        'comment': te_receive,
        'star': star_receive
    }

    db.test.insert_one(doc)
    return jsonify({'msg': '응원댓글 달기 완료!'})

##############################
@app.route("/listen")
def listen():
    def respond_to_client():

        stream = db.test.watch(full_document="updateLookup", full_document_before_change="whenAvailable")
        for docu in stream:

            _data = json.dumps({
                "nick": docu['fullDocument']['comment'],
                "coffee": docu['fullDocument']['star'],
                "energy": docu['fullDocument']['energy_count'],
                "drink": docu['fullDocument']['drink_count'],
                "carbon": docu['fullDocument']['carbon_count'],
                "etc": docu['fullDocument']['etc_count']
            })
            yield f"id: 1\ndata: {_data}\nevent: online\n\n"

    return Response(respond_to_client(), mimetype='text/event-stream')

#
# ##############################
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

