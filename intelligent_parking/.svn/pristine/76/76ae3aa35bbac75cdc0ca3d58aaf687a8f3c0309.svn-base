package com.djoin.parking;

import android.widget.ArrayAdapter;
import android.widget.TextView;
import android.widget.ImageView;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.content.Context;

import java.util.List;
import java.util.Map;
import java.util.HashMap;

import java.lang.reflect.Field;

public class NavigationAdapter<T> extends ArrayAdapter<T>
{
    private int mResource;
    private List<T> mObjects;
    private Context mContext;
    private LayoutInflater mInflater;
    
    public NavigationAdapter(Context ctx, int resourceId, List<T> objects)
    {
        super(ctx, resourceId, objects);
        mContext = ctx;
        mInflater = (LayoutInflater)ctx.getSystemService(Context.LAYOUT_INFLATER_SERVICE);
        mResource  = resourceId;
        mObjects = objects;
    }
    
    @Override
    public View getView(int position, View convertView, ViewGroup parent)
    {
        View v = mInflater.inflate(mResource, parent, false);
        ImageView icon = (ImageView) v.findViewById(R.id.navigation_icon);
        TextView title = (TextView) v.findViewById(R.id.navigation_title);
        
        Map<String, Object> d = (Map<String, Object>) mObjects.get(position);
        int icon_resource;
        
        icon_resource = mContext.getResources().getIdentifier(d.get("icon").toString(), "drawable", mContext.getPackageName());
        icon_resource = icon_resource == 0 ? R.drawable.default_navigation_icon : icon_resource;

        icon.setImageResource(icon_resource);
        title.setText(d.get("title").toString());
        return v;
    }

    public void updateNotifyCount(String key, int count)
    {

    }
}
