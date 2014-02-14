package com.phonegap.plugin;

import java.util.HashMap;
import java.util.Map;

import org.apache.cordova.DroidGap;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.content.Intent;
import android.net.Uri;
import android.util.Log;
import android.text.Html;
import android.app.Activity;

import org.apache.cordova.api.CordovaPlugin;
import org.apache.cordova.api.PluginResult;
import org.apache.cordova.api.CallbackContext;

public class WebIntent extends CordovaPlugin {

    private final String TAG = "WebIntent";

    @Override
    public boolean execute(String action, JSONArray args, CallbackContext callbackContext) throws JSONException
    {
        Log.d(TAG, ">>>>>>>>>>>>>>>>>>>>");
        if (action.equals("startActivity")) {
            if (args.length() != 1) {
                callbackContext.error("无效的ACTION");
                return true;
            }

            // Parse the arguments
            JSONObject obj = args.getJSONObject(0);

            String packageName = obj.has("package") ? obj.getString("package") : null;
            String type = obj.has("type") ? obj.getString("type") : null;
            Uri uri = obj.has("url") ? Uri.parse(obj.getString("url")) : null;
            JSONObject extras = obj.has("extras") ? obj.getJSONObject("extras") : null;
            Map<String, String> extrasMap = new HashMap<String, String>();

            // Populate the extras if any exist
            if (extras != null) {
                JSONArray extraNames = extras.names();
                for (int i = 0; i < extraNames.length(); i++) {
                    String key = extraNames.getString(i);
                    String value = extras.getString(key);
                    extrasMap.put(key, value);
                }
            }

            if (packageName != null)
                startActivity(packageName, extrasMap);
            else
                startActivity(obj.getString("action"), uri, type, extrasMap);
            callbackContext.success();
            return true;

        }
        return true;
    }

    //增加一个, 用于运行外部程序
    void startActivity(String packageName, Map<String, String> extras)
    {
        Activity a = this.cordova.getActivity();
        Intent i = a.getApplication().getPackageManager().getLaunchIntentForPackage(packageName);
        i.addCategory(Intent.CATEGORY_LAUNCHER);
        
        for (String key : extras.keySet()) {
            String value = extras.get(key);
            i.putExtra(key, value);
        }

        ((DroidGap)a).startActivity(i);
    }
    
    void startActivity(String action, Uri uri, String type, Map<String, String> extras) {
        Intent i = (uri != null ? new Intent(action, uri) : new Intent(action));
        
        if (type != null && uri != null) {
            i.setDataAndType(uri, type); //Fix the crash problem with android 2.3.6
        } else {
            if (type != null) {
                i.setType(type);
            }
        }
        
        for (String key : extras.keySet()) {
            String value = extras.get(key);
            // If type is text html, the extra text must sent as HTML
            if (key.equals(Intent.EXTRA_TEXT) && type.equals("text/html")) {
                i.putExtra(key, Html.fromHtml(value));
            } else if (key.equals(Intent.EXTRA_STREAM)) {
                // allowes sharing of images as attachments.
                // value in this case should be a URI of a file
                i.putExtra(key, Uri.parse(value));
            } else if (key.equals(Intent.EXTRA_EMAIL)) {
                // allows to add the email address of the receiver
                i.putExtra(Intent.EXTRA_EMAIL, new String[] { value });
            } else {
                i.putExtra(key, value);
            }
        }
        ((DroidGap)this.cordova.getActivity()).startActivity(i);
    }
}
