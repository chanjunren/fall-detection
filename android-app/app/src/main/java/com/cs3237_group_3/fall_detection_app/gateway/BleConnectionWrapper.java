package com.cs3237_group_3.fall_detection_app.gateway;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothProfile;
import android.content.Context;
import android.util.Log;

import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;

public class BleConnectionWrapper {
    private final String TAG = "BleConnectionWrapper";
    private BluetoothDevice waistSensorTag, wristSensorTag;
    private BluetoothGatt waistGatt, wristGatt;
    private Context context;
    private MutableLiveData<Boolean> isWaistSensorTagConnected, isWristSensorTagConnected;
    private BluetoothGattCallback waistConnCallback, wristConnCallback;

    public BleConnectionWrapper(Context context, BluetoothDevice wristSensorTag,
                                BluetoothDevice waistSensorTag) {
        this.context = context;
        this.wristSensorTag = wristSensorTag;
        this.waistSensorTag = waistSensorTag;
        this.isWaistSensorTagConnected = new MutableLiveData<Boolean>(false);
        this.isWristSensorTagConnected = new MutableLiveData<Boolean>(false);
        initConnectionCallbackForWrist();
        initConnectionCallbackForWaist();
    }

    private void initConnectionCallbackForWrist() {
        this.wristConnCallback = new BluetoothGattCallback() {
            @Override
            public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
                super.onConnectionStateChange(gatt, status, newState);
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    if (newState == BluetoothProfile.STATE_CONNECTED) {
                        Log.i(TAG, "Successfully connected to " + wristSensorTag.getAddress());
                        // Store reference for BluetoothGatt
                        wristGatt = gatt;
                    } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                        Log.i(TAG, "Succesfully disconnected from " +
                                wristSensorTag.getAddress());
                        wristGatt.close();
                    }
                }
            }
        };
    }

    private void initConnectionCallbackForWaist() {
        this.waistConnCallback = new BluetoothGattCallback() {
            @Override
            public void onConnectionStateChange(BluetoothGatt gatt, int status, int newState) {
                super.onConnectionStateChange(gatt, status, newState);
                if (status == BluetoothGatt.GATT_SUCCESS) {
                    if (newState == BluetoothProfile.STATE_CONNECTED) {
                        Log.i(TAG, "Successfully connected to " + waistSensorTag.getAddress());
                        // Store reference for BluetoothGatt
                        waistGatt = gatt;
                    } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                        Log.i(TAG, "Succesfully disconnected from " + waistSensorTag.getAddress());
                        waistGatt.close();
                    }
                } else {
                    Log.i(TAG, "Unsuccessful: status " + status);
                }
            }
        };
    }



    public MutableLiveData<Boolean> getIsWaistSensorTagConnected() {
        return isWaistSensorTagConnected;
    }

    public void setIsWaistSensorTagConnected(MutableLiveData<Boolean> isWaistSensorTagConnected) {
        this.isWaistSensorTagConnected = isWaistSensorTagConnected;
    }

    public MutableLiveData<Boolean> getIsWristSensorTagConnected() {
        return isWristSensorTagConnected;
    }

    public void setIsWristSensorTagConnected(MutableLiveData<Boolean> isWristSensorTagConnected) {
        this.isWristSensorTagConnected = isWristSensorTagConnected;
    }

    public BluetoothGattCallback getWaistConnCallback() {
        return waistConnCallback;
    }
}
