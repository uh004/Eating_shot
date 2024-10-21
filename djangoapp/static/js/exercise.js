function deleteBoard(id) {
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
            $.ajax({
                url: `/delete/exercise/${id}/`,
                type: 'DELETE',
                headers: {
                    'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)[1],
                },
                success: function (response) {
                    Swal.fire('삭제되었습니다!', '', 'success').then(() => {
                        location.reload();
                    });
                },
                error: function (xhr, status, error) {
                    Swal.fire('삭제 실패!', '다시 시도해주세요.', 'error');
                }
            });
        }
    });
}
