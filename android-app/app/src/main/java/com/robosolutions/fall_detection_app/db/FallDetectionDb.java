package com.robosolutions.fall_detection_app.db;

import android.content.Context;

import androidx.annotation.NonNull;
import androidx.room.Room;
import androidx.room.RoomDatabase;
import androidx.sqlite.db.SupportSQLiteDatabase;

import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public abstract class FallDetectionDb extends RoomDatabase {

    public abstract ConfigurationDataDao configDataDao();

    private static volatile FallDetectionDb INSTANCE;
    private static final int THREAD_COUNT = 4;
    static final ExecutorService dbExecutor = Executors.newFixedThreadPool(THREAD_COUNT);

    public static FallDetectionDb getDatabase(final Context context) {
        if (INSTANCE == null) {
            INSTANCE = Room.databaseBuilder(context.getApplicationContext(), FallDetectionDb.class,
                    "FallDetectionAppDatabase").build();
        }
        return INSTANCE;
    }

    public static ExecutorService getDbExecutor() {
        return dbExecutor;
    }

    private static RoomDatabase.Callback sRoomDatabaseCallback = new RoomDatabase.Callback() {
        @Override
        public void onCreate(@NonNull SupportSQLiteDatabase db) {
            super.onCreate(db);

//            dbWriterExecutor.execute(() -> {
//                TemiTaskDao dao = INSTANCE.sequenceDao();
//                dao.deleteAll();
//
//                // Can add some default words
//                Word word = new Word("Hello");
//                dao.insert(word);
//                word = new Word("World");
//                dao.insert(word);
//            });
        }
    };
}
