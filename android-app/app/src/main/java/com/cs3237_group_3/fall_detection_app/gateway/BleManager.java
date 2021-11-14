package com.cs3237_group_3.fall_detection_app.gateway;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGatt;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothGattCharacteristic;
import android.bluetooth.BluetoothGattService;
import android.bluetooth.BluetoothManager;
import android.bluetooth.BluetoothProfile;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.content.Context;
import android.content.Intent;
import android.os.ParcelUuid;
import android.util.Log;

import androidx.lifecycle.MutableLiveData;

import java.util.List;
import java.util.UUID;

import static com.cs3237_group_3.fall_detection_app.util.Utilities.BATT_SERVICE_UUID;
import static com.cs3237_group_3.fall_detection_app.util.Utilities.CC2650_DATA_UUID;
import static com.cs3237_group_3.fall_detection_app.util.Utilities.CC2650_DATA_UUID_STRING;
import static com.cs3237_group_3.fall_detection_app.util.Utilities.CC2650_SERVICE_UUID;
import static com.cs3237_group_3.fall_detection_app.util.Utilities.CC2650_SERV_UUID_STRING;

public class BleManager {
    private final String TAG = "BleManager";
    private Byte[] buffer;
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
                BluetoothManager manager = (BluetoothManager) context.getSystemService(Context.BLUETOOTH_SERVICE);
                manager.getAdapter().disable();
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
                        wristGatt.discoverServices();
//                        readCharacteristicFromUuid(wristGatt, CC2650_SERVICE_UUID, CC2650_DATA_UUID);
                    } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                        Log.i(TAG, "Succesfully disconnected from " +
                                wristSensorTag.getAddress());
                        isWristSensorTagConnected.postValue(false);
                        wristGatt.close();
                    }
                }
            }

            @Override
            public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
                super.onCharacteristicRead(gatt, characteristic, status);
                if  (status == BluetoothGatt.GATT_SUCCESS) {
                    broadcastUpdate(null, characteristic);
                } else if (status == BluetoothGatt.GATT_READ_NOT_PERMITTED) {
                    Log.e(TAG, String.format("Read not permitted for this uuid: !",
                            characteristic.getUuid().toString()));
                } else {
                    Log.e(TAG, "Bluetooth read failed for " +
                            characteristic.getUuid().toString());
                }
            }

            @Override
            public void onServicesDiscovered(BluetoothGatt gatt, int status) {
                super.onServicesDiscovered(gatt, status);
//                for (BluetoothGattService s: gatt.getServices()) {
//                    Log.i(TAG, s.toString());
//                }
//                readCharacteristicFromUuid(gatt, CC2650_SERVICE_UUID, CC2650_DATA_UUID);
                for (BluetoothGattService service: gatt.getServices()) {
                    if (service.getUuid().toString().equals(CC2650_SERV_UUID_STRING)) {
                        Log.i(TAG, "Service UUID found!");
                        for (BluetoothGattCharacteristic c: service.getCharacteristics()) {
                            if (c.getUuid().toString().equals(CC2650_DATA_UUID_STRING)) {
                                Log.i(TAG, "Characteristic UUID found!");
                                gatt.readCharacteristic(c);
                            }
                        }
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
                        waistGatt.discoverServices();
                        //                        readCharacteristicFromUuid(waistGatt, CC2650_SERVICE_UUID, CC2650_DATA_UUID);
                    } else if (newState == BluetoothProfile.STATE_DISCONNECTED) {
                        Log.i(TAG, "Succesfully disconnected from " + waistSensorTag.getAddress());
                        isWaistSensorTagConnected.postValue(false);
                        waistGatt.close();
                    }
                } else {
                    Log.i(TAG, "Unsuccessful: status " + status);
                }
            }
            @Override
            public void onCharacteristicRead(BluetoothGatt gatt, BluetoothGattCharacteristic characteristic, int status) {
                super.onCharacteristicRead(gatt, characteristic, status);
                if  (status == BluetoothGatt.GATT_SUCCESS) {
                    broadcastUpdate(null, characteristic);
                } else if (status == BluetoothGatt.GATT_READ_NOT_PERMITTED) {
                    Log.e(TAG, String.format("Read not permitted for this uuid: !",
                            characteristic.getUuid().toString()));
                } else {
                    Log.e(TAG, "Bluetooth read failed for " +
                            characteristic.getUuid().toString());
                }
            }
            @Override
            public void onServicesDiscovered(BluetoothGatt gatt, int status) {
                super.onServicesDiscovered(gatt, status);
                for (BluetoothGattService service: gatt.getServices()) {
                    if (service.getUuid().toString().equals(CC2650_SERV_UUID_STRING)) {
                        Log.i(TAG, "Service UUID found!");
                        for (BluetoothGattCharacteristic c: service.getCharacteristics()) {
                            if (c.getUuid().toString().equals(CC2650_DATA_UUID_STRING)) {
                                Log.i(TAG, "Characteristic UUID found!");
                                gatt.readCharacteristic(c);
                            }
                        }
                    }
                }
//                for (BluetoothGattService s: gatt.getServices()) {
//                    Log.i(TAG, "===== " + s.getUuid().toString() + " =====");
//                    for (BluetoothGattCharacteristic c: s.getCharacteristics()) {
//                        Log.i(TAG, "\tCharacteristic UUID: " + c.getUuid().toString());
//                    }
//                }
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

    public void readCharacteristicFromUuid(BluetoothGatt gatt, UUID serviceUuid, UUID charUuid) {
        Log.i(TAG, "Reading characteristic from UUID....");
        if (gatt.getService(serviceUuid) == null) {
            Log.e(TAG, "Service is null");
        }
        BluetoothGattCharacteristic characteristic =
                gatt.getService(serviceUuid) != null
                        ? gatt.getService(serviceUuid).getCharacteristic(charUuid)
                        : null;
        if (characteristic == null) {
            Log.e(TAG, "Characteristic is null");
        }
        // Check for null
        gatt.readCharacteristic(characteristic);
    }

    private void broadcastUpdate(final String action,
                                 final BluetoothGattCharacteristic characteristic) {
        Log.i(TAG, "Broadcasting update....");
        final Intent intent = new Intent(action);
        // For all other profiles, writes the data formatted in HEX.
        final byte[] data = characteristic.getValue();
        if (data != null && data.length > 0) {
            final StringBuilder stringBuilder = new StringBuilder(data.length);
            for(byte byteChar : data)
                stringBuilder.append(String.format("%02X ", byteChar));
            Log.i(TAG, stringBuilder.toString());
        }
        context.sendBroadcast(intent);
    }
}
