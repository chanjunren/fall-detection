package com.cs3237_group_3.fall_detection_app.view;

import android.graphics.Color;
import android.os.Bundle;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.navigation.NavController;
import androidx.navigation.Navigation;
import androidx.viewpager.widget.ViewPager;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import com.cs3237_group_3.fall_detection_app.R;
import com.cs3237_group_3.fall_detection_app.view.adapter.HomePageAdapter;

import org.jetbrains.annotations.NotNull;

import java.util.ArrayList;

import devlight.io.library.ntb.NavigationTabBar;

import static androidx.fragment.app.FragmentPagerAdapter.BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT;

public class HomeFragment extends Fragment {
@Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        // Inflate the layout for this fragment
        return inflater.inflate(R.layout.fragment_home, container, false);
    }

    @Override
    public void onViewCreated(@NonNull @NotNull View view, @Nullable @org.jetbrains.annotations.Nullable Bundle savedInstanceState) {
        super.onViewCreated(view, savedInstanceState);
        initTabsAndViewPager(view);
//        NavController navController = Navigation.findNavController(view);
//        navController.navigate(R.id.action_homeFragment_to_fallAlertDialog);
    }

    private void initTabsAndViewPager(View view) {
        final ViewPager viewPager = (ViewPager) view.findViewById(R.id.vp_vertical_ntb);
        viewPager.setAdapter(new HomePageAdapter(getChildFragmentManager(),
                BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT));

        final String[] colors = getResources().getStringArray(R.array.medical_express);

        final NavigationTabBar navigationTabBar = (NavigationTabBar) view.findViewById(R.id.ntb_vertical);
        final ArrayList<NavigationTabBar.Model> models = new ArrayList<>();
        models.add(
                new NavigationTabBar.Model.Builder(
                        getResources().getDrawable(R.drawable.ic_home),
                        Color.parseColor(colors[0]))
                        .title("ic_first")
                        .selectedIcon(getResources().getDrawable(R.drawable.ic_home))
                        .build()
        );
        models.add(
                new NavigationTabBar.Model.Builder(
                        getResources().getDrawable(R.drawable.ic_settings),
                        Color.parseColor(colors[1]))
                        .selectedIcon(getResources().getDrawable(R.drawable.ic_settings))
                        .title("ic_second")
                        .build()
        );
        models.add(
                new NavigationTabBar.Model.Builder(
                        getResources().getDrawable(R.drawable.ic_first),
                        Color.parseColor(colors[2]))
                        .selectedIcon(getResources().getDrawable(R.drawable.ic_first))
                        .title("ic_third")
                        .build()
        );
//        models.add(
//                new NavigationTabBar.Model.Builder(
//                        getResources().getDrawable(R.drawable.ic_fourth),
//                        Color.parseColor(colors[3]))
//                        .selectedIcon(getResources().getDrawable(R.drawable.ic_eighth))
//                        .title("ic_fourth")
//                        .build()
//        );
//        models.add(
//                new NavigationTabBar.Model.Builder(
//                        getResources().getDrawable(R.drawable.ic_fifth),
//                        Color.parseColor(colors[4]))
//                        .selectedIcon(getResources().getDrawable(R.drawable.ic_eighth))
//                        .title("ic_fifth")
//                        .build()
//        );
//        models.add(
//                new NavigationTabBar.Model.Builder(
//                        getResources().getDrawable(R.drawable.ic_sixth),
//                        Color.parseColor(colors[5]))
//                        .selectedIcon(getResources().getDrawable(R.drawable.ic_eighth))
//                        .title("ic_sixth")
//                        .build()
//        );
//        models.add(
//                new NavigationTabBar.Model.Builder(
//                        getResources().getDrawable(R.drawable.ic_seventh),
//                        Color.parseColor(colors[6]))
//                        .selectedIcon(getResources().getDrawable(R.drawable.ic_eighth))
//                        .title("ic_seventh")
//                        .build()
//        );
//        models.add(
//                new NavigationTabBar.Model.Builder(
//                        getResources().getDrawable(R.drawable.ic_eighth),
//                        Color.parseColor(colors[7]))
//                        .selectedIcon(getResources().getDrawable(R.drawable.ic_eighth))
//                        .title("ic_eighth")
//                        .build()
//        );

        navigationTabBar.setModels(models);
        navigationTabBar.setViewPager(viewPager, 4);
    }

}