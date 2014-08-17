(function(){

    $(window).load(function() {
      $("input.atLeast3").each(function(i, el) {
          el = $(el);

          // add success icon
          var success_icon = $("<span/>")
            .addClass("glyphicon glyphicon-ok form-control-feedback success-only");
          success_icon.appendTo(el);

          el.on("change", function(){

              var valid = $(this).val().length >= 3;
              var target = $(this).parents(".form-group");
              var form = $(this).parents("form");

              // reset any validation classes
              target
                .removeClass("has-failure")
                .removeClass("has-warning")
                .removeClass("has-success");

              // add success or error
              target.addClass(valid ? "has-success" : "has-error");

              // update form
              form.attr("data-form-valid", valid);

              // if not valid, update form
              if (!valid) {
                form.attr(
                    "data-form-error", $(this).attr("data-validation-error"));
              }
          });
      });
    });

})();


function showError(message, target) {
    showAlert(message, 'alert-danger', target);
}

function showSuccess(message) {
    showAlert(message, 'alert-success');
}

function showAlert(message, alert_class, target, timeout) {
    var alert_div = $('<div/>').addClass('alert '+alert_class).text(message);
    alert_div.append(
      $('<button/>')
        .addClass('close fade in')
        .attr({
          'data-dismiss': 'alert',
          'aria-hidden': 'true'
        })
        .html("&times;")
    );
    alert_div.appendTo(target || $('#alert_container'));
    alert_div.alert();

    if (timeout !== false) {
      setTimeout(function(){ alert_div.alert('close'); }, 3500);
    }

    return alert_div;
}

function pollForUpdates(pollForUpdatesDelay, company_latest_change, check_for_updates_url) {
    // clear the current timeout
    if (window.idle_timeout) {
      clearInterval(window.idle_timeout);
    };

    // create new timeout
    window.idle_timeout = setInterval(
      function(){
        reloadIfUpdated(check_for_updates_url, company_latest_change)
      }, pollForUpdatesDelay
    );
};

function reloadIfUpdated(check_for_updates_url, company_latest_change) {
  checkForCompanyUpdate(check_for_updates_url, function(latest_change) {
    if (latest_change !== company_latest_change) {
      window.location.reload();
    }
  });
};

function checkForCompanyUpdate(check_for_updates_url, cb) {
  // query for latest change
  $.ajax(check_for_updates_url, {
    method: "POST",
    headers: {"X-CSRFToken": window.csrf_token},
    success: function(response) {
      if (response.latest_change) {
        cb && cb(response.latest_change);
      }
    }
  });
}
