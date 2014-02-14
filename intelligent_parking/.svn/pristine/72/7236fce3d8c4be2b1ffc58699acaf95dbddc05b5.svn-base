/*
       Licensed to the Apache Software Foundation (ASF) under one
       or more contributor license agreements.  See the NOTICE file
       distributed with this work for additional information
       regarding copyright ownership.  The ASF licenses this file
       to you under the Apache License, Version 2.0 (the
       "License"); you may not use this file except in compliance
       with the License.  You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

       Unless required by applicable law or agreed to in writing,
       software distributed under the License is distributed on an
       "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
       KIND, either express or implied.  See the License for the
       specific language governing permissions and limitations
       under the License.
 */

package com.djoin.parking;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.HashMap;

import org.apache.cordova.Config;
import org.apache.cordova.CordovaChromeClient;
import org.apache.cordova.CordovaWebView;
import org.apache.cordova.CordovaWebViewClient;
import org.apache.cordova.DroidGap;
import org.apache.cordova.api.LOG;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.content.Context;
import android.graphics.Color;
import android.os.Bundle;
import android.os.Handler;
import android.os.Vibrator;
import android.support.v4.widget.DrawerLayout;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.ViewConfiguration;
import android.view.ViewGroup;
import android.webkit.JavascriptInterface;
import android.widget.AdapterView;
import android.widget.LinearLayout;
import android.widget.ListView;

public class parking extends DroidGap
{
    protected LinearLayout myroot;

    private ListView mLeftNav;
    private DrawerLayout mDrawerLayout;
    private Handler mUiUpdator = new Handler();
    private MenuItem counter;
    private NotifyDrawable nd;
    
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        setBooleanProperty("showTitle", true);
        setIntegerProperty("splashscreen", R.drawable.boot);
        super.onCreate(savedInstanceState);

        try {
            ViewConfiguration config = ViewConfiguration.get(this);
            Field menuKeyField = ViewConfiguration.class.getDeclaredField("sHasPermanentMenuKey");
            if(menuKeyField != null) {
                menuKeyField.setAccessible(true);
                menuKeyField.setBoolean(config, false);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        super.loadUrl(Config.getStartUrl(), 10000);
    }
    
    @SuppressLint("NewApi")
    @Override
    public void init(CordovaWebView webView, CordovaWebViewClient webViewClient, CordovaChromeClient webChromeClient) {
        LOG.d(TAG, "CordovaActivity.init()");

        // Set up web container
        this.appView = webView;
        this.appView.setId(100);

        //增加js接口
        this.appView.addJavascriptInterface(new JsInterface(), "jsinterface");

        this.appView.setWebViewClient(webViewClient);
        this.appView.setWebChromeClient(webChromeClient);
        webViewClient.setWebView(this.appView);
        webChromeClient.setWebView(this.appView);

        this.appView.setLayoutParams(new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT,
                1.0F));

        if (this.getBooleanProperty("disallowOverscroll", false)) {
            if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.GINGERBREAD) {
                this.appView.setOverScrollMode(CordovaWebView.OVER_SCROLL_NEVER);
            }
        }

        // Add web view but make it invisible while loading URL
        this.appView.setVisibility(View.INVISIBLE);

        View v = getLayoutInflater().inflate(R.layout.main, null);
        
        mDrawerLayout = (DrawerLayout) v.findViewById(R.id.drawer_layout);
        myroot = (LinearLayout) v.findViewById(R.id.content_frame);
        mLeftNav = (ListView) v.findViewById(R.id.left_nav);

        mDrawerLayout.setDrawerLockMode(DrawerLayout.LOCK_MODE_LOCKED_CLOSED);

        myroot.setBackgroundColor(Color.BLACK);

        setTheme(R.style.gray);

        getActionBar().setDisplayHomeAsUpEnabled(true);
        getActionBar().setHomeButtonEnabled(true);

        myroot.addView(this.appView);
        
        setContentView(mDrawerLayout);
        // Clear cancel flag
        this.cancelLoadUrl = false;
        
    }

    private class LeftNavClickListener implements ListView.OnItemClickListener {
        private NavigationAdapter na;
        public LeftNavClickListener(NavigationAdapter n)
        {
            super();
            na = n;
        }
        
        @Override
        public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
            HashMap<String, Object> item = (HashMap<String, Object>) na.getItem(position);
            parking.this.sendJavascript(String.format("$.mobile.changePage(\"%s\")", item.get("url").toString()));
            mDrawerLayout.closeDrawer(mLeftNav);
        }
    }

    private class JsInterface
    {
        @JavascriptInterface
        public void setNavigationContent(final String jsonArray)
        {
            mUiUpdator.post(new Runnable() {
                    public void run()
                    {
                        ArrayList<HashMap<String, Object>> array = new ArrayList<HashMap<String, Object>>();
                        HashMap<String, Object> hm;
                        JSONObject t;
                        NavigationAdapter n;
                        
                        try {
                            JSONArray list = new JSONArray(jsonArray);
                        
                            for(int i = 0; i < list.length(); i++) {
                                hm = new HashMap<String, Object>();
                                t = list.getJSONObject(i);
                                hm.put("icon", t.getString("icon"));
                                hm.put("title", t.getString("title"));
                                hm.put("url", t.getString("url"));
                                array.add(hm);
                            }
                            n = new NavigationAdapter<HashMap<String, Object>>(parking.this, R.layout.list_item, array);
                            mLeftNav.setAdapter(n);
                            mLeftNav.setOnItemClickListener(new LeftNavClickListener(n));
                            mDrawerLayout.setDrawerLockMode(DrawerLayout.LOCK_MODE_UNLOCKED);
                        } catch (JSONException e) {
                            LOG.e("JsInterface", jsonArray + "is invalide");
                        };
                    }
                });
        }

        @JavascriptInterface
        public void lockNavigation(final boolean isShow)
        {
            mUiUpdator.post(new Runnable() {
                    public void run()
                    {
                        if (isShow)
                            mDrawerLayout.setDrawerLockMode(DrawerLayout.LOCK_MODE_UNLOCKED);
                        else
                            mDrawerLayout.setDrawerLockMode(DrawerLayout.LOCK_MODE_LOCKED_CLOSED);
                    }
                });
        }

        @JavascriptInterface
        public void updateNotifyCount(final int count)
        {
            mUiUpdator.post(new Runnable() {
                    public void run()
                    {
                        nd.setCount(count);
                        counter.setVisible(true);
                        ((Vibrator)getSystemService(Context.VIBRATOR_SERVICE)).vibrate(1000);
                    }
                });
        }

        @JavascriptInterface
        public void setNotifyVisible(final boolean showup)
        {
            mUiUpdator.post(new Runnable() {
                    public void run()
                    {
                        counter.setVisible(showup);
                    }
                });
        }
    }

    @Override
    public void loadUrl(final String url, int time)
    {
        this.splashscreenTime = time;
        this.splashscreen = this.getIntegerProperty("splashscreen", 0);
        this.showSplashScreen(this.splashscreenTime);

        // Init web view if not already done
        if (this.appView == null) {
            this.init();
        }

        this.appView.loadUrl(url, time);
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu)
    {
        MenuInflater inflater = getMenuInflater();
        inflater.inflate(R.menu.overlay_menu, menu);
        counter = menu.findItem(R.id.message_count);
        nd = new NotifyDrawable();
        counter.setIcon(nd);
        return super.onCreateOptionsMenu(menu);
    }
    
    @Override
    public boolean onPrepareOptionsMenu (Menu menu)
    {
        return super.onPrepareOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item)
    {
        this.postMessage("onOptionsItemSelected", item);
        switch (item.getItemId()) {
            case android.R.id.home:
                //this.sendJavascript("$.mobile.changePage(\"/mobile/login\")");
                return true;
            case R.id.print_setup:
                this.sendJavascript("$.mobile.changePage(\"/mobile/setup_printer\")");
                return true;
            case R.id.message_count:
                this.sendJavascript("$.mobile.changePage(\"/mobile/messages\")");
                return true;
            default:
                return super.onOptionsItemSelected(item);
        }
        
    }
    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent intent)
    {
        super.onActivityResult(requestCode, resultCode, intent);
    }
}

