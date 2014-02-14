$(function() {
    $(document).on("deviceready", function() {
        $("#checkin-form").submit(function() {
            var url = $(this).attr("action");
            BT_printer.connect(function() {
                $.post(url, $(this).serialize(), function(data) {
                if (data.error == 0)
                    BT_printer.print(data.print_content, function() {
                        location.href = "/mobile/index?u_id=" + data.u_id;
                    }, utils.showMessageBox);
                    BT_printer.disconnect();
                else
                    utils.showMessageBox(data.errorMsg);
                }, "json");

            }, utils.showMessageBox);
            return false;
        });

        $("#take-img").click(function() {
            var opts = {
                quality : 50,
                destinationType : Camera.DestinationType.DATA_URL,
                sourceType : Camera.PictureSourceType.CAMERA,
                allowEdit : false,
                encodingType: Camera.EncodingType.PNG,
                targetWidth: 100,
                targetHeight: 100,
                saveToPhotoAlbum: false
            };
            
            navigator.camera.getPicture(onGetPictureDone, onGetPictureError, opts)
            return false;
        });

        function onGetPictureDone(img_data)
        {
            $("#car-img").val(img_data);
            $("#take-img img").attr("src", "data:image/png;base64,"+img_data);
        }

        function onGetPictureError(data)
        {
            utils.showMessageBox(data);
        }

    });
});
