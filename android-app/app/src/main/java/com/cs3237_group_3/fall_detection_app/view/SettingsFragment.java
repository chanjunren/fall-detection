package com.cs3237_group_3.fall_detection_app.view;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.constraintlayout.widget.ConstraintLayout;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.cs3237_group_3.fall_detection_app.R;
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;

import org.jetbrains.annotations.NotNull;

public class SettingsFragment extends Fragment {
    private final String TAG = "SettingsFragment";

    private NavController navController;

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
        navController = Navigation.findNavController(view);

        TextView wristTagTv = view.findViewById(R.id.wristSensorMacAddTv);
        TextView waistTagTv = view.findViewById(R.id.waistSensorMacAddTv);
        TextView serverTv = view.findViewById(R.id.serverAddTv);
        TextView contactTv = view.findViewById(R.id.emergencyContactTv);
        final Observer<ConfigurationData> configObserver = config -> {
            if (config == null) {
                Log.e(TAG, "ConfigurationData is null");
                return;
            }
            wristTagTv.setText(config.getWristSensorMacAdd());
            waistTagTv.setText(config.getWaistSensorMacAdd());
            serverTv.setText(config.getServerIp());
            contactTv.setText(config.getEmergencyContact());
        };
        viewModel.getConfigurationLiveDataFromRepo().observe(getViewLifecycleOwner(),
                configObserver);

        ConstraintLayout configWristTagBtn = view.findViewById(R.id.configWristTagBtn);
        ConstraintLayout configWaistTagBtn = view.findViewById(R.id.configWaistTagBtn);
        ConstraintLayout configServerAddBtn = view.findViewById(R.id.configServerAddBtn);
        ConstraintLayout configContactBtn = view.findViewById(R.id.configContactBtn);

        configServerAddBtn.setOnClickListener(v ->
                navController.navigate(R.id.action_homeFragment_to_editServerFragment));

        configContactBtn.setOnClickListener(v ->
                navController.navigate(R.id.action_homeFragment_to_editContactFragment));
    }
}