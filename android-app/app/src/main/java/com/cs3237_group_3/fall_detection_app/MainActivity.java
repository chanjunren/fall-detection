package com.cs3237_group_3.fall_detection_app;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import android.bluetooth.BluetoothAdapter;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;

import com.cs3237_group_3.fall_detection_app.gateway.MqttClient;

import static androidx.core.app.ActivityCompat.startActivityForResult;

public class MainActivity extends AppCompatActivity {
    private final String TAG = "MainActivity";
    private final static int REQUEST_ENABLE_BT = 17;
    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
//        MqttClient mqttClient = new MqttClient(getApplicationContext());
        requestForBluetooth();
    }


    private void requestForBluetooth() {
//        Optionally, your app can also listen for the ACTION_STATE_CHANGED broadcast intent,
//        which the system broadcasts whenever the Bluetooth state changes.
//        This broadcast contains the extra fields EXTRA_STATE and EXTRA_PREVIOUS_STATE,
//        containing the new and old Bluetooth states, respectively.
//        Possible values for these extra fields are STATE_TURNING_ON, STATE_ON, STATE_TURNING_OFF, and STATE_OFF.
//        Listening for this broadcast can be useful if your app needs to detect runtime changes made to the Bluetooth state.
        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bluetoothAdapter == null) {
            // Device doesn't support Bluetooth
            Log.e(TAG, "Device does not support bluetooth");
        }
        if (bluetoothAdapter.isEnabled()) {
            Log.i(TAG, "Bluetooth adapter is enabled nigga");
        }
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }

    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable @org.jetbrains.annotations.Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_ENABLE_BT) {
            Log.i(TAG, "REQUEST_ENABLE_BT result code:  " + resultCode);
            if (resultCode != RESULT_OK) {
                requestForBluetooth();
            }
        }
    }
}
