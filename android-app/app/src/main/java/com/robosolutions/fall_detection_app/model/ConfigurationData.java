package com.robosolutions.fall_detection_app.model;

import androidx.room.ColumnInfo;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

@Entity(tableName="configTable")
public class ConfigurationData {
    @PrimaryKey(autoGenerate = true)
    private int configIdx;
    @ColumnInfo(name = "waistSensorMacAdd")
    private String waistSensorMacAdd;
    @ColumnInfo(name = "wristSensorMacAdd")
    private String wristSensorMacAdd;
    @ColumnInfo(name = "emergencyContact")
    private String emergencyContact;

    public ConfigurationData(String waistSensorMacAdd, String wristSensorMacAdd, String emergencyContact) {
        this.waistSensorMacAdd = waistSensorMacAdd;
        this.wristSensorMacAdd = wristSensorMacAdd;
        this.emergencyContact = emergencyContact;
    }

    public int getConfigIdx() {
        return configIdx;
    }

    public void setConfigIdx(int configIdx) {
        this.configIdx = configIdx;
    }

    public String getWaistSensorMacAdd() {
        return waistSensorMacAdd;
    }

    public void setWaistSensorMacAdd(String waistSensorMacAdd) {
        this.waistSensorMacAdd = waistSensorMacAdd;
    }

    public String getWristSensorMacAdd() {
        return wristSensorMacAdd;
    }

    public void setWristSensorMacAdd(String wristSensorMacAdd) {
        this.wristSensorMacAdd = wristSensorMacAdd;
    }

    public String getEmergencyContact() {
        return emergencyContact;
    }

    public void setEmergencyContact(String emergencyContact) {
        this.emergencyContact = emergencyContact;
    }

    @Override
    public String toString() {
        return "ConfigurationData{" +
                "configIdx=" + configIdx +
                ", waistSensorMacAdd='" + waistSensorMacAdd + '\'' +
                ", wristSensorMacAdd='" + wristSensorMacAdd + '\'' +
                ", emergencyContact='" + emergencyContact + '\'' +
                '}';
    }
}
