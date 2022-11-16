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
                alert('회원가입이 완료되었습니다.')
                window.location.href = '/login'
            } else {
                alert(response['msg'])
            }
        }
    })
}

let result_id = document.querySelector('#result')

/* innerHTML 는 안먹히고 text 로 하니까 먹히는걸 확인
   div 는 텍스트 바이너리가 아니라서 불가능 했던걸로 추정
   $('#result').innerHTML("확인")

   아래의 정규식에서 new 가 왜 안돼는지 관련
   정규식 참고 링크 https://hamait.tistory.com/342
                  https://java119.tistory.com/71 이 블로그의 비밀번호 정규식 적용이다 */

var id_reg = new RegExp('^[0-9a-zA-Z가-힣]{5,20}$')
var nick_reg = new RegExp('^[0-9a-zA-Z가-힣]{2,10}$')
var pw_reg = /^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,16}$/

function closeid() {
    let newValue
    $("#userid").on("propertychange change keyup paste input", function () {
        newValue = $(this).val();
        if (newValue.match(id_reg) == null) {
            // 정규식 표현에 맞는 문자열이 없다면 null
            $('#result1').css('display', 'block')

        } else {
            $('#result1').css('display', 'none')

        }
    });
}

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

function closepwch() {
    let newValue1 = $('#userpw').val()
    let newValue2
    console.log(newValue1)
    $("#userpwch").on("propertychange change keyup paste input", function () {
        newValue2 = $(this).val();
        if (newValue1 === newValue2) {
            console.log('B')
            $('#result4').css('display', 'none')
        } else {
            console.log('C')
            $('#result4').css('display', 'block')
        }
    });
}