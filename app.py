import time
import schedule as schedule
from gevent import monkey                                                                                                           # gevent는 동시성과 네트워크 관련 작업들을 위한 다양한 API를 제공
monkey.patch_all()                                                                                                                  # 몽키 패치는 실행중인 프로그램의 메모리 소스를 바꾸는 것으로서, 런타임 환경에서 프로그램의 특정 기능을 수정하여 사용하는 기법
from flask import Flask, Response, render_template, stream_with_context, request, jsonify, redirect, url_for
# from 모듈 이름.. import 뒤는 함수 이므로 뒤에 것들은 설치 할 필요가 없다.
from pymongo import MongoClient
import certifi
import datetime
import json
import jwt
import re
import hashlib


app = Flask(__name__)
# counter = 100

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.s1j14s9.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

SECRET_KEY = 'NIMAUM'
update_dt = str(int(datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]) - 3)



@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.user.find_one({"id": payload['id']})
        return render_template('index.html', nickname=user_info["nick"])
    except Exception as e:
        print(e)
        return redirect(url_for("login"))


# 위의 처리 방법이 통상적인 처리 방법이다.
# 아래의 방법으로 처리 하면 아래의 경우로 처리된 예외 말고는 알 수가 없기 때문에
# 위 방식대로 하면 모든 경우에 대해서 예외처리가 가능하다. 그리고 나중에 원인을 알아보기 위해서
# 프린트문으로 출력하게 해준다.
# except jwt.ExpiredSignatureError:
#     # 로그인 시간이 만료 되었을 때 작동하는 부분
#     return redirect(url_for("login"))
# except jwt.exceptions.DecodeError:
#     # 로그인 정보가 존재하지 않습니다.
#     return redirect(url_for("login"))


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
    idreg = re.compile("^[0-9a-zA-Z가-힣]{5,20}$")
    pwreg = re.compile("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,16}$")
    nickreg = re.compile("^[0-9a-zA-Z가-힣]{2,10}$")

    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']
    pwch_receive = request.form['pwch_give']

    check_id = idreg.match(id_receive)
    check_pw = pwreg.match(pw_receive)
    check_nick = nickreg.match(nickname_receive)

    if id_receive == '':
        return jsonify({'result': 'fail', 'msg': '아이디를 입력해 주세요 !'})
    elif check_id is None:
        return jsonify({'result': 'fail', 'msg': '아이디 작성시 양식에 맞게 다시 입력해 주세요 !'})
    elif db.user.find_one({'id': id_receive}) is not None:
        find = db.user.find_one({'id': id_receive})
        idinput = find['id']
        if id_receive == idinput:
            return jsonify({'result': 'fail', 'msg': '이미 사용중인 아이디가 있습니다 !'})
    elif nickname_receive == '':
        return jsonify({'result': 'fail', 'msg': '닉네임을 입력해 주세요 !'})
    elif check_nick is None:
        return jsonify({'result': 'fail', 'msg': '닉네임 작성시 양식에 맞게 다시 입력해 주세요 !'})
    elif db.user.find_one({'nick': nickname_receive}) is not None:
        find = db.user.find_one({'nick': nickname_receive})
        nickinput = find['nick']
        if nickname_receive == nickinput:
            return jsonify({'result': 'fail', 'msg': '이미 사용중인 닉네임이 있습니다 !'})
    elif pw_receive == '':
        return jsonify({'result': 'fail', 'msg': '비밀번호를 입력해 주세요 !'})
    elif check_pw is None:
        return jsonify({'result': 'fail', 'msg': '비밀번호를 양식에 맞게 입력해 주세요 !'})
    elif pwch_receive == '':
        return jsonify({'result': 'fail', 'msg': '비밀번호를 한번 더 입력해 주세요 !'})
    elif pw_receive != pwch_receive:
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다 !'})

    if check_id and check_pw and check_nick:
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
        db.user.insert_one(
            {'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})  ### 추가 1. insert 내용 변경
        return jsonify({'result': 'success'})
    else:
        return jsonify({'result': 'fail', 'msg': '양식에 맞게 입력해 주세요.'})


# 정규식 참고 링크 https://wikidocs.net/4308

# [로그인 API]
# id, pw를 받아서 맞춰보고, 토큰을 만들어 발급합니다.

@app.route('/api/login', methods=['POST'])
def api_login():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    if db.user.find_one({'id': id_receive}) is not None:
        find = db.user.find_one({'id': id_receive})
        pwinput = find['pw']
        if pw_receive == '':
            return jsonify({'result': 'fail', 'msg': '비밀번호를 입력해 주세요 !'})
        elif pw_hash != pwinput:
            return jsonify({'result': 'fail', 'msg': '입력하신 아이디의 비밀번호가 일치하지 않습니다 !'})

    if id_receive == '' and pw_receive == '':
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호를 입력해 주세요 !'})
    elif id_receive == '':
        return jsonify({'result': 'fail', 'msg': '아이디를 입력해 주세요 !'})
    elif db.user.find_one({'id': id_receive}) is None:
        return jsonify({'result': 'fail', 'msg': '존재하지 않는 아이디 입니다 !'})

    if result is not None:
        payload = {
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
    else:
        return jsonify({'result': 'fail', 'msg': '원인을 알 수 없는 에러 입니다 !'})


#     return jsonify({'result': 'fail', 'msg': '아이디와 비밀번호를 입력해 주세요 !'})


@app.route('/api/show', methods=['GET'])
def api_show():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})

    dt = datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]

    info_list = list(db.info.find({'id': userinfo['id'], 'dt': {"$gte":update_dt, "$lte": str(int(update_dt) + 6)}}, {'_id': False}).sort('coffee_count', -1))
    coffee_rank = list(db.info.find({'dt': {"$gte":update_dt, "$lte": str(int(update_dt) + 6)}}, {'_id': False}, ).sort('coffee_count', -1))
    energy_rank = list(db.info.find({'dt': {"$gte":update_dt, "$lte": str(int(update_dt) + 6)}}, {'_id': False}).sort('energy_count', -1))
    drink_rank = list(db.info.find({'dt': {"$gte":update_dt, "$lte": str(int(update_dt) + 6)}}, {'_id': False}).sort('drink_count', -1))
    carbon_rank = list(db.info.find({'dt': {"$gte":update_dt, "$lte": str(int(update_dt) + 6)}}, {'_id': False}).sort('carbon_count', -1))
    etc_rank = list(db.info.find({'dt': {"$gte":update_dt, "$lte": str(int(update_dt) + 6)}}, {'_id': False}).sort('etc_count', -1))

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
    dt = datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]
    userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})

    nickname_receive = userinfo['nick']
    coffee_receive = request.form['coffee_give']
    energy_receive = request.form['energy_give']
    drink_receive = request.form['drink_give']
    carbon_receive = request.form['carbon_give']
    etc_receive = request.form['etc_give']

    if db.info.find_one({'id': payload['id'], 'dt': dt}, {'_id': 0}) == None:
        db.info.insert_one({
            'id': payload['id'],
            'nick': nickname_receive,
            'coffee_count': int(coffee_receive),
            'energy_count': int(energy_receive),
            'drink_count': int(drink_receive),
            'carbon_count': int(carbon_receive),
            'etc_count': int(etc_receive),
            'dt': dt
        })
    else:
        db.info.update_one({'id': userinfo['id'], 'dt': dt
                            },
                           {'$set': {
                               'coffee_count': int(coffee_receive),
                               'energy_count': int(energy_receive),
                               'drink_count': int(drink_receive),
                               'carbon_count': int(carbon_receive),
                               'etc_count': int(etc_receive),
                           }})

    return jsonify({'msg': "성공"})


# DB변화를 감지하여 변한 데이터에 대한 값을 화면에 전달 하는 함수로 SSE (Server Sent Event) 기능을 한다.
@app.route("/listen")
def listen():
    def respond_to_client(info):
        stream = db.info.watch(full_document="updateLookup", full_document_before_change="whenAvailable")                               # 몽고DB의 특정 collection을 지켜보는 함수 (full_document_before_change옵션은 변경 Key값만을 알려주는 옵션)

        for docu in stream:                                                                                                             # Stream을 유지하며 DB의 변경을 감지하기 위해 계속 도는 for문
            message = "";                                                                                                               # 화면단에서 출력할 메세지를 담는 변수
            if docu['operationType'] == 'update':                                                                                       # 기존값 업데이트와 첫 값 입력시 처리를 나눔
                docu_updates = docu['updateDescription']['updatedFields']                                                               # operation이 update일때는 update된 Key값과 value값만 출력되므로 key값을 확인해 처리
                for Key in docu_updates:
                    if Key == 'coffee_count':                                                                                           # if문
                        count, info = find_id(docu['fullDocument']['id'],info, docu_updates[Key], Key)                                  # 이전 데이터 값과 바뀐 데이터 값을 가져오기 위해 만든 find_id 함수 콜
                        now = docu_updates[Key] - count                                                                                 # 비교값 계산
                        if docu_updates[Key] - count < 0 :                                                                              # 잔 수를 줄였을 때의 처리와 잔 수를 늘렸을 때의 처리
                            message += "커피 " + str(-now) + "잔을 쏟아서 총 " + str(docu_updates['coffee_count']) + "잔\n"
                        else:
                            message += "커피 " + str(now) + "잔 추가해 총 " + str(docu_updates['coffee_count']) + "잔\n"
                    elif Key == 'energy_count':
                        count, info = find_id(docu['fullDocument']['id'], info, docu_updates[Key], Key)
                        now = docu_updates[Key] - count
                        if docu_updates[Key] - count < 0:
                            message += "에너지 드링크 " + str(-now) + "잔을 쏟아서 총 " + str(docu_updates['energy_count']) + "잔\n"
                        else:
                            message += "에너지 드링크 " + str(now) + "잔 추가해 총 " + str(docu_updates['energy_count']) + "잔\n"
                    elif Key == 'carbon_count':
                        count, info = find_id(docu['fullDocument']['id'], info, docu_updates[Key], Key)
                        now = docu_updates[Key] - count
                        if docu_updates[Key] - count < 0:
                            message += "탄산음료 " + str(-now) + "잔을 쏟아서 총 " + str(docu_updates['carbon_count']) + "잔\n"
                        else:
                            message += "탄산음료 " + str(now) + "잔 추가해 총 " + str(docu_updates['carbon_count']) + "잔\n"
                    elif Key == 'drink_count':
                        count, info = find_id(docu['fullDocument']['id'], info, docu_updates[Key], Key)
                        now = docu_updates[Key] - count
                        if docu_updates[Key] - count < 0:
                            message += "술 " + str(-now) + "잔을 쏟아서 총 " + str(docu_updates['drink_count']) + "잔\n"
                        else:
                            message += "술 " + str(now) + "잔 추가해 총 " + str(docu_updates['drink_count']) + "잔\n"
                    elif Key == 'etc_count':
                        count, info = find_id(docu['fullDocument']['id'], info, docu_updates[Key], Key)
                        now = docu_updates[Key] - count
                        if docu_updates[Key] - count < 0:
                            message += "기타음료 " + str(-now) + "잔을 쏟아서 총 " + str(docu_updates['etc_count']) + "잔\n"
                        else:
                            message += "기타음료 " + str(now) + "잔 추가해 총 " + str(docu_updates['etc_count']) + "잔\n"

            elif docu['operationType'] == "insert":
                docu_insert = docu['fullDocument']
                for Key in docu_insert:
                    if Key == 'coffee_count' and docu_insert['coffee_count'] != 0:
                        message += "커피 " + str(docu_insert['coffee_count']) + "잔 추가해 총 " + str(
                            docu_insert['coffee_count']) + "잔\n"
                    elif Key == 'energy_count' and docu_insert['energy_count'] != 0:
                        message += "에너지 드링크 " + str(docu_insert['energy_count']) + "잔 추가해 총 " + str(
                            docu_insert['energy_count']) + "잔\n"
                    elif Key == 'carbon_count' and docu_insert['carbon_count'] != 0:
                        message += "탄산음료 " + str(docu_insert['carbon_count']) + "잔 추가해 총 " + str(
                            docu_insert['carbon_count']) + "잔\n"
                    elif Key == 'drink_count' and docu_insert['drink_count'] != 0:
                        message += "술 " + str(docu_insert['drink_count']) + "잔 추가해 총 " + str(
                            docu_insert['drink_count']) + "잔\n"
                    elif Key == 'etc_count' and docu_insert['etc_count'] != 0:
                        message += "기타음료 " + str(docu_insert['etc_count']) + "잔 추가해 총 " + str(
                            docu_insert['etc_count']) + "잔\n"


            _data = json.dumps({                                                                                                        # 화면으로 보낼 데이터를 json 형태로 저장
                "nick": docu['fullDocument']['nick'],
                "comment": message
            })
            yield f"id: 1\ndata: {_data}\nevent: online\n\n"                                                                            # yield는 for문이 돌면서 중간중간 변경 값을 출력한 값을 하나하나 전달 하기 위한 제네레이터를 생성하는 기능을 한다
                                                                                                                                        # f""는 f-string 문자열 사이에 변수를 사용할 수 있도록 하는 문법

    # DB의 이전값을 가져오는 함수
    def find_id(id, info, update_count, key):                                                                                           # 이전 데이터 모두를 대상으로 for문을 돌려
        for i in range(len(info)):
            if info[i]['id'] == id:                                                                                                     # 해당 아이디를 찾는다
                result = info[i][key]                                                                                                   # 이전 값을 return할 변수에 대입
                info[i][key] = update_count                                                                                             # info에 들어있는 값을 갱신

                return result, info

        return                                                                                                                          # for문 안의 return값을 함수 밖으로 그대로 return, info를 다시 return하는건 info가 갱신되어 for문 안에서 돌아야하기 때문

    info = list(db.info.find({}, {'_id': False}))                                                                                       # 이전 모든 데이터를 list형태로 저장
    return Response(respond_to_client(info), mimetype='text/event-stream')                                                              # 이전 모든 데이틀 담은 info를 가지고 respond_to_clinet를 실행



def update_date():
    global update_dt

    update_dt = datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

    schedule.every().monday.do(update_date())
    while True:
        schedule.run_pending()
        time.sleep(1)

