// 1. 기능 : 회원가입
// 2. 작성자 : 6조 서혁수
// 3. 작성일자 : 2022-11-14
// 4. 수정사항 :
function register() {
    $.ajax({
        type: "POST",
        url: "/api/register",
        data: {
            id_give: $('#userid').val(),
            pw_give: $('#userpw').val(),
            nickname_give: $('#usernick').val(),
            pwch_give: $('#userpwch').val()
        },
        success: function (response) {
            if (response['result'] == 'success') {
                alert('회원가입이 완료되었습니다.')          // 회원가입 메시지 출력
                window.location.href = '/login'         // 회원가입 완료시 로그인 창으로 돌아간다.
            } else {
                alert(response['msg'])                  // 회원가입 실패시 메시지 출력
            }
        }
    })
}


// 1. 기능 : 회원가입 경고문구 출력
// 2. 작성자 : 6조 서혁수
// 3. 작성일자 : 2022-11-14
// 4. 수정사항 :


// 1. 회원가입에 이용될 정규식 선언
// ID 관련 정규식 영어 대/소문자, 숫자 0~9 까지 5~20 자로 제한
// 닉네임 관련 정규식 영어 대/소문자, 한글 자음, 모음만 사용 불가능, 숫자 0~9 까지
// PW 관련 정규식 영어 대/소문자, 숫자 0~9, 특수문자 반드시 사용 8~16자로 제한
var id_reg = new RegExp('^[0-9a-zA-Z]{5,20}$')
var nick_reg = new RegExp('^[0-9a-zA-Z가-힣]{2,10}$')
var pw_reg = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,16}$/

// 2. 실시간 중복 아이디 확인 함수
function closeid() {
    // 입력값을 받아올 변수 선언
    let newValue
    $("#userid").on("propertychange change keyup paste input", function () {
        // 인풋값에 받아온 입력값을 newValue 에 담는다.
        newValue = $(this).val();
        if (newValue.match(id_reg) == null) {
            // 입력 값이 정규식에 맞지 않으면 경고문구 출력
            $('#result1').css('display', 'block')
        } else {
            // 입력 값이 정규식에 맞으면 경고문구 숨기기
            $('#result1').css('display', 'none')
        }
    });
}

// 3. 실시간 중복 닉네임 확인 함수
function closenick() {
    let newValue
    $("#usernick").on("propertychange change keyup paste input", function () {
        newValue = $(this).val();
        if (newValue.match(nick_reg) == null) {
            $('#result2').css('display', 'block')
        } else {
            $('#result2').css('display', 'none')
        }
    });
}

// 4. 실시간 1차 비밀번호 정규식 확인 함수
function closepw() {
    let newValue
    $("#userpw").on("propertychange change keyup paste input", function () {
        newValue = $(this).val();
        if (newValue.match(pw_reg) == null) {
            $('#result3').css('display', 'block')
        } else {
            $('#result3').css('display', 'none')
        }
    });
}

// 5. 실시간 1차 비밀번호 확인 함수
function closepwch() {
    // 1차 비밀번호 값 가져오기
    let newValue1 = $('#userpw').val()
    // 2차 비밀번호를 담을 새로운 변수 선언
    let newValue2
    $("#userpwch").on("propertychange change keyup paste input", function () {
        // 2차 비밀번호를
        newValue2 = $(this).val();
        // 인풋값에 받아온 입력값을 newValue2 에 담는다.
        if (newValue1 === newValue2) {
            // 1차 비밀번호와 2차 비밀번호가 일치하면 경고문구 감추기
            $('#result4').css('display', 'none')
        } else {
            // 1차 비밀번호와 2차 비밀번호가 일치하면 경고문구 출력
            $('#result4').css('display', 'block')
        }
    });
}