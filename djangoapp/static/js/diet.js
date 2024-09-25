$(document).ready(function () {
    // 모든 .meals_btn에 클릭 이벤트 설정
    $('.meals_btn').on('click', function () {
        let info = $(this).next('.meal_info'); // 클릭된 버튼의 바로 다음 .meal_info 선택
        info.toggle(); // .meal_info의 보임/숨김 상태 전환
    });

    $('#add_meal').on('click', function () {
        let add_meal_form = $(this).next('.add_meal_form');
        add_meal_form.toggle();
    });

    $('.modify_meal').on('click', function () {

        var parent_li = $(this).closest("li")

        parent_li.find('.modify_meal').hide();
        parent_li.find('.delete_meal').hide();
        parent_li.find('.meal_name').hide();
        parent_li.find('.confirm_meal').show();
        parent_li.find('.modify_meal_name').show();
        parent_li.find('.modify_meal_kcal').show();
    });

    $('.confirm_meal').on('click', function () {
        $('.modify_meal').show();
        $('.delete_meal').show();
        $('.meal_name').show();
        $('.confirm_meal').hide();
        $('.modify_meal_name').hide();
        $('.modify_meal_kcal').hide();
    });
});

function deleteBoard(mealId) {
    Swal.fire({
        title: '<p style="margin: 0px; font-size: 20px;">해당 식단을 삭제하시겠습니까?</p>',
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
            fetch(`/delete/meal/${mealId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
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


// TODO: Django form????
function deleteMealName2(mealId, nutrientName) {
    Swal.fire({
        title: '<p style="margin: 0px; font-size: 20px;">해당 식품 이름을 삭제하시겠습니까?</p>',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#00BCD4',
        cancelButtonColor: '#e5e2e2',
        confirmButtonText: '삭제',
        cancelButtonText: '취소',
        width: '400px'
    }).then((result) => {
        if (result.value) {
            fetch(`/mod/${mealId}/${nutrientName}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({name: nutrientName}) // TODO: Kcal 추가
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

function modifyMealName2(mealId, nutrientName) {
    const newNutrientName = document.getElementById('toModifyNutrientName').value;
    const newKcal = document.getElementById('toModifyKcal').value;

    if (newNutrientName === '') {
        Swal.fire('수정할 식품 이름을 입력해주세요.', '', 'error');
        return;
    }

    fetch(`/mod/${mealId}/${nutrientName}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({name: newNutrientName}) // TODO: Kcal 추가
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            Swal.fire('수정되었습니다!', '', 'success').then(() => {
                location.reload();
            });
        })
        .catch(error => {
            Swal.fire('수정 실패!', '다시 시도해주세요.', 'error');
        });

    // a good looking alternative bigger alert
    // Swal.fire({
    //     title: '수정할 식품 이름을 입력해주세요.',
    //     input: 'text',
    //     inputAttributes: {
    //         autocapitalize: 'off'
    //     },
    //     showCancelButton: true,
    //     cancelButtonText: '취소',
    //     confirmButtonText: '수정',
    //     showLoaderOnConfirm: true,
    //     preConfirm: (meal_name) => {
    //         return fetch(`/mod/${mealId}/${nutrientName}/`, {
    //             method: 'PUT',
    //             headers: {
    //                 'Content-Type': 'application/json',
    //                 'X-CSRFToken': csrfToken
    //             },
    //             body: JSON.stringify({meal_name: meal_name})
    //         })
    //             .then(response => {
    //                 if (!response.ok) {
    //                     throw new Error('Network response was not ok');
    //                 }
    //                 return response.json();
    //             })
    //             .catch(error => {
    //                 Swal.showValidationMessage(
    //                     `Request failed: ${error}`
    //                 )
    //             });
    //     },
    //     allowOutsideClick: () => !Swal.isLoading()
    // }).then((result) => {
    //     if (result.value) {
    //         Swal.fire('수정되었습니다!', '', 'success').then(() => {
    //             location.reload();
    //         });
    //     }
    // });
}

function modifyMealName3(mealId, nutrientName) {
    const newNutrientName = document.getElementById('newNutrientName').value;
    const newKcal = document.getElementById('newKcal').value;

    if (newNutrientName === '') {
        Swal.fire('추가할 식품 이름을 입력해주세요.', '', 'error');
        return;
    }

    // 삭제, 수정도 아닌 추가
    fetch(`/mod/${mealId}/${nutrientName}/`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({name: newNutrientName}) // TODO: Kcal 추가
    })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            Swal.fire('추가되었습니다!', '', 'success').then(() => {
                location.reload();
            });
        })
        .catch(error => {
            Swal.fire('추가 실패!', '다시 시도해주세요.', 'error');
        });
}
