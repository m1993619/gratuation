$(function() {
    $(document).on("deviceready", function() {
        navigator.splashscreen.hide();
        document.addEventListener("backbutton", onBackKeyDown, false); //返回键
    });

    $(document).on("mobileinit", function() {
        $.mobile.defaultPageTransition = $.mobile.defaultDialogTransition = "none";
        $.mobile.pageLoadErrorMessage = "网络异常!";
        //window.device_os = '{{ os }}';
    });
});
 
function onConfirm(button) {
    if(button==1) navigator.app.exitApp(); //选择了确定才执行退出
}

function onBackKeyDown() {
    if($.mobile.activePage.is("#login-page") || $.mobile.activePage.is('#main-page') || $.mobile.activePage.is("#queryparkingrecord-checkfilter-page")){
          navigator.notification.confirm(
            '按确定退出程序!',  // message
            onConfirm,              // callback to invoke with index of button pressed
            '确定要退出程序吗?',            // title
            '确定,取消'          // buttonLabels
        );
    }
    else {
        navigator.app.backHistory();
    }
}


