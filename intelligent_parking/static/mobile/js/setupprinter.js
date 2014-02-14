$(function() {
    $(document).on("deviceready", function() {
        BT_printer.getPairedDevices(function(data) {
            var item = $("#bt-list #template").hide();
            var ul = $("#bt-list");
            $.each(data, function(idx, d) {
                var new_item = item.clone();
                ul.append(new_item);
                new_item.show();
                $("#bt-name", new_item).html(d.device_name);
                $("#bt-mac", new_item).html(d.mac_address);

                $("a", new_item).click(function() {
                    BT_printer.selectPrinter(d.mac_address, function(d) {
                        utils.showMessageBox(d);
                    }, function(error) {
                        utils.showMessageBox(error);
                    });

                    return false;
                });
            });
            
            console.log(ul.html());
        }, function(error) {
            utils.showMessageBox(error);
        });
    });
});
