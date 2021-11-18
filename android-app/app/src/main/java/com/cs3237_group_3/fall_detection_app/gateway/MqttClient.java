package com.cs3237_group_3.fall_detection_app.gateway;

import android.content.Context;
import android.util.Log;

import androidx.lifecycle.MutableLiveData;

import com.cs3237_group_3.fall_detection_app.viewmodel.GlobalViewModel;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.DisconnectedBufferOptions;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttCallbackExtended;
import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.util.Timer;
import java.util.TimerTask;

import static com.cs3237_group_3.fall_detection_app.util.Utilities.ACTIVITY_OUTPUT_TOPIC;
import static com.cs3237_group_3.fall_detection_app.util.Utilities.WRITE_CHANNEL;

public class MqttClient {
    private final String TAG = "MqttClient";

    final String serverUri = "tcp://192.168.10.127:1883";

    String clientId = "CS3237_Group_3";
    private Timer timer;

    private final MqttAndroidClient client;
    private GlobalViewModel viewModel;
    private Context context;
    public MqttClient(Context context, GlobalViewModel viewModel) {
        client = new MqttAndroidClient(context, serverUri, clientId);
        this.viewModel = viewModel;
        this.context = context;
        initConnection(serverUri, context);
    }

    private void initConnection(String uri, Context context) {
//        String serverUri = "tcp://" + uri + ":1883";
        client.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean reconnect, String serverURI) {
                if (reconnect) {
                    Log.i(TAG, "Reconnected to : " + serverURI);
                    // Because Clean Session is true, we need to re-subscribe
                    viewModel.postMqttConnStatus(true);
                } else {
                    Log.i(TAG, "Connected to: " + serverURI);
                    viewModel.postMqttConnStatus(true);
                }
            }

            @Override
            public void connectionLost(Throwable cause) {
                Log.i(TAG, "The Connection was lost.");
                viewModel.postMqttConnStatus(false);
//                timer.cancel();
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                Log.i(TAG, "Incoming message: " + new String(message.getPayload()));
                viewModel.getActivityReceivedFromServer().postValue(new String(message.getPayload()));
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {

            }
        });
        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setUserName("testuser1");
        mqttConnectOptions.setPassword("pass".toCharArray());
        mqttConnectOptions.setCleanSession(false);
        mqttConnectOptions.setAutomaticReconnect(true);
        mqttConnectOptions.setKeepAliveInterval(1);
//        mqttConnectOptions.setCleanSession(true);

        try {
            //addToHistory("Connecting to " + serverUri);
            Log.i(TAG, "Attempting to connect...");
            client.connect(mqttConnectOptions, context, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    DisconnectedBufferOptions disconnectedBufferOptions = new DisconnectedBufferOptions();
                    disconnectedBufferOptions.setBufferEnabled(true);
                    disconnectedBufferOptions.setBufferSize(100);
                    disconnectedBufferOptions.setPersistBuffer(false);
                    disconnectedBufferOptions.setDeleteOldestMessages(false);
                    client.setBufferOpts(disconnectedBufferOptions);
                    subscribeToTopic();
                    publishMessage("hello");
                    viewModel.postMqttConnStatus(true);
                    periodicWrite();
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Log.e(TAG, "Failed to connect to: " + serverUri);
                    Log.e(TAG, exception.toString());
//                    addToHistory();
                    viewModel.postMqttConnStatus(false);
                }

            });


        } catch (MqttException ex){
            ex.printStackTrace();
        }
    }

    public void subscribeToTopic(){
        try {
            client.subscribe(ACTIVITY_OUTPUT_TOPIC, 0, context, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    Log.i(TAG, "Subscribed successfully!");
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
//                    addToHistory("Failed to subscribe");
                    Log.e(TAG, "Failed to subscribe!");
                }

            });

        } catch (MqttException e){
            Log.e(TAG, "Subscribe error: " + e.toString());
        }
    }
//
    public void periodicWrite() {
        timer = new Timer();

        timer.schedule( new TimerTask() {
            public void run() {
                // do your work
                publishMessage("Message to keep client alive");
            }
        }, 0, 1*1000);
    }

    public void publishMessage(String publishMessage){

        try {
            MqttMessage message = new MqttMessage();
            message.setPayload(publishMessage.getBytes());
            client.publish(WRITE_CHANNEL, message);
//            if(!lient.isConnected()){
//                addToHistory(mqttAndroidClient.getBufferedMessageCount() + " messages in buffer.");
//            }
        } catch (MqttException e) {
            System.err.println("Error Publishing: " + e.getMessage());
            e.printStackTrace();
        }
    }
}

