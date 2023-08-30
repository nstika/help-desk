$(document).ready(function () {
  $("#ticket_client").on("click", function (e) {
    document.getElementById("searchEngineInput").focus();
    $(this).val("");
    $("#searchModal").modal("show");
  });

  $(".users-body .list").on("click", ".item", function () {
    $("#ticket_client").val(
      $(this).attr("username") +
        " - " +
        $(this).attr("name") +
        " (" +
        $(this).attr("type") +
        ")"
    );
    $("#ticket_client").attr("username", $(this).attr("username"));
    $("#ticket_client").attr("userID", $(this).attr("userid"));
    $("#searchModal").modal("hide");
    getReport($(this).attr("userid"));
  });

  $("#searchEngineInput").on("input", function () {
    $(".users-body .list").html("");
  });

  $("#SearchBTN").click(function (e) {
    e.preventDefault();
    if ($("#searchEngineInput").val() != "") {
      SearchEngine($("#searchEngineInput").val());
    } else {
      Swal.fire("Warning", "Type your search", "warning");
    }
  });

  function SearchEngine(letter) {
    $.ajax({
      method: "GET",
      url: BASE_URL + "users/search_engine/" + letter + "/" + "AG",
      async: false,
      headers: { "X-CSRFToken": csrftoken },
      success: function (data) {
        $(".users-body .list").html("");
        data.Message.forEach((user) => {
          $(".users-body .list").append(`
              <div class="col-md-12 item" type = ${user.Type} name='${user.Name}' username=${user.Username} userid = ${user.ID}>
              <div class="row">
                  <div class="col-md-12">
                      <h5 id="userName">${user.Username} - ${user.Name} - (${user.Type})</h5>
                  </div>
                  <div class="col-md-12">
                      <p class="userEmail">${user.Email}</p>
                  </div>
                  <div class="col-md-12" style="margin-bottom:10px;">
                      <p class="userPhone">${user.Phone}</p>
                  </div>
              </div>
          </div>
            `);
        });

        if (data.Message.length == 0) {
          $(".users-body .list").html("No users matched the search...");
        }
      },
    });
  }

  function getReport(id) {
    var rows = "";
    let formData = new FormData();
    formData.append("Type", "get_ticket_report");
    formData.append("id", id);
    $.ajax({
      method: "POST",
      url: BASE_URL + "users/get_users_links",
      processData: false,
      contentType: false,
      data: formData,
      headers: { "X-CSRFToken": csrftoken },
      async: false,
      success: function (data) {
        if (!data.Message.isError) {
          if (data.Message.length != "") {
            let num = 0;

            for (let i = 0; i < data.Message.length; i++) {
              is_accepted = "";
              if(data.Message[i]["is_accepted"]){
                is_accepted="Accepted"
              }
              else{
                is_accepted="Not Accepted"
              }
              num++;
              $("#ticket_table tbody").append(`
                <tr><td>${num}</td>
                    
                    <td> ${data.Message[i]["ticket_number"]} </td>
                    <td> ${data.Message[i]["title"]} </td>
                    <td> ${data.Message[i]["priority"]} </td>
                    <td> ${is_accepted} </td>
                 
                </tr>
               `);
            }
          } else {
            $("#ticket_table").append(`
                <td colspan="4" class="btn-danger" style="font-size:20px"><center> No Data is Available </center></td>
               `);
          }
        } else {
        }
      },
      error: function (response) {},
    });
  }
});
