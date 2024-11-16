function deleteBoard(num, id) {
    Swal.fire({
        title: '<p style="margin: 0; font-size: 20px;">해당 항목을 삭제하시겠습니까?</p>',
        text: "삭제하시면 다시 복구시킬 수 없습니다.",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#00BCD4',
        cancelButtonColor: '#e5e2e2',
        confirmButtonText: '삭제',
        cancelButtonText: '취소',
        width: '400px'
    }).then((result) => {
        if (result.value) {
            fetch(`/delete/blood${num}/${id}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrf-token]').content
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    Swal.fire('삭제되었습니다!', '', 'success').then(() => {
                        location.reload();
                    });
                })
                .catch(error => {
                    Swal.fire('삭제 실패!', '다시 시도해주세요.', 'error');
                });
        }
    });
}

function showPopup(e) {
    e.stopPropagation(); // Prevent the event from bubbling up the DOM tree
    const popup = document.getElementById("popup3");
    if (popup) {
        popup.style.visibility = "visible";
        popup.style.opacity = "1";
    } else {
        console.error('Element with ID "popup3" not found.');
    }
}

function hidePopup(e) {
    const popup = document.getElementById("popup3");
    if (popup) {
        const popupContent = document.querySelector(".popup-content3");
        if (popup.style.visibility === "visible" && !popupContent.contains(e.target)) {
            popup.style.visibility = "hidden";
            popup.style.opacity = "0";
        }
    } else {
        console.error('Element with ID "popup3" not found.');
    }
}

document.getElementById("target_popup_button").addEventListener('click', showPopup);
document.getElementById("blood").addEventListener('click', hidePopup);

$(document).ready(function () {
    // 모든 .meals_btn에 클릭 이벤트 설정
    $('.blood_btn').on('click', function () {
        let info = $(this).next('.for_indicator'); // 클릭된 버튼의 바로 다음 .meal_info 선택
        info.toggle(); // .meal_info의 보임/숨김 상태 전환
    });
});
