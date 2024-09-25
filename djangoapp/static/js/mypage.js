$(document).ready(function () {
    // 모든 .meals_btn에 클릭 이벤트 설정
    $('#for_pill_alarm').on('click', function () {
        let info = $(this).next('.pill_alarm'); // 클릭된 버튼의 바로 다음 .meal_info 선택
        info.toggle(); // .meal_info의 보임/숨김 상태 전환
    });

});

$(document).ready(function () {
    // 모든 .meals_btn에 클릭 이벤트 설정
    $('#for_hospital_alarm').on('click', function () {
        let info = $(this).next('.hospital_alarm'); // 클릭된 버튼의 바로 다음 .meal_info 선택
        info.toggle(); // .meal_info의 보임/숨김 상태 전환
    });

});
