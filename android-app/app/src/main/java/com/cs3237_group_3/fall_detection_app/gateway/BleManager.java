package com.cs3237_group_3.fall_detection_app.gateway;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.BluetoothLeScanner;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanFilter;
import android.bluetooth.le.ScanResult;
import android.bluetooth.le.ScanSettings;
import android.os.ParcelUuid;
import android.util.Log;

import java.util.Collections;
import java.util.List;

import static com.cs3237_group_3.fall_detection_app.util.Utilities.CC2650_DATA_UUID;

public class BleManager {
    private final String TAG = "BleManager";
    private BluetoothLeScanner bleScanner;
    private ScanCallback scanCallback;
    private boolean isScanning;
    public BleManager(BluetoothManager bluetoothManager, ScanCallback scanCallback) {
        this.bleScanner = bluetoothManager.getAdapter().getBluetoothLeScanner();
        this.scanCallback = scanCallback;
        this.isScanning = false;
    }

    // Notable errors
        // 1. scanning too frequently => scanning cannot exceed 30 seconds
            // if need scan for longer need to stop then start again
        // 2. SCAN_FAILED_APPLICATION_REGISTRATION_FAILED
            // disable / re-enable bluetooth OR ask users reboot android device

    public void startBleScan() {
        ScanFilter filter = new ScanFilter.Builder().setServiceUuid(
            ParcelUuid.fromString(CC2650_DATA_UUID)
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
        isScanning = true;
    }

    public void stopBleScan() {
        Log.i(TAG, "Stopping scan...");
        bleScanner.stopScan(scanCallback);
        isScanning = false;
    }
}
