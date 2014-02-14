package com.djoin.parking;

import android.graphics.drawable.Drawable;
import android.graphics.Paint;
import android.graphics.RectF;
import android.graphics.Rect;
import android.graphics.Canvas;
import android.graphics.ColorFilter;
import android.graphics.Paint.Style;
import android.graphics.PixelFormat;
import android.util.Log;

public class NotifyDrawable extends Drawable
{
    private static final String TAG = "NotifyDrawable";
    private int msgCount = 0;
    
    public NotifyDrawable()
    {
        //super();
    }

    @Override
    public void draw(Canvas canvas)
    {
        int font_size = 24, text_x = -7, text_y = 8;

        if (msgCount > 99) {
            font_size = 20;
            text_x = -17;            
        } else if (msgCount > 9) {
            font_size = 22;
            text_x = -12;
        }
        
        // Set the correct values in the Paint
        Paint bg_pen = new Paint();
        bg_pen.setARGB(127, 0x00, 0x99, 0xcc);
        bg_pen.setStrokeWidth(2);
        bg_pen.setStyle(Style.FILL);

        Paint text_pen = new Paint(Paint.FAKE_BOLD_TEXT_FLAG | Paint.ANTI_ALIAS_FLAG);
        text_pen.setARGB(255, 0xef, 0xef, 0xef);
        text_pen.setTextSize(font_size);

        // Draw it
        canvas.drawRoundRect(new RectF(-20, -20, 20, 20), 5, 5, bg_pen);
        canvas.drawText(String.format("%d", msgCount), text_x, text_y, text_pen);
    }

    @Override
    public int getOpacity()
    {
        return PixelFormat.OPAQUE;
    }

    @Override
    public void setAlpha(int arg0)
    {
    }

    @Override
    public void setColorFilter(ColorFilter arg0)
    {
    }

    public void setCount(int msgCount)
    {
        this.msgCount = msgCount;
        invalidateSelf();
    }
}

