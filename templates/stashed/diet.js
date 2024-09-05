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