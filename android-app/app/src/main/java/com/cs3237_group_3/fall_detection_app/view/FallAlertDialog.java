package com.cs3237_group_3.fall_detection_app.view;

import android.app.Dialog;
import android.app.NotificationManager;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.NotificationCompat;
import androidx.fragment.app.DialogFragment;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;

import android.os.CountDownTimer;
import android.os.Message;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.cs3237_group_3.fall_detection_app.R;
import com.cs3237_group_3.fall_detection_app.model.ConfigurationData;
import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;
import com.google.android.material.dialog.MaterialAlertDialogBuilder;

import org.jetbrains.annotations.NotNull;

public class FallAlertDialog extends DialogFragment {
    private final String TAG = "FallAlertDialog";
    private final static String default_notification_channel_id = "default" ;
    private String contactNumber;
    NavController navController;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @NonNull
    @NotNull
    @Override
    public Dialog onCreateDialog(@Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        MaterialAlertDialogBuilder dialogBuilder = new MaterialAlertDialogBuilder(getActivity());
        LayoutInflater inflater = requireActivity().getLayoutInflater();
        View view = inflater.inflate(R.layout.dialog_fall_alert, null);
        GlobalViewModel viewModel = new ViewModelProvider(this).get(GlobalViewModel.class);
        final Observer<ConfigurationData> contactObs = config -> {
            if (config == null) {
                Log.e(TAG, "config is null");
                return;
            }
            Log.i(TAG, "contactNumber set to " + config.getEmergencyContact());
            this.contactNumber = config.getEmergencyContact();
        };
        viewModel.getConfigurationLiveDataFromRepo().observe(getActivity(),
                contactObs);
//        NavController navController = Navigation.findNavController(getView());
        dialogBuilder
                .setTitle("A fall has been detected!")
                .setView(view)
                .setPositiveButton("I'm okay!", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface dialog, int which) {
                        dialog.cancel();
//                        navController.navigate(R.id.action_fallAlertDialog_to_homeFragment);
                    }
                });
        Dialog dialog = dialogBuilder.create();

        TextView timerTv = (TextView) view.findViewById(R.id.timerTv);
        CountDownTimer timer = new CountDownTimer(10000, 1000) {
            @Override
            public void onTick(long millisUntilFinished) {
                timerTv.setText(String.format("Distress message will be sent in %d",
                        millisUntilFinished / 1000));
            }

            @Override
            public void onFinish() {
                 sendwts();
                 notification();
                 dialog.cancel();
            }
        };
        timer.start();
        return dialog;
    }

    private void notification() {
        Uri alarmSound = RingtoneManager. getDefaultUri (RingtoneManager. TYPE_NOTIFICATION);
        NotificationCompat.Builder mBuilder =
                new NotificationCompat.Builder(getContext(),
                        default_notification_channel_id )
                        .setSmallIcon(R.drawable. ic_launcher_foreground )
                        .setVibrate( new long []{ 1000 , 1000 , 1000 , 1000 , 1000 })
                        .setContentTitle( "A Fall Has Been Detected!" )
                        .setSound(alarmSound)
                        .setContentText( "Are you okay?" ) ;
        NotificationManager mNotificationManager = (NotificationManager)
                getContext().getSystemService(Context.NOTIFICATION_SERVICE);
        mNotificationManager.notify(( int ) System.currentTimeMillis(), mBuilder.build());
    }

    protected void sendwts(){
        Intent sendIntent = new Intent(Intent.ACTION_SEND);
        //  Intent sendIntent = new Intent(Intent.ACTION_SENDTO);
        Log.i(TAG, contactNumber);
        sendIntent.setType("text/plain");
        sendIntent.putExtra(Intent.EXTRA_TEXT, "A fall has been detected"
                + getResources().getString(R.string.whatsapp_suffix));
        sendIntent.putExtra("jid", contactNumber + "@s.whatsapp.net"); //phone number without "+" prefix
        sendIntent.setPackage("com.whatsapp");
        startActivity(sendIntent);
    }
}