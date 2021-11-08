package com.cs3237_group_3.fall_detection_app.view;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.baoyz.widget.PullRefreshLayout;
import com.cs3237_group_3.fall_detection_app.R;
import com.cs3237_group_3.fall_detection_app.view.adapter.BleDevicesAdapter;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;


public class ConfigWaistSensorFragment extends Fragment
        implements BleDevicesAdapter.OnBleDeviceClickedListener {
    private final String TAG = "ConfigWaistSensorFragment";
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
        availableBleDevices.add("Device 1");
        availableBleDevices.add("Device 2");
        availableBleDevices.add("Device 3");
        availableBleDevices.add("Device 4");

        return inflater.inflate(R.layout.fragment_config_waist_sensor, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view, @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        bleDevicesRv = view.findViewById(R.id.discoveredBleDevicesRv);
        initializeRecylerView();
        pullRefreshLayout = view.findViewById(R.id.refreshLayout);

        // listen refresh event
        pullRefreshLayout.setOnRefreshListener(() -> {
            // start refresh
            Log.i(TAG, "Refresh called");
            pullRefreshLayout.setRefreshing(false);
        });
    }

    private void initializeRecylerView() {
        BleDevicesAdapter bleDevicesAdapter = new BleDevicesAdapter(availableBleDevices, this);
        RecyclerView.LayoutManager mLayoutManager = new LinearLayoutManager(getActivity());
        bleDevicesRv.setAdapter(bleDevicesAdapter);
        bleDevicesRv.setLayoutManager(mLayoutManager);
    }

    @Override
    public void onBleDeviceSelected(int position) {
        Log.i(TAG, availableBleDevices.get(position) + " selected");
    }
}