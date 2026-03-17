package com.safeandsound.signals

import android.app.NotificationManager
import android.app.usage.UsageStatsManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import java.text.SimpleDateFormat
import java.util.*

class SignalCollector(private val context: Context) {

    fun collectScreenActivity(): Int {
        // Use UsageStatsManager. Query last 30 minutes. Return total minutes of screen-on time.
        // Requires PACKAGE_USAGE_STATS permission
        // Mocking for MVP framework:
        return 12 
    }

    fun collectMovement(): String {
        // ActivityRecognitionClient (Google Play Services)
        // Requires ACTIVITY_RECOGNITION
        // STILL / WALKING / RUNNING / IN_VEHICLE
        return "STILL"
    }

    fun collectLastInteraction(): String {
        // UsageStatsManager last event time
        // Never return which app was used
        val df = SimpleDateFormat("HH:mm", Locale.getDefault())
        return df.format(Date())
    }

    fun collectBattery(): Pair<Int, Boolean> {
        val batteryStatus = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: 100
        val status = batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || status == BatteryManager.BATTERY_STATUS_FULL
        return Pair(level, isCharging)
    }

    fun collectNetwork(): String {
        val cm = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val activeNetwork = cm.activeNetwork ?: return "NONE"
        val caps = cm.getNetworkCapabilities(activeNetwork) ?: return "NONE"
        return when {
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WIFI"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "MOBILE"
            else -> "NONE"
        }
    }

    fun collectDND(): Boolean {
        val nm = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        return nm.currentInterruptionFilter != NotificationManager.INTERRUPTION_FILTER_ALL
    }
}
