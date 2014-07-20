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

function showAlert(message, alert_class, target) {
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

    setTimeout(function(){ alert_div.alert('close'); }, 3500);
}

