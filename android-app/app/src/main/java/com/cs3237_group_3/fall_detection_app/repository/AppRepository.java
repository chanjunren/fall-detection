package com.cs3237_group_3.fall_detection_app.repository;

import android.app.Application;
import android.util.Log;

import androidx.lifecycle.LiveData;

import com.cs3237_group_3.fall_detection_app.db.ConfigurationDataDao;
import com.cs3237_group_3.fall_detection_app.db.FallDetectionDb;
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;

public class AppRepository {
    private final String TAG = "AppRepository";

    private ConfigurationDataDao configurationDataDao;
    private LiveData<ConfigurationData> configurationDataLiveData;

    public AppRepository(Application application) {
        FallDetectionDb db = FallDetectionDb.getDatabase(application);
        configurationDataDao = db.configDataDao();

        configurationDataLiveData = configurationDataDao.getConfigurationDataFromDb();
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

    public LiveData<ConfigurationData> getConciergeConfigFromDao() {
//        if (conciergeConfiguration == null) {
//            conciergeConfiguration = conciergeConfigDao.getConciergConfigurationFromDb();
//        }
        if (configurationDataLiveData.getValue() == null) {
            insertDefaultConfigurationIntoDao();
        }
        return configurationDataLiveData;
    }

    private void insertDefaultConfigurationIntoDao() {
        String DEFAULT_GREETING_MSG = "Hi! I'm Temi, how can I help you today?";
        ConfigurationData defaultConfig = new ConfigurationData("WAIST_DAG_DEFAULT_ADD",
                "WRIST_DAG_DEFAULT_ADD", "127.0.0.1", "6592301048");
        insertConfigDataIntoDao(defaultConfig);
    }
}
