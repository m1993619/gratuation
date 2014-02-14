$(function() {
    $(document).on("deviceready", function() {
        $("#checkout-form").submit(function() {
            var url = $(this).attr("action");
            $.post(url, $(this).serialize(), function(data) {
                if (data.error == 0) {
                    BT_printer.print(data.print_content, function() {
                        location.href="/mobile/index?u_id=" + data.u_id;
                    }, utils.showMessageBox);
                } else
                    utils.showMessageBox(data.errorMsg);
            }, "json");
            return false;
        });
    });
});
