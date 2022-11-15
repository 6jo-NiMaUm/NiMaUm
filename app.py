from flask import Flask, render_template, request, jsonify, redirect, url_for

app = Flask(__name__)

from pymongo import MongoClient
import certifi

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.s1j14s9.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

SECRET_KEY = 'NIMAUM'

import jwt

import re

import datetime

import hashlib


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)


@app.route('/register')
def register():
    msg = request.args.get("msg")
    return render_template('register.html', msg=msg)


@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/api/register', methods=['POST'])
def api_register():
    idreg = re.compile("^[0-9a-zA-Z가-힣]{2,20}$")
    pwreg = re.compile("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$")
    nickreg = re.compile("^[0-9a-zA-Z가-힣]{2,10}$")

    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']

    check_id = idreg.match(id_receive)
    check_pw = pwreg.match(pw_receive)
    check_nick = nickreg.match(nickname_receive)
    if check_id and check_pw and check_nick:
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.user.insert_one(
            {'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive, 'coffee_count': 0, 'energy_count': 0,
             'drink_count': 0, 'carbon_count': 0, 'etc_count': 0})
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg': '양식에 맞게 입력해 주세요.'})


# var reg = "^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$";
# var txt = "aaaa";
# if( !reg.test(txt) ) {
#     alert("비밀번호 정규식 규칙 위반!!");
#     return false;
# }

# 정규식 참고 링크 https://wikidocs.net/4308

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.

@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호가 일치하지 않습니다.'})


@app.route('/api/show', methods=['GET'])
def api_show():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})

    info_list = list(db.user.find({'id': userinfo['id']}, {'_id': False}).sort('coffee_count', -1))

    coffee_rank = list(db.user.find({}, {'_id': False}).sort('coffee_count', -1))

    energy_rank = list(db.user.find({}, {'_id': False}).sort('energy_count', -1))
    drink_rank = list(db.user.find({}, {'_id': False}).sort('drink_count', -1))
    carbon_rank = list(db.user.find({}, {'_id': False}).sort('carbon_count', -1))
    etc_rank = list(db.user.find({}, {'_id': False}).sort('etc_count', -1))

    # coffee energy carbon drink etc
    my_rank = [0 for i in range(5)]

    for i in range(len(coffee_rank)):
        for k, v in coffee_rank[i].items():
            if v == userinfo['id']:
                my_rank[0] = i + 1

    for i in range(len(energy_rank)):
        for k, v in energy_rank[i].items():
            if v == userinfo['id']:
                my_rank[1] = i + 1

    for i in range(len(carbon_rank)):
        for k, v in carbon_rank[i].items():
            if v == userinfo['id']:
                my_rank[2] = i + 1

    for i in range(len(drink_rank)):
        for k, v in drink_rank[i].items():
            if v == userinfo['id']:
                my_rank[3] = i + 1

    for i in range(len(etc_rank)):
        for k, v in etc_rank[i].items():
            if v == userinfo['id']:
                my_rank[4] = i + 1

    return jsonify({
        'info': info_list,
        'coffee': coffee_rank,
        'energy': energy_rank,
        'drink': drink_rank,
        'carbon': carbon_rank,
        'etc': etc_rank,
        'ranking': my_rank
    })


@app.route('/api/count', methods=['POST'])
def api_count():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})

    coffee_receive = request.form['coffee_give']
    energy_receive = request.form['energy_give']
    drink_receive = request.form['drink_give']
    carbon_receive = request.form['carbon_give']
    etc_receive = request.form['etc_give']

    db.user.update_one({'id': userinfo['id']
                        },
                       {'$set': {
                           'coffee_count': int(coffee_receive),
                           'energy_count': int(energy_receive),
                           'drink_count': int(drink_receive),
                           'carbon_count': int(carbon_receive),
                           'etc_count': int(etc_receive)
                       }})

    return jsonify({'msg': "성공"})


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
