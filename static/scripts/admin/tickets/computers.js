$(document).ready(function () {
  // Update The Entries Selection
  $("#DataNumber").val($("#DataNumber").attr("DataNumber"));

  let actionTYpe = "AddComputer";

  $("#add_computer_btn").on("click", function () {
    // Reset the form field
    // Show computer model
    // Change model's title
    $("#computerForm")[0].reset();
    $("#computerModal").modal("show");
    $("#computerTitle").text("Add Computer");
    actionTYpe = "AddComputer";
  });

  // Listen for submit event
  $("#computerForm").on("submit", function (e) {
    e.preventDefault();
    // Create form data
    let formData = new FormData();

    // Read user inputs
    formData.append("computer_tag", $("#computer_tag").val());
    formData.append("full_name", $("#full_name").val());
    formData.append("username", $("#username").val());
    formData.append("office_key", $("#office_key").val());
    formData.append("office_type", $("#office_type").val());
    formData.append("windows_key", $("#windows_key").val());
    formData.append("windows_type", $("#windows_type").val());
    formData.append("location", $("#location").val());
    formData.append("department", $("#department").val());
    formData.append(
      "bitlocker_recovery_keys",
      $("#bitlocker_recovery_keys").val()
    );

    // if the action is edit
    if (actionTYpe == "EditComputer") {
      formData.append("computer_id", $("#computer_id").val());
    }

    // Send data to server
    $.ajax({
      method: "POST",
      url: BASE_URL + "tickets/manage_computer/" + actionTYpe,
      headers: { "X-CSRFToken": csrftoken },
      processData: false,
      contentType: false,
      data: formData,
      async: false,
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
            if (e.value) {
              // hide the modal and resret the form

              $("#computerForm")[0].reset();
              $("#computerModal").modal("hide");

              RefreshPage();
            }
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
  });

  // Fetch computer of edit clicking
  $("#computerTable tbody").on("click", ".edit-computer", function () {
    let computerID = $(this).attr("computer_id");

    actionTYpe = "EditComputer";
    $("#computerTitle").text("Edit Computer");

    // Create new form data
    let formData = new FormData();

    // Read user inputs
    formData.append("computer_id", computerID);

    // Send data to server
    $.ajax({
      method: "POST",
      url: BASE_URL + "tickets/manage_computer/GetComputer",
      headers: { "X-CSRFToken": csrftoken },
      processData: false,
      contentType: false,
      data: formData,
      async: false,
      success: function (response) {
        if (!response.isError) {
          $("#computer_id").val(response.Message.id);
          $("#computer_tag").val(response.Message.computer_tag);
          $("#full_name").val(response.Message.full_name);
          $("#username").val(response.Message.username);
          $("#office_key").val(response.Message.office_key);
          $("#office_type").val(response.Message.office_type);
          $("#windows_key").val(response.Message.windows_key);
          $("#windows_type").val(response.Message.windows_type);
          $("#location").val(response.Message.location);
          $("#department").val(response.Message.department);
          $("#bitlocker_recovery_keys").val(
            response.Message.bitlocker_recovery_keys
          );

          $("#computerModal").modal("show");
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

  $("#DataNumber").change(function () {
    RefreshPage();
  });

  $("#SearchQuery").on("change", function () {
    RefreshPage();
  });

  $("#SearchQueryBTN").on("click", function () {
    RefreshPage();
  });

  $(".pagination .page-item").on("click", function () {
    const pageNumber = $(this).attr("page");
    $(".activePage").attr("activePage", pageNumber);
    RefreshPage();
  });

  function RefreshPage() {
    let page = $(".activePage").attr("activePage");
    let search = $("#SearchQuery").val();
    let entries = $("#DataNumber").val();

    if (search == "") {
      window.location.replace(
        BASE_URL + `tickets/computers?DataNumber=${entries}&page=${page}`
      );
    } else {
      window.location.replace(
        BASE_URL +
          `tickets/computers?DataNumber=${entries}&SearchQuery=${search}&page=${page}`
      );
    }
  }
});
