package com.cs3237_group_3.fall_detection_app.view;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.EditText;
import android.widget.ImageView;

import com.cs3237_group_3.fall_detection_app.R;
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;

import org.jetbrains.annotations.NotNull;

import at.markushi.ui.CircleButton;

public class EditServerFragment extends Fragment {
    private final String TAG = "EditServerFragment";

    private GlobalViewModel globalViewModel;
    private ConfigurationData currentConfig;

    private EditText serverAddEt;
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_edit_server, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view, @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        NavController navController = Navigation.findNavController(view);
        globalViewModel = new ViewModelProvider(this).get(GlobalViewModel.class);
        attachLiveData();
        ImageView backBtn = view.findViewById(R.id.backBtn);
        backBtn.setOnClickListener(v ->
                navController.navigate(R.id.action_editServerFragment_to_homeFragment));

        serverAddEt = view.findViewById(R.id.serverAddEt);

        CircleButton setNewServerAddBtn = view.findViewById(R.id.setNewServerAddBtn);
        setNewServerAddBtn.setOnClickListener(v -> {
            updateServerAddress();
            backBtn.callOnClick();
        });
    }

    private void updateServerAddress() {
        currentConfig.setServerIp(serverAddEt.getText().toString());
        globalViewModel.updateConciergeConfigurationInRepo(currentConfig);
    }

    private void attachLiveData() {
        final Observer<ConfigurationData> configObserver = conConfig -> {
            this.currentConfig = conConfig;
        };
        globalViewModel.getConfigurationLiveDataFromRepo().observe(getActivity(),
                configObserver);
    }
}