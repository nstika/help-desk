$(document).ready(function () {
    let action = 'insert'


    $('#upload_btn_shower').on('click', function () {
        action = 'insert'
        document.querySelector('#upload_file_form').reset();
        $('.upload_file').modal('show');
        $('#File').parent().removeClass('d-none');
    });

    let file = "";
    $("#File").on("change", function (e) {
        file = e.target.files[0];
    });

    $('#upload_file_form').on('submit', function (e) {
        e.preventDefault();

        let formData = new FormData();
        let link;

        if (action == 'insert') {
            link = BASE_URL + "project/manage_task_attachments/" + 0
        } else {
            link = BASE_URL + "project/manage_task_attachments/" + $("#fileID").val()
        }

        let title = $("#FileName").val();
        let task = $("#FileName").attr('taskID');
        formData.append("title", title);
        formData.append("task", task);
        formData.append("file", file);

        $.ajax({
            method: "POST",
            url: link,
            headers: { "X-CSRFToken": csrftoken },
            processData: false,
            contentType: false,
            data: formData,
            async: true,
            success: function (response) {
                if (!response.isError) {
                    Swal.fire({
                        title: "Successfully",
                        text: response.Message,
                        icon: "success",
                        confirmButtonClass: "btn btn-primary w-xs mt-2",
                        buttonsStyling: !1,
                        showCloseButton: !0,
                    }).then((e) => {
                        e.value && location.reload();
                    });
                } else {
                    Swal.fire({
                        title: "Something Wrong!!",
                        text: response.Message,
                        icon: "error",
                        confirmButtonClass: "btn btn-primary w-xs mt-2",
                        buttonsStyling: !1,
                        showCloseButton: !0,
                    });
                }
            },
            error: function (response) { },
        });
    })


    $('#task_files tbody').on('click', '#delete_file', function (e) {
        e.preventDefault();
        const id = $(this).attr("row_id");
        Swal.fire({
            title: "Are you sure?",
            text: "You won't be able to get it after!",
            icon: "warning",
            showCancelButton: !0,
            confirmButtonColor: "#2ab57d",
            cancelButtonColor: "#fd625e",
            confirmButtonText: "Yes, delete it!",
        }).then(e => {
            if (e.value) {
                $.ajax({
                    method: "DELETE",
                    url: BASE_URL + "project/manage_task_attachments/" + id,
                    headers: { "X-CSRFToken": csrftoken },
                    async: true,
                    success: function (response) {
                        if (!response.isError) {
                            Swal.fire({
                                title: "Success",
                                text: response.Message,
                                icon: "success",
                                confirmButtonClass: "btn btn-primary w-xs mt-2",
                                buttonsStyling: !1,
                                showCloseButton: !0,
                            }).then(e => {
                                e.value && location.reload();
                            });
                        } else {
                            Swal.fire({
                                title: "Something Wrong!!",
                                text: response.Message,
                                icon: "error",
                                confirmButtonClass: "btn btn-primary w-xs mt-2",
                                buttonsStyling: !1,
                                showCloseButton: !0,
                            });
                        }
                    },
                    error: function (response) { },
                });
            }
        });
    })

    $('#task_files tbody').on('click', '#edit_file', function (e) {
        e.preventDefault();
        const id = $(this).attr("row_id");
        $('#File').parent().addClass('d-none');
        action = 'update'
       
        $.ajax({
            method: "GET",
            url: BASE_URL + "project/manage_task_attachments/" + id,
            headers: { "X-CSRFToken": csrftoken },
            async: true,
            success: function (response) {
                if (!response.isError) {
                    $('.upload_file').modal('show');
                    response = response.Message;
                    $('#FileName').val(response.title);
                    $('#fileID').val(response.id);
                } else {
                    Swal.fire({
                        title: "Something Wrong!!",
                        text: response.Message,
                        icon: "error",
                        confirmButtonClass: "btn btn-primary w-xs mt-2",
                        buttonsStyling: !1,
                        showCloseButton: !0,
                    });
                }
            },
            error: function (response) { },
        });
    })
});