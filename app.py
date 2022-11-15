from gevent import monkey;

monkey.patch_all()
from flask import Flask, Response, render_template, stream_with_context, request, jsonify
from gevent.pywsgi import WSGIServer
import json
import time

from pymongo import MongoClient

app = Flask(__name__)
counter = 100

client = MongoClient('mongodb+srv://test:sparta@cluster0.i7caukz.mongodb.net/Cluster0?retryWrites=true&w=majority')
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

        stream = db.watch(full_document="updateLookup")
        for docu in stream:

            _data = json.dumps({"update": docu['fullDocument']['comment'], "star": docu['fullDocument']['star']})
            yield f"id: 1\ndata: {_data}\nevent: online\n\n"

    return Response(respond_to_client(), mimetype='text/event-stream')

#
# ##############################
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

