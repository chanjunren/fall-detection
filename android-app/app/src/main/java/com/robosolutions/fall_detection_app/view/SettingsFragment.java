package com.robosolutions.fall_detection_app.view;

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

import com.robosolutions.fall_detection_app.R;
import com.robosolutions.fall_detection_app.model.ConfigurationData;
import com.robosolutions.fall_detection_app.viewmodel.GlobalViewModel;

import org.jetbrains.annotations.NotNull;

public class SettingsFragment extends Fragment {
    private final String TAG = "SettingsFragment";
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_settings, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view, @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        GlobalViewModel viewModel = new ViewModelProvider(this).get(GlobalViewModel.class);
        TextView wristTagTv = view.findViewById(R.id.wristTagTv);
        TextView waistTagTv = view.findViewById(R.id.waistTagTv);
        TextView contactTv = view.findViewById(R.id.contactTv);
        final Observer<ConfigurationData> configObserver = config -> {
            if (config == null) {
                Log.e(TAG, "ConfigurationData is null");
                return;
            }
            wristTagTv.setText(config.getWristSensorMacAdd());
            waistTagTv.setText(config.getWaistSensorMacAdd());
            contactTv.setText(config.getEmergencyContact());
        };
        viewModel.getConfigurationLiveDataFromRepo().observe(getViewLifecycleOwner(),
                configObserver);

    }
}