package com.robosolutions.fall_detection_app.viewmodel;

import android.app.Application;

import androidx.annotation.NonNull;
import androidx.lifecycle.AndroidViewModel;

import com.robosolutions.fall_detection_app.model.ConfigurationData;
import com.robosolutions.fall_detection_app.repository.AppRepository;

public class GlobalViewModel extends AndroidViewModel {
    private AppRepository appRepository;
    public GlobalViewModel(@NonNull Application application) {
        super(application);
        appRepository = new AppRepository(application);
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
}
