package com.cs3237_group_3.fall_detection_app;

import androidx.appcompat.app.AppCompatActivity;

import android.os.Bundle;

import com.cs3237_group_3.fall_detection_app.gateway.MqttClient;

public class MainActivity extends AppCompatActivity {
    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        MqttClient mqttClient = new MqttClient(getApplicationContext());
    }
}
