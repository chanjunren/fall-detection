package com.cs3237_group_3.fall_detection_app.view;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.bluetooth.le.ScanCallback;
import android.bluetooth.le.ScanResult;
import android.content.Context;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;
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
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.view.adapter.BleDevicesAdapter;
import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;


public class ConfigWristSensorFragment extends Fragment
        implements BleDevicesAdapter.OnBleDeviceClickedListener {
    private final String TAG = "ConfigWristSensorFragment";
    private GlobalViewModel globalViewModel;
    private ConfigurationData configurationData;

    private BleManager bleManager;
    private ScanCallback scanCallback;

    ImageView backBtn;
    private RecyclerView bleDevicesRv;
    private BleDevicesAdapter bleDevicesAdapter;
    private PullRefreshLayout pullRefreshLayout;
    private ArrayList<BluetoothDevice> availableBleDevices;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        availableBleDevices = new ArrayList<>();
        return inflater.inflate(R.layout.fragment_config_wrist_sensor, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view, @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        globalViewModel = new ViewModelProvider(this).get(GlobalViewModel.class);
        final Observer<ConfigurationData> configObserver = config -> {
            if (config == null) {
                Log.e(TAG, "ConfigurationData is null");
                return;
            }
            this.configurationData = config;
        };
        globalViewModel.getConfigurationLiveDataFromRepo().observe(getViewLifecycleOwner(),
                configObserver);

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

        backBtn = view.findViewById(R.id.backBtn);
        backBtn.setOnClickListener(v ->
                navController.navigate(R.id.action_configWristSensorFragment_to_homeFragment));
        globalViewModel.initBleServices(
                (BluetoothManager) getActivity().getSystemService(Context.BLUETOOTH_SERVICE),
                getContext());
        bleManager = globalViewModel.getBleManager();
        initBleCallBack();
        bleManager.startBleScan(scanCallback);
    }

    @Override
    public void onResume() {
        super.onResume();
        globalViewModel.initBleServices(
                (BluetoothManager) getActivity().getSystemService(Context.BLUETOOTH_SERVICE),
                getContext());
        bleManager = globalViewModel.getBleManager();
    }

    @Override
    public void onStop() {
        super.onStop();
        bleManager.stopBleScan(scanCallback);
    }

    private void initializeRecylerView() {
        bleDevicesAdapter = new BleDevicesAdapter(availableBleDevices, this);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity());
        bleDevicesRv.setAdapter(bleDevicesAdapter);
        bleDevicesRv.setLayoutManager(mLayoutManager);
    }

    private void initBleCallBack() {
        scanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                super.onScanResult(callbackType, result);
                Optional<BluetoothDevice> query = availableBleDevices.stream()
                        .filter(device -> device.getAddress().equals(result.getDevice().getAddress()))
                        .findFirst();

                if (query.isPresent()) {
                    // Query present
//                    int queryIndex = availableBleDevices.indexOf(query.get());
//                    Log.i(TAG, "Query Index " + queryIndex);
//                    availableBleDevices.set(queryIndex, result.getDevice());
//                    bleDevicesAdapter.notifyItemChanged(queryIndex);
                } else {
//                    Log.i(TAG, String.format("Found: %s | %s\n",
//                            result.getDevice().getAddress(), result.getDevice().getName()));
                    availableBleDevices.add(result.getDevice());
                    bleDevicesAdapter.notifyItemInserted(availableBleDevices.size() - 1);
                }
            }

            @Override
            public void onBatchScanResults(List<ScanResult> results) {
                super.onBatchScanResults(results);
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
        configurationData.setWristSensorMacAdd(availableBleDevices.get(position).getAddress());
        globalViewModel.updateConciergeConfigurationInRepo(configurationData);
        backBtn.callOnClick();
    }
}