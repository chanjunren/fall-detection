package com.cs3237_group_3.fall_detection_app;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.lifecycle.ViewModelProvider;

import android.Manifest;
import android.accessibilityservice.AccessibilityService;
import android.bluetooth.BluetoothAdapter;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Bundle;
import android.provider.Settings;
import android.text.TextUtils;
import android.util.Log;

import com.cs3237_group_3.fall_detection_app.util.WhatsappAccessibilityService;
import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;

public class MainActivity extends AppCompatActivity {
    private final String TAG = "MainActivity";
    private final static int REQUEST_ENABLE_LOCATION = 7;
    private final static int REQUEST_ENABLE_BT = 17;

    @Override
    protected void onCreate(final Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        sendwts();
    }

    protected void sendwts(){
        String smsNumber = "6596262301"; // E164 format without '+' sign
        Intent sendIntent = new Intent(Intent.ACTION_SEND);
        //  Intent sendIntent = new Intent(Intent.ACTION_SENDTO);
        sendIntent.setType("text/plain");
        sendIntent.putExtra(Intent.EXTRA_TEXT, "test n"
                + getResources().getString(R.string.whatsapp_suffix));
        sendIntent.putExtra("jid", smsNumber + "@s.whatsapp.net"); //phone number without "+" prefix
        sendIntent.setPackage("com.whatsapp");

        startActivity(sendIntent);
    }

    @Override
    protected void onResume() {
        super.onResume();
        requestBlePermission();
        requestLocationPermission();
    }
    private void requestLocationPermission() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[] {Manifest.permission.ACCESS_FINE_LOCATION},
                    REQUEST_ENABLE_LOCATION);
        }
    }

    private void requestBlePermission() {
//        Optionally, your app can also listen for the ACTION_STATE_CHANGED broadcast intent,
//        which the system broadcasts whenever the Bluetooth state changes.
//        This broadcast contains the extra fields EXTRA_STATE and EXTRA_PREVIOUS_STATE,
//        containing the new and old Bluetooth states, respectively.
//        Possible values for these extra fields are STATE_TURNING_ON, STATE_ON, STATE_TURNING_OFF, and STATE_OFF.
//        Listening for this broadcast can be useful if your app needs to detect runtime changes made to the Bluetooth state.
        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if (bluetoothAdapter == null) {
            // Device doesn't support Bluetooth
            Log.e(TAG, "Device does not support bluetooth");
        }
        if (bluetoothAdapter.isEnabled()) {
            Log.i(TAG, "Bluetooth adapter is enabled nigga");
        }
        if (!bluetoothAdapter.isEnabled()) {
            Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            startActivityForResult(enableBtIntent, REQUEST_ENABLE_BT);
        }
        if (!isAccessibilityOn(getApplicationContext(), WhatsappAccessibilityService.class)) {
            Intent intent = new Intent (Settings.ACTION_ACCESSIBILITY_SETTINGS);
            startActivity(intent);
        }
    }

    private boolean isAccessibilityOn (Context context, Class<? extends AccessibilityService> clazz) {
        int accessibilityEnabled = 0;
        final String service = context.getPackageName () + "/" + clazz.getCanonicalName ();
        try {
            accessibilityEnabled = Settings.Secure.getInt (context.getApplicationContext ().getContentResolver (), Settings.Secure.ACCESSIBILITY_ENABLED);
        } catch (Settings.SettingNotFoundException ignored) {  }

        TextUtils.SimpleStringSplitter colonSplitter = new TextUtils.SimpleStringSplitter(':');

        if (accessibilityEnabled == 1) {
            String settingValue = Settings.Secure.getString (context.getApplicationContext ().getContentResolver (), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
            if (settingValue != null) {
                colonSplitter.setString (settingValue);
                while (colonSplitter.hasNext ()) {
                    String accessibilityService = colonSplitter.next ();

                    if (accessibilityService.equalsIgnoreCase (service)) {
                        return true;
                    }
                }
            }
        }

        return false;
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable @org.jetbrains.annotations.Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_ENABLE_BT) {
            Log.i(TAG, "REQUEST_ENABLE_BT result code:  " + resultCode);
            if (resultCode != RESULT_OK) {
                requestBlePermission();
            }
        } else if (requestCode == REQUEST_ENABLE_LOCATION) {
            Log.i(TAG, "ACCESS_FINE_LOCATION result code:  " + resultCode);
            if (resultCode != RESULT_OK) {
                requestLocationPermission();
            }
        }
    }
}
