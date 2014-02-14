package com.phonegap.plugin;

import org.apache.cordova.api.CordovaPlugin;
import org.apache.cordova.api.PluginResult;
import org.apache.cordova.api.CallbackContext;
import org.apache.cordova.api.CordovaInterface;
import org.apache.cordova.CordovaWebView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.util.Log;
import android.app.Activity;

import java.util.HashMap;
import java.util.ArrayList;
import java.util.Date;
import java.util.Set;

import java.io.UnsupportedEncodingException;

import java.text.SimpleDateFormat;

import android.widget.Toast;

import com.woosim.bt.WoosimPrinter;

public class BluetoothPrinter extends CordovaPlugin
{
    private WoosimPrinter woosim;
    private String printerMacAddress;
    private final static String CHARSET = "GBK";
    private final static String TAG = "BluetoothPrinter";

    public final int DEVICE_CONNECT_SUCCESS = 1;  //连接成功
    public final int DEVICE_CONNECT_FAILED = -2;  //连接失败
    public final int DEVICE_IS_NOT_BONDED = -5;   //没有配对
    public final int DEVICE_ALREADY_CONNECTED = -6; //已经连接
    public final int DEVICE_BLUETOOTH_DISABLED = -8; //蓝牙没有打开
    public final int DEVICE_NO_MAC_FOUND = -9;  //没有提供mac地址

    private final String PREFERENCE_NAME = "com.phonegap.plugin.BluetoothPrinter";

    @Override
    public void initialize(CordovaInterface cordova, CordovaWebView webView) {
        super.initialize(cordova, webView);

        Activity app = cordova.getActivity();
        String mac = app.getSharedPreferences(PREFERENCE_NAME, Context.MODE_PRIVATE).getString("printer_mac", null);

        String msg;

        int reVal = connect(mac);
        switch(reVal) {
        case DEVICE_CONNECT_SUCCESS:
            msg = "打印机连接成功";
            break;
        case DEVICE_CONNECT_FAILED:
            msg = "打印机连接失败";
            break;
        case DEVICE_IS_NOT_BONDED:
            msg = "未配对的打印机";
            break;
        case DEVICE_ALREADY_CONNECTED:
            msg = "已经连接";
            break;
        case DEVICE_BLUETOOTH_DISABLED:
            msg = "蓝牙未打开";
            break;
        case DEVICE_NO_MAC_FOUND:
            msg = "请先在打印机设置里面选择要使用的打印机";
            break;
        default:
            msg = "未知错误";
            break;
        }

        Toast.makeText(app, msg, 2).show();
    }
    
    @Override
    public boolean execute(String action, JSONArray args, CallbackContext callbackContext)
        throws JSONException {
        if (action.equals("init")) {
            callbackContext.success("ok");
            return true;
        }else if (action.equals("print")) {
            printString(args.getString(0), callbackContext);
            return true;
        } else if (action.equals("getPairedDevices")) {
            getPairedBluetoothDevices(callbackContext);
            return true;
        } else if (action.equals("open")) {
            connect(args.getString(0), callbackContext);
            return true;
        } else if (action.equals("close")) {
            disconnect(callbackContext);
            return true;
        }

        return false;
    }

    private int connect(String mac_address)
    {
        disconnect();
        woosim = new WoosimPrinter();
        int reVal = -2;

        try {
            reVal = woosim.BTConnection(mac_address, false);
            if (reVal != 1)
                woosim = null;
        } catch (Exception e) {
            return DEVICE_NO_MAC_FOUND;
        }

        return reVal;
    }
    
    private void disconnect()
    {
        if (woosim != null) {
            woosim.closeConnection();
            woosim = null;
        }
    }
    
    private void connect(final String mac_address, final CallbackContext callbackContext)
    {
        disconnect();
        cordova.getActivity().runOnUiThread(new Runnable() {
                public void run()
                {
                    int reVal = -2;

                    reVal = connect(mac_address);

                    switch(reVal) {
                        case DEVICE_CONNECT_SUCCESS:
                            SharedPreferences.Editor ed =
                                cordova.getActivity().getSharedPreferences(PREFERENCE_NAME, Context.MODE_PRIVATE).edit();
                            ed.putString("printer_mac", mac_address);
                            ed.commit();
                            callbackContext.success("连接成功"); break;
                        case DEVICE_CONNECT_FAILED:
                            callbackContext.error("连接失败"); break;
                        case DEVICE_IS_NOT_BONDED:
                            callbackContext.error("未配对的打印机"); break;
                        case DEVICE_ALREADY_CONNECTED:
                            callbackContext.success("已经连接"); break;
                        case DEVICE_BLUETOOTH_DISABLED:
                            callbackContext.error("蓝牙未打开"); break;
                        case DEVICE_NO_MAC_FOUND:
                            callbackContext.error("请先在打印机设置里面选择要使用的打印机"); break;
                        default:
                            callbackContext.error("未知错误");
                    }
                }
            });
    }

    private void disconnect(CallbackContext callbackContext)
    {
        disconnect();
        callbackContext.success("ok");
    }
    private void printString(final String printContent, final CallbackContext callbackContext)
    {
        if (woosim == null)
            callbackContext.error("请在打印设置里面选择要使用的打印机");
        else
            cordova.getActivity().runOnUiThread(new Runnable() {
                    public void run()
                    {
                        byte[] init = {0x1b,'@'};
                        woosim.controlCommand(init, init.length);
                        byte[] lf = {0x0a};
                        woosim.controlCommand(lf, lf.length);

                        woosim.saveSpool(CHARSET, printContent, 0, false);
		
                        woosim.printSpool(true);

                        callbackContext.success("ok");
                    }
                });
    }

    private void getPairedBluetoothDevices(CallbackContext callbackContext)
    {
        // Get a set of currently paired devices
        BluetoothAdapter ba = BluetoothAdapter.getDefaultAdapter();

        if (ba == null) {
            callbackContext.error("此终端不支持蓝牙功能");
            return;
        }

        Set<BluetoothDevice> pairedDevices = ba.getBondedDevices();

        if (pairedDevices == null) {
            callbackContext.error("获取蓝牙配对信息出错, 原因不明");
            return;
        }

        ArrayList<HashMap<String, String>> t = new ArrayList<HashMap<String, String>>();
        HashMap<String, String> tmp;
        
        for (BluetoothDevice device : pairedDevices) {
            tmp = new HashMap<String, String>();
            tmp.put("device_name", device.getName());
            tmp.put("mac_address", device.getAddress());
            t.add(tmp);
        }

        JSONArray arr = new JSONArray();
            
        for (HashMap<String, String> device : t) {
            arr.put(new JSONObject(device));
        }
        callbackContext.success(arr);
    }

    @Override
    public void onReset()
    {
        disconnect();
    }

    @Override
    public void onDestroy()
    {
        disconnect();
    }
}
