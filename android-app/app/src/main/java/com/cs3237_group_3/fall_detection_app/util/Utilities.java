package com.cs3237_group_3.fall_detection_app.util;

import java.util.UUID;

public class Utilities {
    public static final UUID CC2650_CCCD_UUID =
            UUID.fromString("00002902-0000-1000-8000-00805f9b34fb");

    public static final UUID CC2650_SERVICE_UUID =
            UUID.fromString("f000aa80-0451-4000-b000-000000000000");
    public static final UUID CC2650_DATA_UUID =
            UUID.fromString("f000aa81-0451-4000-b000-000000000000");

    public static final UUID CC2650_MOVEMENT_CONF_UUID =
            UUID.fromString("f000aa82-0451-4000-b000-000000000000");
    public static final UUID BATT_SERVICE_UUID =
            UUID.fromString("0000180f-0000-1000-8000-00805f9b34fb");
    public static final UUID BATT_LEVEL_CHAR_UUID =
            UUID.fromString("00002a19-0000-1000-8000-00805f9b34fb");

    public static final String CC2650_MOVEMENT_SERV_UUID_STRING = "f000aa80-0451-4000-b000-000000000000";
    public static final String CC2650_MOVEMENT_DATA_UUID_STRING = "f000aa81-0451-4000-b000-000000000000";
    public static final String CC2650_MOVEMENT_CONF_UUID_STRING = "f000aa82-0451-4000-b000-000000000000";
    public static final String BATT_SERVICE_UUID_STRING = "0000180f-0000-1000-8000-00805f9b34fb";
    public static final String BATT_LEVEL_CHAR_STRING = "00002a19-0000-1000-8000-00805f9b34fb";

    public static final String BLE_READING_TOPIC = "ble_data";
    public static final String ACTIVITY_OUTPUT_TOPIC = "test123";
    public static final String WRITE_CHANNEL = "test456";
    public static final String FALL_DETECTION_MSG = "fall!";
}
