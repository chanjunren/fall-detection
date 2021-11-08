package com.cs3237_group_3.fall_detection_app.view;

import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import com.google.android.material.card.MaterialCardView;
import com.cs3237_group_3.fall_detection_app.R;
import com.wang.avi.AVLoadingIndicatorView;

import org.jetbrains.annotations.NotNull;

import at.markushi.ui.CircleButton;

public class DashboardFragment extends Fragment implements View.OnClickListener {
    private final String TAG = "DashboardFragment";
    private AVLoadingIndicatorView wristSensorLiv, waistSensorLiv, serverLiv;
    private MaterialCardView wristSensorConnCard, waistSensorConnCard, serverConnCard;
    private TextView wristSensorConnTv, waistSensorConnTv, serverConnTv;

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_dashboard, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view, @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        wristSensorLiv = view.findViewById(R.id.wristSensorLiv);
        wristSensorConnCard = view.findViewById(R.id.wristSensorConnCard);
        wristSensorConnTv = view.findViewById(R.id.wristSensorConnTv);
        CircleButton refreshWristSensorBtn = view.findViewById(R.id.refreshWristSensorBtn);
        refreshWristSensorBtn.setOnClickListener(this);

        waistSensorLiv = view.findViewById(R.id.waistSensorLiv);
        waistSensorConnCard = view.findViewById(R.id.waistSensorConnCard);
        waistSensorConnTv = view.findViewById(R.id.waistSensorConnTv);
        CircleButton refreshWaistSensorBtn = view.findViewById(R.id.refreshWaistSensorBtn);
        refreshWaistSensorBtn.setOnClickListener(this);

        serverLiv = view.findViewById(R.id.serverLiv);
        serverConnCard = view.findViewById(R.id.serverConnCard);
        serverConnTv = view.findViewById(R.id.serverConnTv);
        CircleButton refreshServerConnBtn = view.findViewById(R.id.refreshServerConnBtn);
        refreshServerConnBtn.setOnClickListener(this);
    }

    private void setConnRes(MaterialCardView card, TextView tv, boolean connSuccess) {
        if (connSuccess) {
            tv.setText("Connected");
            card.setCardBackgroundColor(getResources().getColor(R.color.test_success));
        } else {
            tv.setText("Not Connected");
            card.setCardBackgroundColor(getResources().getColor(R.color.test_fail));
        }
        card.setVisibility(View.VISIBLE);
    }

    @Override
    public void onClick(View v) {
        // For refresh buttons
        if (v.getId() == R.id.refreshWristSensorBtn) {
            wristSensorLiv.hide();
            setConnRes(wristSensorConnCard, wristSensorConnTv, true);
        } else if (v.getId() == R.id.refreshWaistSensorBtn) {
            waistSensorLiv.hide();
            setConnRes(waistSensorConnCard, waistSensorConnTv, true);
        } else if (v.getId() == R.id.refreshServerConnBtn) {
            serverLiv.hide();
            setConnRes(serverConnCard, serverConnTv, false);
        }
    }
}