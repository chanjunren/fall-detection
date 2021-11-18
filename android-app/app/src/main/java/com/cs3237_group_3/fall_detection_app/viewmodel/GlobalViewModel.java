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
import com.cs3237_group_3.fall_detection_app.gateway.MqttClient;
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.repository.AppRepository;

public class GlobalViewModel extends AndroidViewModel {
    private AppRepository appRepository;
    private BleManager bleManager;
    private MqttClient mqttClient;

    private MutableLiveData<Boolean> isMqttConnected;
    private MutableLiveData<String> activityReceivedFromServer;

    public GlobalViewModel(@NonNull Application application) {
        super(application);
        appRepository = new AppRepository(application);
        isMqttConnected = new MutableLiveData<>(false);
        activityReceivedFromServer = new MutableLiveData<>("");
    }

    public void initMqttService(Context context) {
        mqttClient = new MqttClient(context, this);
    }

    public void initBleServices(BluetoothManager bluetoothManager, Context context) {
        this.bleManager = new BleManager(bluetoothManager, context);
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

    public MutableLiveData<Boolean> getMqttConnLiveData() {
        return isMqttConnected;
    }

    public void postMqttConnStatus(boolean isMqttConnected) {
        this.isMqttConnected.postValue(isMqttConnected);
    }

    public MutableLiveData<String> getActivityReceivedFromServer() {
        return activityReceivedFromServer;
    }

    public void postActivityStatus(String status) {
        this.activityReceivedFromServer.postValue(status);
    }
}
