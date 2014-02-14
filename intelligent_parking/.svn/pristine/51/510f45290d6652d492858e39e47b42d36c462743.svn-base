$(document).on("pagebeforechange", function(e, data) {
    if (typeof(data.toPage) === "string") {
        //console.log(data);
        var active_index = $.mobile.urlHistory.activeIndex;
        var his_index = ($.mobile.urlHistory.find(data.toPage));
        if ((his_index != undefined) && (his_index != active_index)) {
            history.go(his_index - $.mobile.urlHistory.activeIndex);
            e.preventDefault();
        }
    }
});


(function($) {

    var datePicker;
    /**
     * Phonegap DatePicker Plugin Copyright (c) Greg Allen 2011 MIT Licensed
     * Reused and ported to Android plugin by Daniel van 't Oever
     */
    if (typeof cordova !== "undefined") {
	/**
	 * Constructor
	 */
	function DatePicker() {
	    this._callback;
	}

	/**
	 * show - true to show the ad, false to hide the ad
	 */
	DatePicker.prototype.show = function(options, cb) {
	    if (options.date) {
		options.date = (options.date.getMonth() + 1) + "/" + (options.date.getDate()) + "/" + (options.date.getFullYear()) + "/"
		    + (options.date.getHours()) + "/" + (options.date.getMinutes());
	    }
	    var defaults = {
		mode : '',
		date : '',
		allowOldDates : true
	    };

	    for ( var key in defaults) {
		if (typeof options[key] !== "undefined")
		    defaults[key] = options[key];
	    }
	    this._callback = cb;

	    return cordova.exec(cb, failureCallback, 'DatePickerPlugin', defaults.mode, new Array(defaults));
	};

	DatePicker.prototype._dateSelected = function(date) {
	    var d = new Date(parseFloat(date) * 1000);
	    if (this._callback)
		this._callback(d);
	};

	function failureCallback(err) {
	    console.log("datePickerPlugin.js failed: " + err);
	}

	cordova.addConstructor(function() {
	    //if (!window.plugins) {
	    //    window.plugins = {};
	    //}
	    //window.plugins.datePicker = new DatePicker();
            datePicker = new DatePicker();
	});
    };

    
    /**
     * jquery android 原生 datetimepicker 插件
     * @param {
     *           mode: date或者time, 空字符串为datetime, 默认为datetime
     *           format: 格式化字符串, 默认为yyyy-mm-dd 详见 http://blog.stevenlevithan.com/archives/date-time-format
     *           cb: 完成时的回调函数
     *        } 
     */

    $.fn.DatePicker = function(opts, cb) {
        //IOS系统不需要这个插件
        if (window.device_os == "ios")
            return;
        var currentField = $(this);
        if (typeof(opts) == "function") {
            cb = opts;
            opts = {};
        }
        
        currentField.attr("readonly", "readonly").focus(function() {
            datePicker.show({
                date : new Date(),
                mode : opts.mode || "",
            }, function(returnDate) {
                var newDate = new Date(returnDate),
                    format = opts.format || "yyyy-mm-dd",
                    cb = cb || $.noop;
                
                currentField.val(dateFormat(newDate, format));
                currentField.blur();
                setTimeout(cb, 0);
            });

            currentField.blur();
        });
    };
})(jQuery);


/**
 * cordova Web Intent plugin
 * Copyright (c) Boris Smus 2010
 *
 */
 (function(cordova){
    var WebIntent = function() {

    };

    WebIntent.prototype.ACTION_SEND = "android.intent.action.SEND";
    WebIntent.prototype.ACTION_VIEW= "android.intent.action.VIEW";
    WebIntent.prototype.EXTRA_TEXT = "android.intent.extra.TEXT";
    WebIntent.prototype.EXTRA_SUBJECT = "android.intent.extra.SUBJECT";
    WebIntent.prototype.EXTRA_STREAM = "android.intent.extra.STREAM";
    WebIntent.prototype.EXTRA_EMAIL = "android.intent.extra.EMAIL";

    WebIntent.prototype.startActivity = function(params, success, fail) {
        return cordova.exec(function(args) {
            success(args);
        }, function(args) {
            fail(args);
        }, 'WebIntent', 'startActivity', [params]);
    };

    WebIntent.prototype.hasExtra = function(params, success, fail) {
        return cordova.exec(function(args) {
            success(args);
        }, function(args) {
            fail(args);
        }, 'WebIntent', 'hasExtra', [params]);
    };

    WebIntent.prototype.getUri = function(success, fail) {
        return cordova.exec(function(args) {
            success(args);
        }, function(args) {
            fail(args);
        }, 'WebIntent', 'getUri', []);
    };

    WebIntent.prototype.getExtra = function(params, success, fail) {
        return cordova.exec(function(args) {
            success(args);
        }, function(args) {
            fail(args);
        }, 'WebIntent', 'getExtra', [params]);
    };


    WebIntent.prototype.onNewIntent = function(callback) {
        return cordova.exec(function(args) {
            callback(args);
        }, function(args) {
        }, 'WebIntent', 'onNewIntent', []);
    };

    WebIntent.prototype.sendBroadcast = function(params, success, fail) {
        return cordova.exec(function(args) {
            success(args);
        }, function(args) {
            fail(args);
        }, 'WebIntent', 'sendBroadcast', [params]);
    };

    cordova.addConstructor(function() {
        window.webintent = new WebIntent();
        
        // backwards compatibility
        window.plugins = window.plugins || {};
        window.plugins.webintent = window.webintent;
    });
})(window.PhoneGap || window.Cordova || window.cordova);


function startKDActivity(data)
{
    window.plugins.webintent.startActivity({
        package: "com.yntel.padcrm",
        extras : data
    }, function(){}, function(e) {
        utils.showMessageBox("移动受理客户端没有安装!");
        //window.requestFileSystem(LocalFileSystem.PERSISTENT, 0, onRequestFileSystemComplete, onRequestFileSystemFailt);
    });

    function onDownloadFail()
    {
        
    }

    function onDownladComplete(entry)
    {
        var activityOpts = {
            action: window.plugins.webintent.ACTION_VIEW,
            url: entry.fullPath,
            type: 'application/vnd.android.package-archive'
        };

        window.plugins.webintent.startActivity(activityOpts, onStartActivityComplete, onStartActivityFailt);
    }

    function onDownloading()
    {
        console.log("download.....");
    }

    function onStartActivityComplete()
    {

    }

    function onStartActivityFailt()
    {
        
    }

    function onGetFileFailt()
    {
        
    }

    function onGetFileComplete(fileEntry)
    {
        var localPath = fileEntry.fullPath,
        fileTransfer = new FileTransfer();
        fileTransfer.onprogress = onDownloading;        
        fileTransfer.download("http://192.168.1.101:8001/bin/cordovaExample-debug.apk", localPath, onDownladComplete, onDownloadFail);
    }

    function onRequestFileSystemFailt()
    {
        
    }

    function onRequestFileSystemComplete(fileSystem)
    {
        console.log(JSON.stringify(fileSystem));
        var opts = {
            create: true,
            explicity: false
        }
        
        fileSystem.root.getFile('filename.apk', opts, onGetFileComplete, onGetFileFailt);
    }
}
