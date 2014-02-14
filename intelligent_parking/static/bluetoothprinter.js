var BT_printer = (function() {
    ret = {
        print : function(string, onSuccess, onError)
        {
            setTimeout(function() {
                cordova.exec(onSuccess, onError, "BluetoothPrinter", "print", [string||""]);
            }, 1);
        },
        getPairedDevices : function(onSuccess, onError)
        {
            cordova.exec(onSuccess, onError, "BluetoothPrinter", "getPairedDevices", [""]);
        },
        open : function(mac, onSuccess, onError)
        {
            setTimeout(function() {
                cordova.exec(onSuccess, onError, "BluetoothPrinter", "open", [mac]);
            }, 1);
        },
        close : function(onSuccess, onError)
        {
            setTimeout(function() {
                cordova.exec(onSuccess, onError, "BluetoothPrinter", "close", [""]);
            }, 1);
        }
    }

    cordova.addConstructor(function() {
        cordova.exec(function(){}, function(){}, "BluetoothPrinter", "init", [""]);
    });

    return ret;
})();
