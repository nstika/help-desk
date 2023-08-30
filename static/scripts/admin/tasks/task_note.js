$(document).ready(function () {
  let action = "insert";
  $("#add_note_btn").on("click", function () {
    action = "insert";
    document.querySelector("#new_task_note").reset();
    $(".add_task_note").modal("show");
  });

  $("#new_task_note").on("submit", function (e) {
    e.preventDefault();

    let formData = new FormData();
    let link;

    if (action == "insert") {
      link = BASE_URL + "project/manage_task_notes/" + 0;
    } else {
      link = BASE_URL + "project/manage_task_notes/" + $("#noteID").val();
    }

    let note = $("#project-task-description").val();
    let task = $("#project-task-description").attr("TaskIDs");
    formData.append("note", note);
    formData.append("task", task);
    Swal.fire({
      title: "Are you sure",
      text: "to Change ?",
      icon: "warning",
      showCancelButton: !0,
      confirmButtonColor: "#2ab57d",
      cancelButtonColor: "#fd625e",
      confirmButtonText: "Yes, change it!",
    }).then(function (e) {
      if (e.value) {
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
          error: function (response) {},
        });
      }
    });
  });

  $("#note_tabs_container").on("click", "#delete_note", function (e) {
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
    }).then((e) => {
      if (e.value) {
        $.ajax({
          method: "DELETE",
          url: BASE_URL + "project/manage_task_notes/" + id,
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
          error: function (response) {},
        });
      }
    });
  });

  $("#note_tabs_container").on("click", "#edit_note", function (e) {
    e.preventDefault();
    const id = $(this).attr("row_id");
    action = "update";

    $.ajax({
      method: "GET",
      url: BASE_URL + "project/manage_task_notes/" + id,
      headers: { "X-CSRFToken": csrftoken },
      async: true,
      success: function (response) {
        if (!response.isError) {
          $(".add_task_note").modal("show");
          response = response.Message;
          $("#project-task-description").val(response.note);
          $("#noteID").val(response.id);
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
      error: function (response) {},
    });
  });
});
