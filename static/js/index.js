$(document).ready(function () {
    show();
});

function show() {
    $.ajax({
        type: 'GET',
        url: '/api/show',
        data: {},
        success: function (response) {
            let rows_info = response['info'];
            let rows_coffee = response['coffee'];
            let rows_energy = response['energy'];
            let rows_carbon = response['carbon'];
            let rows_drink = response['drink'];
            let rows_etc = response['etc'];
            let rows_myrank = response['ranking'];


            var arr_coffee = ['#coffee_1st', '#coffee_2nd', '#coffee_3rd', '#coffee_4th', '#coffee_5th'];
            var arr_energy = ['#energy_1st', '#energy_2nd', '#energy_3rd', '#energy_4th', '#energy_5th'];
            var arr_carbon = ['#carbon_1st', '#carbon_2nd', '#carbon_3rd', '#carbon_4th', '#carbon_5th'];
            var arr_drink = ['#drink_1st', '#drink_2nd', '#drink_3rd', '#drink_4th', '#drink_5th'];
            var arr_etc = ['#etc_1st', '#etc_2nd', '#etc_3rd', '#etc_4th', '#etc_5th'];


            console.log(rows_myrank);

            for (let i = 0; i < rows_info.length; i++) {

                let coffee = rows_info[i]['coffee_count'];
                let energy = rows_info[i]['energy_count'];
                let carbonic = rows_info[i]['carbon_count'];
                let drink = rows_info[i]['drink_count'];
                let etc = rows_info[i]['etc_count'];

                $('#coffee_count').text(coffee);
                $('#energy_count').text(energy);
                $('#carbonic_count').text(carbonic);
                $('#drink_count').text(drink);
                $('#etc_count').text(etc);
            }

            $('#coffee_myranking').text("나의 랭킹: " + rows_myrank[0]);
            $('#energy_myranking').text("나의 랭킹: " + rows_myrank[1]);
            $('#carbon_myranking').text("나의 랭킹: " + rows_myrank[2]);
            $('#drink_myranking').text("나의 랭킹: " + rows_myrank[3]);
            $('#etc_myranking').text("나의 랭킹: " + rows_myrank[4]);

            for (let i = 0; i < rows_coffee.length; i++) {
                $(arr_coffee[i]).text((i + 1) + '. ' + rows_coffee[i]['nick']);
            }

            for (let i = 0; i < rows_energy.length; i++) {
                $(arr_energy[i]).text((i + 1) + '. ' + rows_energy[i]['nick']);
            }

            for (let i = 0; i < rows_carbon.length; i++) {
                $(arr_carbon[i]).text((i + 1) + '. ' + rows_carbon[i]['nick']);
            }
            for (let i = 0; i < rows_drink.length; i++) {
                $(arr_drink[i]).text((i + 1) + '. ' + rows_drink[i]['nick']);
            }

            for (let i = 0; i < rows_etc.length; i++) {
                $(arr_etc[i]).text((i + 1) + '. ' + rows_etc[i]['nick']);
            }
        }
    });
}

// 로그아웃은 내가 가지고 있는 토큰만 쿠키에서 없애면 됩니다.
function logout() {
    $.removeCookie('mytoken');
    window.location.href = '/login'
}

function count(id, dir) {
    dir = dir.split('_')[0];


    if (dir == 'up') {
        cnt = parseInt($('#' + id).text()) + 1;
    } else {
        cnt = parseInt($('#' + id).text()) - 1;
    }

    if (cnt < 0) {
        cnt = 0;
    }


    $('#' + id).text(cnt);
}

function send_count() {
    let coffee = $('#coffee_count').text();
    let energy = $('#energy_count').text();
    let carbonic = $('#carbonic_count').text();
    let drink = $('#drink_count').text();
    let etc = $('#etc_count').text();

    $.ajax({
        type: 'POST',
        url: '/api/count',
        data: {coffee_give: coffee, energy_give: energy, carbon_give: carbonic, drink_give: drink, etc_give: etc},
        success: function (response) {
            show();
        }
    });
}