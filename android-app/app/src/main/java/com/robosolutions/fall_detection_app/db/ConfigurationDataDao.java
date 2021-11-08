package com.robosolutions.fall_detection_app.db;
import androidx.lifecycle.LiveData;
import androidx.room.Dao;
import androidx.room.Delete;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;
import androidx.room.Update;

import com.robosolutions.fall_detection_app.model.ConfigurationData;

@Dao
public interface ConfigurationDataDao {
    @Insert(onConflict = OnConflictStrategy.IGNORE)
    void insertConfigDataIntoDb(ConfigurationData configurationData);

    @Delete
    void deleteConfigDataFromDb(ConfigurationData configurationData);

    @Update
    void updateConfigDataInDb(ConfigurationData configurationData);

    @Query("SELECT * from configtable LIMIT 1")
    public LiveData<ConfigurationData> getConfigurationDataFromDb();
}
