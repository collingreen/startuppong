(function(){

    $(window).load(function() {

      $('[data-tooltip]').tooltip();

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

    $('#notifications_close').on('click', function () {
      apiCall({
        url: $(this).attr('data-url'),
        url_prefix: '',
        callback: function (err, res) {
          $('#notifications_button').hide();
        }
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

    if (!target) {
      if ($('#alert_container').length > 0) {
        target = $('#alert_container');
      } else {
        target = $('#alert_wrapper');
      }
    }

    alert_div.appendTo(target);
    alert_div.alert();

    if (timeout !== false) {
      setTimeout(function(){ alert_div.alert('close'); }, 3500);
    }

    return alert_div;
}

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

/**
 * apiCall
 *
 * Make an api call to the server. Prepends the
 * api version unless `prefix` is explicitly given.
 *
 * opts:
 *   - url: url to access
 *   - url_prefix (optional): explicit prefix - defaults to latest api version
 *   - data (optional): an object to send in the request
 *   - callback (optional): function to call when complete
 *     - callback is called with (err, res) where err is true if an
 *     error occurred and response is an object representing the api response
 */
function apiCall(opts) {

  var prefix = 'url_prefix' in opts ? opts.url_prefix : '/api/v1/';
  var url = prefix + opts.url;
  var cb = opts.callback;

  $.ajax(url, {
    method: "POST",
    headers: {"X-CSRFToken": window.csrf_token},
    data: opts.data || {},
    success: function(response) {
      var res = {};
      var err = null;

      // try to JSON parse the response
      try {
        res = JSON.parse(response);
      } catch (e) {
        res.error = "Invalid Response";
        res.error_code = "invalid_response";
        err = true;
      }

      cb && cb(err, res);
    },
    failure: function(response) {
      var res = {};
      // try to JSON parse the response
      try {
        res = JSON.parse(response);
      } catch (e) {
        res.error = "Invalid Response";
        res.error_code = "invalid_response";
        err = true;
      }

      cb && cb(true, res);
    }
  });
}
