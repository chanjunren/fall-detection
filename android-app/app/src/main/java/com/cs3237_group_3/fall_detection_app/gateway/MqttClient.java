package com.cs3237_group_3.fall_detection_app.gateway;

import android.content.Context;
import android.util.Log;

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

public class MqttClient {
    private final String TAG = "MqttClient";

    final String serverUri = "tcp://127.0.0.1:1883";

    String clientId = "ExampleAndroidClient12312412r3";
    final String subscriptionTopic = "exampleAndroidTopic";
    final String publishTopic = "exampleAndroidPublishTopic";
    final String publishMessage = "Hello World!";

    private MqttAndroidClient client;
    public MqttClient(Context context) {
        client = new MqttAndroidClient(context, serverUri, clientId);
        initConnection(serverUri);
    }

    private void initConnection(String serverUri) {
        MqttConnectOptions options = new MqttConnectOptions();
//        options.setUserName("username");
//        options.setPassword("username".toCharArray());
        client.setCallback(new MqttCallbackExtended() {
            @Override
            public void connectComplete(boolean reconnect, String serverURI) {
                if (reconnect) {
                    Log.i(TAG, "Reconnected to : " + serverURI);
                    // Because Clean Session is true, we need to re-subscribe
                } else {
                    Log.i(TAG, "Connected to: " + serverURI);
                }
            }

            @Override
            public void connectionLost(Throwable cause) {
                Log.i(TAG, "The Connection was lost.");
            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                Log.i(TAG, "Incoming message: " + new String(message.getPayload()));
            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {

            }
        });
        MqttConnectOptions mqttConnectOptions = new MqttConnectOptions();
        mqttConnectOptions.setAutomaticReconnect(true);
        mqttConnectOptions.setCleanSession(false);

        try {
            //addToHistory("Connecting to " + serverUri);
            Log.i(TAG, "Attempting to connect...");
            client.connect(mqttConnectOptions, null, new IMqttActionListener() {
                @Override
                public void onSuccess(IMqttToken asyncActionToken) {
                    DisconnectedBufferOptions disconnectedBufferOptions = new DisconnectedBufferOptions();
                    disconnectedBufferOptions.setBufferEnabled(true);
                    disconnectedBufferOptions.setBufferSize(100);
                    disconnectedBufferOptions.setPersistBuffer(false);
                    disconnectedBufferOptions.setDeleteOldestMessages(false);
                    client.setBufferOpts(disconnectedBufferOptions);
//                    subscribeToTopic();
                }

                @Override
                public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
                    Log.e(TAG, "Failed to connect to: " + serverUri);
                    Log.e(TAG, exception.toString());
//                    addToHistory();
                }
            });


        } catch (MqttException ex){
            ex.printStackTrace();
        }

//        public void subscribeToTopic(){
//            try {
//                mqttAndroidClient.subscribe(subscriptionTopic, 0, null, new IMqttActionListener() {
//                    @Override
//                    public void onSuccess(IMqttToken asyncActionToken) {
//                        addToHistory("Subscribed!");
//                    }
//
//                    @Override
//                    public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
//                        addToHistory("Failed to subscribe");
//                    }
//                });
//
//                // THIS DOES NOT WORK!
//                mqttAndroidClient.subscribe(subscriptionTopic, 0, new IMqttMessageListener() {
//                    @Override
//                    public void messageArrived(String topic, MqttMessage message) throws Exception {
//                        // message Arrived!
//                        System.out.println("Message: " + topic + " : " + new String(message.getPayload()));
//                    }
//                });
//
//            } catch (MqttException ex){
//                System.err.println("Exception whilst subscribing");
//                ex.printStackTrace();
//            }
//        }
//
//        public void publishMessage(){
//
//            try {
//                MqttMessage message = new MqttMessage();
//                message.setPayload(publishMessage.getBytes());
//                mqttAndroidClient.publish(publishTopic, message);
//                addToHistory("Message Published");
//                if(!mqttAndroidClient.isConnected()){
//                    addToHistory(mqttAndroidClient.getBufferedMessageCount() + " messages in buffer.");
//                }
//            } catch (MqttException e) {
//                System.err.println("Error Publishing: " + e.getMessage());
//                e.printStackTrace();
//            }
//        }


    }
}

