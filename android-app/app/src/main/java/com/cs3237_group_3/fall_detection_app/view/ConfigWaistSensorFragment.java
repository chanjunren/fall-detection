package com.cs3237_group_3.fall_detection_app.view;

import android.bluetooth.BluetoothManager;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.content.Context;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ImageView;

import com.baoyz.widget.PullRefreshLayout;
import com.cs3237_group_3.fall_detection_app.R;
import com.cs3237_group_3.fall_detection_app.gateway.BleManager;
import com.cs3237_group_3.fall_detection_app.view.adapter.BleDevicesAdapter;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;


public class ConfigWaistSensorFragment extends Fragment
        implements BleDevicesAdapter.OnBleDeviceClickedListener {
    private final String TAG = "ConfigWaistSensorFragment";
    private BleManager bleManager;
    private ScanCallback scanCallback;
    private RecyclerView bleDevicesRv;
    private PullRefreshLayout pullRefreshLayout;
    private ArrayList<String> availableBleDevices;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        availableBleDevices = new ArrayList<>();
        return inflater.inflate(R.layout.fragment_config_waist_sensor, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view, @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        BluetoothManager bluetoothManager = (BluetoothManager)
                getActivity().getSystemService((Context.BLUETOOTH_SERVICE));
        initBleCallBack();
        bleManager = new BleManager(bluetoothManager, scanCallback);

        bleDevicesRv = view.findViewById(R.id.discoveredBleDevicesRv);
        initializeRecylerView();
        pullRefreshLayout = view.findViewById(R.id.refreshLayout);

        // listen refresh event
        pullRefreshLayout.setOnRefreshListener(() -> {
            // start refresh
            Log.i(TAG, "Refresh called");
            pullRefreshLayout.setRefreshing(false);
        });
        NavController navController = Navigation.findNavController(view);

        ImageView backBtn = view.findViewById(R.id.backBtn);
        backBtn.setOnClickListener(v ->
                navController.navigate(R.id.action_configWaistSensorFragment_to_homeFragment));

        bleManager.startBleScan();
    }

    @Override
    public void onStop() {
        super.onStop();
        bleManager.stopBleScan();
    }

    private void initializeRecylerView() {
        BleDevicesAdapter bleDevicesAdapter = new BleDevicesAdapter(availableBleDevices, this);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity());
        bleDevicesRv.setAdapter(bleDevicesAdapter);
        bleDevicesRv.setLayoutManager(mLayoutManager);
    }

    private void initBleCallBack() {
        scanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                super.onScanResult(callbackType, result);
                Log.i(TAG, String.format("Detected: %s | %s\n",
                        result.getDevice().getAddress(), result.getDevice().getName()));
            }

            @Override
            public void onBatchScanResults(List<ScanResult> results) {
                super.onBatchScanResults(results);
                for (ScanResult result: results) {
                    Log.i(TAG, String.format("Detected: %s | %s\n",
                            result.getDevice().getAddress(), result.getDevice().getName()));
                }
            }

            @Override
            public void onScanFailed(int errorCode) {
                super.onScanFailed(errorCode);
                Log.e(TAG, "ScanCallBack error code: "  + errorCode);
            }
        };
    }

    @Override
    public void onBleDeviceSelected(int position) {
        Log.i(TAG, availableBleDevices.get(position) + " selected");
    }
}