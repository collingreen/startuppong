
// make delete match links open the modal
$(".delete_match").on('click', function(){
  $("#deleteMatchID").val($(this).attr("data-match-id"));

  // clone the match summary
  var summary = $(this).parent().find(".row_summary");
  $("#deleteMatchSummary").empty();
  summary.clone().appendTo($("#deleteMatchSummary"));

  $("#deleteMatchModal").modal();
});

$('#deleteMatchConfirm').on('click', function(){
  // send to server
  $("#deleteMatchConfirm").attr("disabled", true);
  var deleting_match_alert = showAlert(
    "Deleting Match. Please Wait.",
    "alert-success",
    $("#deleteMatchModal .alertContainer"),
    false
  );
  $(deleting_match_alert).attr("id", "deleting_match_alert");

  $.ajax("{% url 'ajax_delete_match' company_name=company.short_name %}", {
    method: "POST",
    headers: {"X-CSRFToken": "{{ csrf_token|safe() }}"},
    data: {
      match_id: $("#deleteMatchID").val()
    },
    success: function(response) {
      if (response.success) {
        // todo: update without reload
        window.location.reload();
      }
      else {
        $("#deleteMatchConfirm").attr("disabled", false);
        var error_message = "There was an error while deleting the match. Go yell at whomever set this up.";
        if (response.error_message) {
          error_message = response.error_message;
        }
        $("#deleting_match_alert").alert('close');
        showError(error_message, $("#deleteMatchModal .alertContainer"));
      }
    },
    failure: function(response) {
      $("#deleteMatchConfirm").attr("disabled", false);
      $("#deleting_match_alert").alert('close');
      showError("Error deleting match. Go yell at whomever set this up.", $("#deleteMatchModal .alertContainer"));
    },
    error: function(response) {
      $("#deleteMatchConfirm").attr("disabled", false);
      $("#deleting_match_alert").alert('close');
      showError("Error deleting match. Go yell at whomever set this up.", $("#deleteMatchModal .alertContainer"));
    }
  });
});
