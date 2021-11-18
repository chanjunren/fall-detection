package com.cs3237_group_3.fall_detection_app.view;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothGattCallback;
import android.bluetooth.BluetoothManager;
import android.content.Context;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.cs3237_group_3.fall_detection_app.gateway.BleManager;
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;
import com.google.android.material.card.MaterialCardView;
import com.cs3237_group_3.fall_detection_app.R;
import com.wang.avi.AVLoadingIndicatorView;

import org.jetbrains.annotations.NotNull;

import at.markushi.ui.CircleButton;

public class DashboardFragment extends Fragment
        implements View.OnClickListener {
    private final String TAG = "DashboardFragment";
    private GlobalViewModel viewModel;
    private BleManager bleManager;
    private ConfigurationData configurationData;
    private String serverUri;

    private AVLoadingIndicatorView wristSensorLiv, waistSensorLiv, serverLiv, activityLiv;
    private MaterialCardView wristSensorConnCard, waistSensorConnCard,
            serverConnCard, activityStatusCard;
    private TextView wristSensorConnTv, waistSensorConnTv, serverConnTv, activityStatusTv;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_dashboard, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view,
                              @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        viewModel = new ViewModelProvider(this).get(GlobalViewModel.class);
        viewModel.initBleServices(
                (BluetoothManager) getActivity().getSystemService(Context.BLUETOOTH_SERVICE),
                getContext());
        bleManager = viewModel.getBleManager();
        initObservers();

        wristSensorLiv = view.findViewById(R.id.wristSensorLiv);
        wristSensorConnCard = view.findViewById(R.id.wristSensorConnCard);
        wristSensorConnTv = view.findViewById(R.id.wristSensorConnTv);
        CircleButton refreshWristSensorBtn = view.findViewById(R.id.refreshWristSensorBtn);
        refreshWristSensorBtn.setOnClickListener(this);

        waistSensorLiv = view.findViewById(R.id.waistSensorLiv);
        waistSensorConnCard = view.findViewById(R.id.waistSensorConnCard);
        waistSensorConnTv = view.findViewById(R.id.waistSensorConnTv);
        CircleButton refreshWaistSensorBtn = view.findViewById(R.id.refreshWaistSensorBtn);
        refreshWaistSensorBtn.setOnClickListener(this);

        serverLiv = view.findViewById(R.id.serverLiv);
        serverConnCard = view.findViewById(R.id.serverConnCard);
        serverConnTv = view.findViewById(R.id.serverConnTv);
        CircleButton refreshServerConnBtn = view.findViewById(R.id.refreshServerConnBtn);
        refreshServerConnBtn.setOnClickListener(this);

        activityStatusCard = view.findViewById(R.id.activityStatusCard);
        activityStatusTv = view.findViewById(R.id.activityStatusTv);
    }

    private void initObservers() {
        final Observer<ConfigurationData> configObserver = config -> {
            if (config == null) {
                Log.e(TAG, "ConfigurationData is null");
                return;
            }
            serverUri = config.getServerIp();
            viewModel.initMqttService(getActivity().getApplicationContext(), serverUri);
            bleManager.connectToSensorTags(config.getWristSensorMacAdd(), config.getWaistSensorMacAdd());
        };
        viewModel.getConfigurationLiveDataFromRepo().observe(getViewLifecycleOwner(),
                configObserver);
        final Observer<Boolean> wristTagConnStatusObserver = wristTagConnRes -> {
            if (wristTagConnRes == null) {
                Log.e(TAG, "connRes is null");
                return;
            }
            setConnRes(wristSensorConnCard, wristSensorConnTv, wristSensorLiv, wristTagConnRes);
        };
        bleManager.getWristConnStatusLiveData().observe(getViewLifecycleOwner(),
                wristTagConnStatusObserver);

        final Observer<Boolean> waistTagConnStatusObserver = waistTagConnRes -> {
            if (waistTagConnRes == null) {
                Log.e(TAG, "connRes is null");
                return;
            }
            setConnRes(waistSensorConnCard, waistSensorConnTv, waistSensorLiv, waistTagConnRes);
        };
        bleManager.getWaistConnStatusLiveData().observe(getViewLifecycleOwner(),
                waistTagConnStatusObserver);

        final Observer<Boolean> mqttConnStatusObserver = mqttConnRes -> {
            if (mqttConnRes == null) {
                Log.e(TAG, "mqttConnRes is null");
                return;
            }
            setConnRes(serverConnCard, serverConnTv, serverLiv, mqttConnRes);
        };
        viewModel.getMqttConnLiveData().observe(getViewLifecycleOwner(),
                mqttConnStatusObserver);

        final Observer<String> activityStatusObserver = status -> {
            if (status == null) {
                Log.e(TAG, "mqttConnRes is null");
                return;
            }
            setActivityStatus(status);
        };
        viewModel.getActivityReceivedFromServer().observe(getViewLifecycleOwner(),
                activityStatusObserver);

    }

    private void setConnRes(MaterialCardView card, TextView tv,
                            AVLoadingIndicatorView liv, boolean connSuccess) {
        if (connSuccess) {
            tv.setText("Connected");
            card.setCardBackgroundColor(getResources().getColor(R.color.test_success));
        } else {
            tv.setText("Not Connected");
            card.setCardBackgroundColor(getResources().getColor(R.color.test_fail));
        }
        liv.hide();
        card.setVisibility(View.VISIBLE);
    }

    private void showLoading(MaterialCardView card, TextView tv, AVLoadingIndicatorView liv) {
        liv.setVisibility(View.VISIBLE);
        card.setVisibility(View.INVISIBLE);
        tv.setVisibility(View.VISIBLE);
    }

    private void setActivityStatus(String status) {
        activityStatusTv.setText(status);
    }

    @Override
    public void onClick(View v) {
        // For refresh buttons
        if (v.getId() == R.id.refreshWristSensorBtn) {
            showLoading(wristSensorConnCard, wristSensorConnTv, wristSensorLiv);
            bleManager.refreshConnectionForWristTag();
        } else if (v.getId() == R.id.refreshWaistSensorBtn) {
            showLoading(waistSensorConnCard, waistSensorConnTv, waistSensorLiv);
            bleManager.refreshConnectionForWaistTag();
        } else if (v.getId() == R.id.refreshServerConnBtn) {
            showLoading(serverConnCard, serverConnTv, serverLiv);
            viewModel.initMqttService(getActivity().getApplicationContext(), serverUri);
        }
    }


}