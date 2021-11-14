package com.cs3237_group_3.fall_detection_app.gateway;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.os.ParcelUuid;
import android.util.Log;

import androidx.lifecycle.MutableLiveData;

import static com.cs3237_group_3.fall_detection_app.util.Utilities.CC2650_DATA_UUID_STRING;

public class BleManager {
    private final String TAG = "BleManager";

    private Context context;
    private BluetoothLeScanner bleScanner;

    // For connection
    private String waistTagMacAdd, wristTagMacAdd;
    private BluetoothDevice waistSensorTag, wristSensorTag;
    private BluetoothGatt waistGatt, wristGatt;
    private MutableLiveData<Boolean> isWaistSensorTagConnected, isWristSensorTagConnected;
    private BluetoothGattCallback waistConnCallback, wristConnCallback,
            waistReadCallback, wristReadCallback;
    private ScanCallback connScanCallback, waistScanCallback, wristScanCallback;

    public BleManager(BluetoothManager bluetoothManager, Context context) {
        this.bleScanner = bluetoothManager.getAdapter().getBluetoothLeScanner();
        isWaistSensorTagConnected = new MutableLiveData<>(false);
        isWristSensorTagConnected = new MutableLiveData<>(false);
        this.context = context;
    }

    // Notable errors
        // 1. scanning too frequently => scanning cannot exceed 30 seconds
            // if need scan for longer need to stop then start again
        // 2. SCAN_FAILED_APPLICATION_REGISTRATION_FAILED
            // disable / re-enable bluetooth OR ask users reboot android device

    public void startBleScan(ScanCallback scanCallback) {
        ScanFilter filter = new ScanFilter.Builder().setServiceUuid(
            ParcelUuid.fromString(CC2650_DATA_UUID_STRING)
        ).build();

        ScanSettings scanSettings = new ScanSettings.Builder()
                // Scanning for a short period of time to find specific device
                .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
                // Single callback for EACH device
                .setCallbackType(ScanSettings.CALLBACK_TYPE_ALL_MATCHES)
                // Filtering out devices that are too far away
                .setMatchMode(ScanSettings.MATCH_MODE_STICKY)
                .build();
        Log.i(TAG, "Starting scan...");
        bleScanner.startScan(null, scanSettings, scanCallback);
    }

    public void stopBleScan(ScanCallback scanCallback) {
        Log.i(TAG, "Stopping scan...");
        bleScanner.stopScan(scanCallback);
    }

    public void connectToSensorTags(String wristTagMacAdd, String waistTagMacAdd) {
        this.wristTagMacAdd = wristTagMacAdd;
        this.waistTagMacAdd = waistTagMacAdd;
        initAllCallbacksForConnection();
        startBleScan(connScanCallback);
    }

    public void refreshConnectionForWaistTag() {
        initWaistScanCallback();
        startBleScan(waistScanCallback);
    }

    public void refreshConnectionForWristTag() {
        initWristScanCallback();
        startBleScan(wristScanCallback);
    }

    private void initAllCallbacksForConnection() {
        initConnScanCallback();
        initConnectionCallbackForWaist();
        initConnectionCallbackForWrist();
    }

    private void initConnScanCallback() {
        this.connScanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                super.onScanResult(callbackType, result);
                if (result.getDevice().getAddress().equals(wristTagMacAdd)) {
                    wristSensorTag = result.getDevice();
                    connectToWristSensorTag();
                }
                if (result.getDevice().getAddress().equals(waistTagMacAdd)) {
                    waistSensorTag = result.getDevice();
                    connectToWaistSensorTag();
                }
                if (wristSensorTag != null && waistSensorTag != null) {
                    stopBleScan(this);
                }
            }

            @Override
            public void onScanFailed(int errorCode) {
                super.onScanFailed(errorCode);
                Log.e(TAG, "Error code while scanning: " + errorCode);
            }
        };
    }

    private void initWristScanCallback() {
        this.wristScanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                super.onScanResult(callbackType, result);
                if (result.getDevice().getAddress().equals(wristTagMacAdd)) {
                    wristSensorTag = result.getDevice();
                    connectToWristSensorTag();
                    stopBleScan(this);
                }
            }

            @Override
            public void onScanFailed(int errorCode) {
                super.onScanFailed(errorCode);
                Log.e(TAG, "Error code while scanning: " + errorCode);
            }
        };
    }

    private void initWaistScanCallback() {
        this.waistScanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                super.onScanResult(callbackType, result);
                if (result.getDevice().getAddress().equals(waistTagMacAdd)) {
                    waistSensorTag = result.getDevice();
                    connectToWaistSensorTag();
                    stopBleScan(this);
                }
            }

            @Override
            public void onScanFailed(int errorCode) {
                super.onScanFailed(errorCode);
                Log.e(TAG, "Error code while scanning: " + errorCode);
            }
        };
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
                        isWristSensorTagConnected.postValue(true);
                        wristGatt = gatt;
                    } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                        Log.i(TAG, "Succesfully disconnected from " +
                                wristSensorTag.getAddress());
                        isWristSensorTagConnected.postValue(false);
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
                        isWaistSensorTagConnected.postValue(true);
                        waistGatt = gatt;
                    } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                        Log.i(TAG, "Succesfully disconnected from " + waistSensorTag.getAddress());
                        isWaistSensorTagConnected.postValue(false);
                        waistGatt.close();
                    }
                } else {
                    Log.i(TAG, "Unsuccessful: status " + status);
                }
            }
        };
    }

    public MutableLiveData<Boolean> getWaistConnStatusLiveData() {
        return isWaistSensorTagConnected;
    }

    public MutableLiveData<Boolean> getWristConnStatusLiveData() {
        return isWristSensorTagConnected;
    }

    public void connectToWaistSensorTag() {
        waistSensorTag.connectGatt(context, true, waistConnCallback);
    }

    public void connectToWristSensorTag() {
        wristSensorTag.connectGatt(context, true, wristConnCallback);
    }

//    private
//
//    public void readBatteryLevel() {
//
//    }

    public void readCharacteristic() {
//        BluetoothGattCharacteristic gattCharacteristic = new BluetoothGattCharacteristic();
//        waistGatt.readCharacteristic(Blue)
    }
}
