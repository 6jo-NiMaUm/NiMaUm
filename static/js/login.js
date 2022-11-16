function enterkey() {
    if (window.event.keyCode == 13) {
        document.getElementById('login-btn').click()
    }
}

// onkeyup 어떤 키를 누르더라도 입력시 발생하는 함수 엔터키가 13번
// https://blog.miyam.net/139
// https://stackoverflow.com/questions/40772691/trigger-button-click-in-javascript


function login() {
    $.ajax({
        type: "POST",
        url: "/api/login",
        data: {id_give: $('#floatingInput').val(), pw_give: $('#floatingPassword').val()},
        success: function (response) {
            let keyCode = window.event.keyCode

            if (response['result'] == 'success') {
                $.cookie('mytoken', response['token']);

                alert('로그인 완료 !')
                window.location.href = '/'
            } else {
                alert(response['msg'])
            }
        }
    })
}