package com.safeandsound.signals

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.media.AudioManager
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import android.os.BatteryManager
import android.os.PowerManager
import android.app.usage.UsageEvents
import android.app.usage.UsageStatsManager
import kotlinx.coroutines.*
import com.safeandsound.api.RetrofitClient
import com.safeandsound.api.SignalPacket
import com.safeandsound.utils.SharedPrefsHelper
import java.text.SimpleDateFormat
import java.util.*

class SignalCollector(private val context: Context) {
    
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + job)
    
    fun startCollecting() {
        scope.launch {
            while (isActive) {
                collectAndSend()
                delay(5 * 60 * 1000L) // 5 minutes
            }
        }
    }
    
    fun stopCollecting() {
        job.cancel()
    }
    
    private suspend fun collectAndSend() {
        val phone = SharedPrefsHelper.getPhoneNumber(context) ?: return
        
        // 1. Battery
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = batteryIntent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: 100
        val scale = batteryIntent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: 100
        val batteryPct = (level * 100 / scale.toFloat()).toInt()
        val plugged = batteryIntent?.getIntExtra(BatteryManager.EXTRA_PLUGGED, -1) ?: 0
        val isCharging = plugged == BatteryManager.BATTERY_PLUGGED_AC || plugged == BatteryManager.BATTERY_PLUGGED_USB
        
        // 2. Network & Wifi
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork
        val caps = connectivityManager.getNetworkCapabilities(network)
        val networkType = when {
            caps == null -> "offline"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WIFI"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "CELLULAR"
            else -> "UNKNOWN"
        }
        
        var wifiSsid = ""
        if (networkType == "WIFI") {
            try {
                val wifiManager = context.applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
                val info = wifiManager.connectionInfo
                if (info != null && info.ssid != null && !info.ssid.contains("unknown")) {
                    wifiSsid = info.ssid.removeSurrounding("\"")
                }
            } catch (e: Exception) { }
        }
        
        // 3. Screen
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
        val isScreenOn = powerManager.isInteractive
        val screenActiveMins = if (isScreenOn) 0 else 10
        
        // 4. Audio (Ringer & Headphones)
        val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
        val ringerModeStr = when (audioManager.ringerMode) {
            AudioManager.RINGER_MODE_SILENT -> "SILENT"
            AudioManager.RINGER_MODE_VIBRATE -> "VIBRATE"
            else -> "NORMAL"
        }
        val currentVol = audioManager.getStreamVolume(AudioManager.STREAM_RING)
        val maxVol = audioManager.getStreamMaxVolume(AudioManager.STREAM_RING)
        val ringerVolPct = if (maxVol > 0) (currentVol * 100) / maxVol else 0
        val headphonesOn = audioManager.isWiredHeadsetOn || audioManager.isBluetoothA2dpOn
        
        // 5. App Usage
        var lastAppUsedStr = ""
        try {
            val usageStatsManager = context.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
            val endTime = System.currentTimeMillis()
            val startTime = endTime - 1000 * 60 * 60 * 2 // 2 hours
            val usageEvents = usageStatsManager.queryEvents(startTime, endTime)
            var lastPkg = ""
            if (usageEvents != null) {
                val event = UsageEvents.Event()
                while (usageEvents.hasNextEvent()) {
                    usageEvents.getNextEvent(event)
                    if (event.eventType == UsageEvents.Event.MOVE_TO_FOREGROUND) {
                        lastPkg = event.packageName
                    }
                }
            }
            lastAppUsedStr = lastPkg.split(".").lastOrNull() ?: lastPkg
        } catch (e: Exception) { }

        // Timestamp
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply { 
            timeZone = TimeZone.getTimeZone("UTC")
        }
        val currentTimestamp = sdf.format(Date())

        val packet = SignalPacket(
            phoneNumber = phone,
            timestamp = currentTimestamp,
            screenActiveLastMins = screenActiveMins,
            movementType = "STILL", 
            lastInteractionTime = "",
            batteryLevel = batteryPct,
            isCharging = isCharging,
            networkType = networkType,
            dndActive = (ringerModeStr == "SILENT"),
            ringerMode = ringerModeStr,
            ringerVolume = ringerVolPct,
            isHeadphonePlugged = headphonesOn,
            wifiSsid = wifiSsid,
            lastAppUsed = lastAppUsedStr
        )
        
        try {
            RetrofitClient.apiService.sendSignals(packet)
            println("Successfully synced signals to backend")
        } catch (e: Exception) {
            println("Failed to sync signals: ${e.message}")
        }
    }
}
