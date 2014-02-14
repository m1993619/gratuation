$(function() {
    $("#login-form").submit(function() {
        var url = $(this).attr("action");
        $.post(url, $(this).serialize(), function(data) {
            if (data.error == 0) {
                navigator.app.loadUrl("http://" + location.host + "/mobile/index?u_id=" + data.u_id);
            } else {
                utils.showMessageBox(data.errorMsg);
            }
        }, "json");
        return false;
    });
});
