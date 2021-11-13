package com.cs3237_group_3.fall_detection_app.viewmodel;

import android.app.Application;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothManager;
import android.content.Context;

import androidx.annotation.NonNull;
import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;

import com.cs3237_group_3.fall_detection_app.gateway.BleManager;
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.repository.AppRepository;

public class GlobalViewModel extends AndroidViewModel {
    private AppRepository appRepository;
    private BleManager bleManager;

    public GlobalViewModel(@NonNull Application application) {
        super(application);
        appRepository = new AppRepository(application);
    }

    public void initBleServices(BluetoothManager bluetoothManager, Context context) {
        this.bleManager = new BleManager(bluetoothManager, context);
    }

    public void connectToSensorTags(String wristMacAdd, String waistMacAdd) {
        bleManager.connectToSensorTags(wristMacAdd, waistMacAdd);
    }

    public BleManager getBleManager() {
        return bleManager;
    }

    public void insertConfigurationDataIntoRepo(ConfigurationData configurationData) {
        appRepository.insertConfigDataIntoDao(configurationData);
    }

    public void deleteConfigurationDataFromRepo(ConfigurationData configurationData) {
        appRepository.deleteConfigDataInDao(configurationData);
    }

    public void updateConciergeConfigurationInRepo(ConfigurationData configurationData) {
        appRepository.updateConfigDataInDao(configurationData);
    }

    public LiveData<ConfigurationData> getConfigurationLiveDataFromRepo() {
        return appRepository.getConciergeConfigFromDao();
    }
}
