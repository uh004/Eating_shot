// 버튼 누를 때마다 html 불러오기

$(document).ready(function() {
    let now = 1;  // 현재 위치
    const arr = ['','food', 'exercise', 'indicator','report','mypage'];

    $(`#menu${now}`).css('background-color', '#00BCD4');
    $('#insert').load('diet.html #food');

    
    // 다른 메뉴를 클릭했을 때 now 값을 업데이트하고 배경색 변경
    $('ul li').on('click', function() {

        $(`#menu${now}`).css('background-color', ''); // 이전 메뉴의 배경색 초기화
        
        now = $(this).attr('id').replace('menu', ''); // 나중에 클릭된 거 

        $(`#menu${now}`).css('background-color', '#00BCD4');
        if (now == 1) {
            $('#insert').load('diet.html #food');
        } else if (now == 2) {
            $('#insert').load('exercise.html #exercise');
        } else if (now == 3) {
            $('#insert').load('blood.html #indicator');
        } else if (now == 4) {
            $('#insert').load('report.html');
        } else if (now == 5) {
            $('#insert').load('mypage.html #mypage');
        }
        
    });

});

function openPopup() {
    window.location.href = 'diet_form.html'
}

// 식단 버튼마다 상세 정보나오게 하는 함수

$(document).ready(function() {
    let now = 0;

    $('.meals_btn').on('click', function() {
        now++;
        if (now % 2 == 1) {
            var info = document.getElementById('meal_info')
            info.style.display = "block";
        }

        else {
            var info = document.getElementById('meal_info')
            info.style.display = "none";
        }
    });
});


// 이미지 입력 폼에 이미지 미리보기 하는 함수

document.getElementById('chooseFile').addEventListener('change', function(event) {
    var input = event.target;
    var label = document.querySelector('.file-label');
    var imgPreview = document.getElementById('image_preview');

    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function(e) {
            imgPreview.src = e.target.result;
            imgPreview.style.display = 'block';
            label.style.display = 'none';
        };

        reader.readAsDataURL(input.files[0]);
    }
});

function openPopup2() {
    window.location.href = 'exercise_list.html'
}

function openPopup3() {
    var popup = document.getElementById("popup3");
    popup.style.visibility = "visible";
    popup.style.opacity = "1";
}

function Blood1(){
    window.location.href = "blood_form1.html"
}

function Blood2(){
    window.location.href = "blood_form2.html"
}

function Blood3(){
    window.location.href = "blood_form3.html"
}