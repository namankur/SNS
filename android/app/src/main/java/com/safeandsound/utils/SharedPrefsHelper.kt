package com.safeandsound.utils

import android.content.Context
import android.content.SharedPreferences

object SharedPrefsHelper {
    private const val PREF_NAME = "SafeAndSoundPrefs"
    private const val KEY_PHONE_NUMBER = "phone_number"
    private const val KEY_IS_SETUP_COMPLETE = "is_setup_complete"
    private const val KEY_LAST_ACTIVE_TIME = "last_active_time"

    fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    }

    fun savePhoneNumber(context: Context, phone: String) {
        getPrefs(context).edit().putString(KEY_PHONE_NUMBER, phone).apply()
    }

    fun getPhoneNumber(context: Context): String? {
        return getPrefs(context).getString(KEY_PHONE_NUMBER, null)
    }

    fun setSetupComplete(context: Context, isComplete: Boolean) {
        getPrefs(context).edit().putBoolean(KEY_IS_SETUP_COMPLETE, isComplete).apply()
    }

    fun isSetupComplete(context: Context): Boolean {
        return getPrefs(context).getBoolean(KEY_IS_SETUP_COMPLETE, false)
    }

    fun saveLastActiveTime(context: Context, time: Long) {
        getPrefs(context).edit().putLong(KEY_LAST_ACTIVE_TIME, time).apply()
    }

    fun getLastActiveTime(context: Context): Long {
        return getPrefs(context).getLong(KEY_LAST_ACTIVE_TIME, System.currentTimeMillis())
    }
}
