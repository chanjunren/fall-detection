package com.cs3237_group_3.fall_detection_app.view.adapter;

import android.bluetooth.BluetoothDevice;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.cs3237_group_3.fall_detection_app.R;

import java.util.ArrayList;

// For discovering BLE devices
public class BleDevicesAdapter extends RecyclerView.Adapter<BleDevicesAdapter.BleDeviceViewHolder> {
    private final String TAG = "BleAdapter";

    private OnBleDeviceClickedListener onBleDeviceClickedListener;
    private ArrayList<BluetoothDevice> bleDevices;

    public BleDevicesAdapter(ArrayList<BluetoothDevice> bleDevices,
                             OnBleDeviceClickedListener onBleDeviceClickedListener) {
        this.onBleDeviceClickedListener = onBleDeviceClickedListener;
        this.bleDevices = bleDevices;
    }

    @NonNull
    @Override
    public BleDevicesAdapter.BleDeviceViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        LayoutInflater inflater = LayoutInflater.from(parent.getContext());
        View v = inflater.inflate(R.layout.card_ble_device, parent, false);
        return new BleDeviceViewHolder(v, onBleDeviceClickedListener);
    }

    @Override
    public void onBindViewHolder(@NonNull BleDevicesAdapter.BleDeviceViewHolder holder, int position) {
        holder.setText(position);
        holder.itemView.setOnClickListener(v ->
                holder.onBleDeviceClickedListener.onBleDeviceSelected(position));
    }

    @Override
    public int getItemCount() {
        return bleDevices.size();
    }

    public class BleDeviceViewHolder extends RecyclerView.ViewHolder {
        TextView bleDeviceNameTv, bleDeviceMacAddTv;
        OnBleDeviceClickedListener onBleDeviceClickedListener;
        public BleDeviceViewHolder(@NonNull View itemView, OnBleDeviceClickedListener onBleDeviceClickedListener) {
            super(itemView);
            bleDeviceNameTv = itemView.findViewById(R.id.bleDeviceNameTv);
            bleDeviceMacAddTv = itemView.findViewById(R.id.bleDeviceMacAddTv);
            this.onBleDeviceClickedListener = onBleDeviceClickedListener;
        }

        void setText(int position) {
            bleDeviceNameTv.setText(bleDevices.get(position).getName());
            bleDeviceMacAddTv.setText(bleDevices.get(position).getAddress());
        }
    }

    public interface OnBleDeviceClickedListener {
        void onBleDeviceSelected(int position);
    }
}