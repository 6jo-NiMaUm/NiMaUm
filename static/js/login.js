// 1. 기능 : 로그인 버튼 Enter 키로 작동
// 2. 작성자 : 6조 서혁수
// 3. 작성일자 : 2022-11-14
// 4. 수정사항 :
function enterkey() {
    // 1. 엔터키 입력 확인
    if (window.event.keyCode === 13) {
        // 2. 로그인 버튼 태그 클릭 발생
        document.getElementById('login-btn').click()
    }
}

// 1. 기능 : 로그인 처리 함수
// 2. 작성자 : 6조 서혁수
// 3. 작성일자 : 2022-11-14
// 4. 수정사항 :
function login() {
    $.ajax({
        type: "POST",
        url: "/api/login",
        data: {id_give: $('#floatingInput').val(), pw_give: $('#floatingPassword').val()},
        success: function (response) {
            // 1. 서버로부터 받아온 응답값을 확인
            if (response['result'] == 'success') {
                // 2. 쿠키에 mytoken 으로 토큰을 담아서 넣어주고 메시지 출력
                $.cookie('mytoken', response['token']);
                alert('로그인 완료 !')

                // 3. 메인 페이지로 주소 변경
                window.location.href = '/'
            } else {
                // 4. 응답값이 success 가 아닐 시 메시지 출력
                alert(response['msg'])
            }
        }
    })
}