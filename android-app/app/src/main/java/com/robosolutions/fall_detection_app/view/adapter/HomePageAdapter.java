package com.robosolutions.fall_detection_app.view.adapter;

import android.content.Context;
import androidx.annotation.NonNull;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.fragment.app.FragmentStatePagerAdapter;
import com.robosolutions.fall_detection_app.view.AboutFragment;
import com.robosolutions.fall_detection_app.view.DashboardFragment;
import com.robosolutions.fall_detection_app.view.SettingsFragment;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;

public class HomePageAdapter extends FragmentStatePagerAdapter {
    private ArrayList<Fragment> homeTabs;

    public HomePageAdapter(@NonNull @NotNull FragmentManager fm, int behavior) {
        super(fm, behavior);
        homeTabs = new ArrayList<>();
        homeTabs.add(new DashboardFragment());
        homeTabs.add(new SettingsFragment());
        homeTabs.add(new AboutFragment());


    }

    @Override
    public int getCount() {
        return homeTabs.size();
    }

    @Override
    public Fragment getItem(int position) {
        return homeTabs.get(position);
    }

//    @Override
//    public Object instantiateItem(final ViewGroup container, final int position) {
//        final View view = LayoutInflater.from(
//                baseContext).inflate(R.layout.item_vp, null, false);
//
//        final TextView txtPage = (TextView) view.findViewById(R.id.txt_vp_item_page);
//        txtPage.setText(String.format("Page #%d", position));
//
//        container.addView(view);
//        return view;
//    }
}
