package com.robosolutions.fall_detection_app.repository;

import android.app.Application;
import android.util.Log;

import androidx.lifecycle.LiveData;

import com.robosolutions.fall_detection_app.db.ConfigurationDataDao;
import com.robosolutions.fall_detection_app.db.FallDetectionDb;
import com.robosolutions.fall_detection_app.model.ConfigurationData;

public class AppRepository {
    private final String TAG = "AppRepository";

    private ConfigurationDataDao configurationDataDao;
    private LiveData<ConfigurationData> configurationDataLiveData;

    public AppRepository(Application application) {
        FallDetectionDb db = FallDetectionDb.getDatabase(application);
        configurationDataDao = db.configDataDao();
    }

    public void insertConfigDataIntoDao(ConfigurationData configurationData) {
        FallDetectionDb.getDbExecutor().execute(() -> {
            Log.i(TAG, "Inserting: " + configurationData.toString());
            configurationDataDao.insertConfigDataIntoDb(configurationData);
        });
    }

    public void deleteConfigDataInDao(ConfigurationData configurationData) {
        FallDetectionDb.getDbExecutor().execute(() -> {
            Log.i(TAG, "Deleting: " + configurationData.toString());
            configurationDataDao.deleteConfigDataFromDb(configurationData);
        });
    }

    public void updateConfigDataInDao(ConfigurationData configurationData) {
        FallDetectionDb.getDbExecutor().execute(() -> {
            Log.i(TAG, "Updating: " + configurationData.toString());
            configurationDataDao.updateConfigDataInDb(configurationData);
        });
    }
}
