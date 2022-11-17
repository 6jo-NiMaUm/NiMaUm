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
from operator import itemgetter


app = Flask(__name__)
# counter = 100

ca = certifi.where()

client = MongoClient('mongodb+srv://test:sparta@cluster0.s1j14s9.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)
db = client.dbsparta

# JWT 디코딩 문자열
SECRET_KEY = 'NIMAUM'
update_dt = str(int(datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]) - 3)


# 1. 기능 : 로그인 처리 페이지
# 2. 작성자 : 6조 서혁수
# 3. 작성일자 : 2022-11-14
# 4. 수정사항 :
@app.route('/')
def home():
    # 1. 클라이언트 에게서 토큰을 받기
    token_receive = request.cookies.get('mytoken')

    # 2. 토큰으로 부터 데이터 추출 및 예외처리
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])   # payload 변수에 받은 토큰을 디코딩
        user_info = db.user.find_one({"id": payload['id']})                     # user_info 에 토큰에서 가져온 아이디와 동일한 정보를 DB 에서 가져와서 담기
        return render_template('index.html', nickname=user_info["nick"])        # nickname 변수에 닉네임 정보를 담아서 index.html 으로 같이 리턴
    except Exception as e:                                                      # 모든 예외 사항을 e 변수에 담아서 처리
        print(e)                                                                # 문제 발생시 나중에 확인을 위해 e 변수를 프린트 문으로 출력
        return redirect(url_for("login"))                                       # 로그인 페이지로 강제 이동


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


# 1. 기능 : 회원가입 처리 API
# 2. 작성자 : 6조 서혁수
# 3. 작성일자 : 2022-11-14
# 4. 수정사항 :
@app.route('/api/register', methods=['POST'])
def api_register():
    # 1. 양식에 사용될 정규식을 선언
    idreg = re.compile("^[0-9a-zA-Z]{5,20}$")                                               # ID 관련 정규식 영어 대/소문자, 숫자 0~9 까지 5~20 자로 제한
    pwreg = re.compile("^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,16}$")  # PW 관련 정규식 영어 대/소문자, 숫자 0~9, 특수문자 반드시 사용 8~16자로 제한
    nickreg = re.compile("^[0-9a-zA-Z가-힣]{2,10}$")                                         # 닉네임 관련 정규식 영어 대/소문자, 한글 자음, 모음만 사용 불가능, 숫자 0~9 까지

    # 2. 클라이언트 로 부터 정보를 받기
    id_receive = request.form['id_give']                # 클라이언트 로 부터 ID 입력값 받아오기
    pw_receive = request.form['pw_give']                # 클라이언트 로 부터 PW 입력값 받아오기
    nickname_receive = request.form['nickname_give']    # 클라이언트 로 부터 닉네임 입력값 받아오기
    pwch_receive = request.form['pwch_give']            # 클라이언트 로 부터 2차 비밀번호 입력값 받아오기

    # 3. 받아온 정보를 바탕으로 정규식 검사
    check_id = idreg.match(id_receive)                  # 받아온 입력값을 정규식으로 검사
    check_pw = pwreg.match(pw_receive)
    check_nick = nickreg.match(nickname_receive)

    # 4. 로그인 시 예외 사항 관련 처리
    if id_receive == '':                                                                      # 아이디를 입력하지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '아이디를 입력해 주세요 !'})
    elif check_id is None:                                                                    # 아이디가 정규식에 맞지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '아이디 작성시 양식에 맞게 다시 입력해 주세요 !'})
    elif db.user.find_one({'id': id_receive}) is not None:                                    # DB에 입력한 아이디가 있을 경우 메시지 출력
        return jsonify({'result': 'fail', 'msg': '이미 사용중인 아이디가 있습니다 !'})
    elif nickname_receive == '':                                                              # 닉네임칸에 입력하지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '닉네임을 입력해 주세요 !'})
    elif check_nick is None:                                                                  # 닉네임이 정규식에 맞지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '닉네임 작성시 양식에 맞게 다시 입력해 주세요 !'})
    elif db.user.find_one({'nick': nickname_receive}) is not None:                            # DB에 입력한 닉네임이 있을 경우 메시지 출력
        return jsonify({'result': 'fail', 'msg': '이미 사용중인 닉네임이 있습니다 !'})
    elif pw_receive == '':                                                                    # 1차 비밀번호칸에 입력하지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '비밀번호를 입력해 주세요 !'})
    elif check_pw is None:                                                                    # 1차 비밀번호가 정규식에 맞지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '비밀번호를 양식에 맞게 입력해 주세요 !'})
    elif pwch_receive == '':                                                                  # 2차 비밀번호에 아무런 입력이 없을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '비밀번호를 한번 더 입력해 주세요 !'})
    elif pw_receive != pwch_receive:                                                          # 1차와 2차 비밀번호가 일치하지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '비밀번호가 일치하지 않습니다 !'})

    # 5. 회원가입 완료 처리 부분
    if check_id and check_pw and check_nick:                                        # 예외사항을 모두 통과시에 작동
        pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()            # 입력한 비밀번호를 암호화
        db.user.insert_one(                                                         # 입력한 값들을 모두 디비에 넣어준다.
            {'id': id_receive, 'pw': pw_hash, 'nick': nickname_receive})
        return jsonify({'result': 'success'})                                       # 결과를 result 키에 success 값을 반환
    else:
        return jsonify({'result': 'fail', 'msg': '양식에 맞게 입력해 주세요.'})         # 위의 모든 과정과 맞지 않으면 발생


# 1. 기능 : 로그인 처리 API
# 2. 작성자 : 6조 서혁수
# 3. 작성일자 : 2022-11-14
# 4. 수정사항 :
@app.route('/api/login', methods=['POST'])
def api_login():
    # 1. 클라이언트의 회원 정보 받기
    id_receive = request.form['id_give']        # 클라이언트 로 부터 ID 값 가져오기
    pw_receive = request.form['pw_give']        # 클라이언트 로 부터 PW 값 가져오기

    # 2. 받아온 비밀번호를 암호화
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # 3. 받아온 값을 필요한 처리를 거친 후 DB 에서 정보 찾기
    result = db.user.find_one({'id': id_receive, 'pw': pw_hash})

    # 4. 가입된 ID 가 존재할 경우 예외처리
    if db.user.find_one({'id': id_receive}) is not None:                                            # 입력받은 아이디가 DB 에 존재하면
        find = db.user.find_one({'id': id_receive})                                                 # find 변수에 해당 아이디의 DB 정보를 가져옴
        pwinput = find['pw']                                                                        # pwinput 변수에 비밀번호 값만 가져온다.
        if pw_receive == '':                                                                        # 비밀번호를 입력하지 않을시 메시지 출력
            return jsonify({'result': 'fail', 'msg': '비밀번호를 입력해 주세요 !'})
        elif pw_hash != pwinput:                                                                    # DB 의 비밀번호와 입력한 비밀번호가 일치하지 않으면 메시지 출력
            return jsonify({'result': 'fail', 'msg': '입력하신 아이디의 비밀번호가 일치하지 않습니다 !'})

    # 5. 입력값이 없거나 ID 가 없을 경우 예외처리
    if id_receive == '' and pw_receive == '':                                                       # ID 와 비밀번호 모두 입력하지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '아이디 또는 비밀번호를 입력해 주세요 !'})
    elif id_receive == '':                                                                          # ID 만 입력하지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '아이디를 입력해 주세요 !'})
    elif db.user.find_one({'id': id_receive}) is None:                                              # 아이디가 DB 에 존재하지 않을시 메시지 출력
        return jsonify({'result': 'fail', 'msg': '존재하지 않는 아이디 입니다 !'})

    # 6. 결과적으로 ID, PW 모두 존재하고 맞을 경우 로그인 완료
    if result is not None:                                                          # result 의 값이 None 아닐시
        payload = {                                                                 # payload 에 ID 를 담고, 파기될 시간 정보도 담는다.
            'id': id_receive,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')                  # 토큰에다가 payload 정보와 암호화 키를 담아서 sha256 방식으로 암호화 한다.
        return jsonify({'result': 'success', 'token': token})                       # 해당 토큰을 리턴
    else:
        return jsonify({'result': 'fail', 'msg': '원인을 알 수 없는 에러 입니다 !'})    # 예외 사항의 경우 메시지를 출력


# 1. 기능: 웹 페이지로 DB 데이터 전송
# 2. 작성자: 황지성
# 3. 작성일자: 2022-11-17
@app.route('/api/show', methods=['GET'])
def api_show():

    # 1. JWT 수신 및 유저 정보 확인
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo = db.user.find_one({'id': payload['id']}, {'_id': 0})          # DB로부터 접속 유저 정보 추출
    my_rank = [0 for i in range(5)]                                         # 접속 사용자의 음료별 랭킹 저장을 위한 리스트

    # 2. 날짜 데이터 생성 및 정제
    dt = datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]


    # 3. DB 데이터 추출(기간별 데이터)
    info_list = list(db.info.find({
                                    'id': userinfo['id'],
                                    'dt': {"$gte": update_dt, "$lte": str(int(update_dt) + 6)}},
                                  {'_id': False}).sort('coffee_count', -1)
                     )


    # 4. 그룹화된 DB 데이터 추출(그룹화 기준 : id, nick)
    merge_count = list(db.info.aggregate([{'$group': {'_id': {'id': '$id', 'nick': '$nick'},
                                                      'coffee_count': {'$sum': '$coffee_count'},
                                                      'energy_count': {'$sum': '$energy_count'},
                                                      'drink_count': {'$sum': '$drink_count'},
                                                      'carbon_count': {'$sum': '$carbon_count'},
                                                      'etc_count': {'$sum': '$etc_count'}
                                                      }}]))

    # 5. 추출 데이터 정렬(정렬 기준 = 음료별 마신 잔 수)
    coffee_rank = sorted(merge_count, key=itemgetter('coffee_count')    , reverse=True)
    energy_rank = sorted(merge_count, key=itemgetter('energy_count')    , reverse=True)
    drink_rank  = sorted(merge_count, key=itemgetter('drink_count')     , reverse=True)
    carbon_rank = sorted(merge_count, key=itemgetter('carbon_count')    , reverse=True)
    etc_rank    = sorted(merge_count, key=itemgetter('etc_count')       , reverse=True)


    # 6. 접속 사용자의 음료별 랭킹 계산
    for i in range(len(coffee_rank)):                   # 커피 랭킹
        userid = coffee_rank[i]['_id']['id']

        if userid == userinfo['id']:
            my_rank[0] = i + 1

    for i in range(len(energy_rank)):                   # 에너지드링크 랭킹
        userid = energy_rank[i]['_id']['id']

        if userid == userinfo['id']:
            my_rank[1] = i + 1

    for i in range(len(carbon_rank)):                   # 탄산음료 랭킹
        userid = carbon_rank[i]['_id']['id']

        if userid == userinfo['id']:
            my_rank[2] = i + 1

    for i in range(len(drink_rank)):                    # 술 랭킹
        userid = drink_rank[i]['_id']['id']

        if userid == userinfo['id']:
            my_rank[3] = i + 1

    for i in range(len(etc_rank)):                      # 기타음료 랭킹
        userid = etc_rank[i]['_id']['id']

        if userid == userinfo['id']:
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


# 1. 기능: 웹 페이지로부터 수신한 데이터 DB 적재
# 2. 작성자: 황지성
# 3. 작성일자: 2022-11-17
@app.route('/api/count', methods=['POST'])
def api_count():

    # 1. JWT 수신 및 유저 정보 확인
    token_receive = request.cookies.get('mytoken')
    payload       = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
    userinfo      = db.user.find_one({'id': payload['id']}, {'_id': 0})          # DB로부터 접속 유저 정보 추출

    # 2. 날짜 데이터 생성 및 정제
    dt = datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]


    # 3. 클라이언트 데이터 수신(ajax)
    coffee_receive   = request.form['coffee_give']
    energy_receive   = request.form['energy_give']
    drink_receive    = request.form['drink_give']
    carbon_receive   = request.form['carbon_give']
    etc_receive      = request.form['etc_give']
    nickname_receive = userinfo['nick']

    # 4. 수신 데이터  DB 적재
    if db.info.find_one({'id': payload['id'], 'dt': dt}, {'_id': 0}) == None:    # DB에 해당 유저의 오늘자 데이터가 존재하지 않으면 INSERT
        db.info.insert_one({
            'id': payload['id'],
            'nick': nickname_receive,
            'coffee_count': int(coffee_receive),
            'energy_count': int(energy_receive),
            'drink_count':  int(drink_receive),
            'carbon_count': int(carbon_receive),
            'etc_count':    int(etc_receive),
            'dt': dt
        })
    else:
        db.info.update_one({'id': userinfo['id'], 'dt': dt                      # DB에 해당 유저의 오늘자 데이터가 존재하면 UPDATE
                            },
                           {'$set': {
                               'coffee_count': int(coffee_receive),
                               'energy_count': int(energy_receive),
                               'drink_count':  int(drink_receive),
                               'carbon_count': int(carbon_receive),
                               'etc_count':    int(etc_receive),
                           }})

    return jsonify({'msg': "성공"})


# 1. 기능 : DB변화를 감지하여 변한 데이터에 대한 값을 화면에 전달 하는 함수로 SSE (Server Sent Event) 기능을 한다.
# 2. 작성자 : 6조 조소영
# 3. 작성일자 : 2022-11-15
# 4. 수정사항 : - operation 별 처리와 출력 Key값 변화에 따른 처리 적용 (2022-11-16 by.조소영)
#              - 이전 값과 변화 값의 비교 함수 (2022-11-16 by.황지성)
# 5. 수정일자 : 2022-11-17
@app.route("/listen")
def listen():

    def respond_to_client(info):

        #1. DB변화 감지 스트림 생성
        stream = db.info.watch(full_document="updateLookup", full_document_before_change="whenAvailable")                               # 몽고DB의 특정 collection을 지켜보는 함수 (full_document_before_change옵션은 변경 Key값만을 알려주는 옵션)

        #2. 스트림을 유지 및 DB변화
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

            #3.
            _data = json.dumps({                                                                                                        # 화면으로 보낼 데이터를 json 형태로 저장
                "nick": docu['fullDocument']['nick'],
                "comment": message
            })
            yield f"id: 1\ndata: {_data}\nevent: online\n\n"                                                                            # yield는 for문이 돌면서 중간중간 변경 값을 출력한 값을 하나하나 전달 하기 위한 제네레이터를 생성하는 기능을 한다
                                                                                                                                        # f""는 f-string 문자열 사이에 변수를 사용할 수 있도록 하는 문법

    # DB의 이전 값을 가져오는 함수
    def find_id(id, info, update_count, key):                                                                                           # 이전 데이터 모두를 대상으로 for문을 돌려
        for i in range(len(info)):
            if info[i]['id'] == id:                                                                                                     # 해당 아이디를 찾는다
                result = info[i][key]                                                                                                   # 이전 값을 return할 변수에 대입
                info[i][key] = update_count                                                                                             # info에 들어있는 값을 갱신
                return result, info

        return                                                                                                                          # for문 안의 return값을 함수 밖으로 그대로 return, info를 다시 return하는건 info가 갱신되어 for문 안에서 돌아야하기 때문

    info = list(db.info.find({}, {'_id': False}))                                                                                       # 이전 모든 데이터를 list형태로 저장
    return Response(respond_to_client(info), mimetype='text/event-stream')


def update_date():
    global update_dt

    update_dt = datetime.datetime.today().strftime("%Y%m%d%H%M%S")[0:8]

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

    schedule.every().monday.do(update_date())
    while True:
        schedule.run_pending()
        time.sleep(1)



if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
