package com.cs3237_group_3.fall_detection_app;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.util.Log;

import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;

public class MainActivity extends AppCompatActivity {
    private final String TAG = "MainActivity";
    private final static int REQUEST_ENABLE_LOCATION = 7;
    private final static int REQUEST_ENABLE_BT = 17;

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
//        MqttClient mqttClient = new MqttClient(getApplicationContext());
        GlobalViewModel globalViewModel = new ViewModelProvider(this).get(GlobalViewModel.class);
        globalViewModel.initBleServices(
                (BluetoothManager) getSystemService(Context.BLUETOOTH_SERVICE),
                getApplicationContext());
        final Observer<ConfigurationData> configObserver = config -> {
            if (config == null) {
                Log.e(TAG, "ConfigurationData is null");
                return;
            }
            globalViewModel.getBleManager().connectToSensorTags(config.getWristSensorMacAdd(),
                    config.getWaistSensorMacAdd());
        };
        globalViewModel.getConfigurationLiveDataFromRepo().observe(this, configObserver);
    }

    @Override
    protected void onResume() {
        super.onResume();
        requestBlePermission();
        requestLocationPermission();
    }
    private void requestLocationPermission() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[] {Manifest.permission.ACCESS_FINE_LOCATION},
                    REQUEST_ENABLE_LOCATION);
        }
    }

    private void requestBlePermission() {
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
                requestBlePermission();
            }
        } else if (requestCode == REQUEST_ENABLE_LOCATION) {
            Log.i(TAG, "ACCESS_FINE_LOCATION result code:  " + resultCode);
            if (resultCode != RESULT_OK) {
                requestLocationPermission();
            }
        }
    }
}
