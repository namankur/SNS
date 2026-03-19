package com.safeandsound.signals

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.BatteryManager
import android.os.PowerManager
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
        // Simple loop implementation that periodically checks status every 5 minutes and pushes
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
        
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        val level = batteryIntent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: 100
        val scale = batteryIntent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: 100
        val batteryPct = (level * 100 / scale.toFloat()).toInt()
        val plugged = batteryIntent?.getIntExtra(BatteryManager.EXTRA_PLUGGED, -1) ?: 0
        val isCharging = plugged == BatteryManager.BATTERY_PLUGGED_AC || plugged == BatteryManager.BATTERY_PLUGGED_USB
        
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork
        val caps = connectivityManager.getNetworkCapabilities(network)
        val networkType = when {
            caps == null -> "offline"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WIFI"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "CELLULAR"
            else -> "UNKNOWN"
        }
        
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
        val isScreenOn = powerManager.isInteractive
        val screenActiveMins = if (isScreenOn) 0 else 10 // Simplified logic for screen active. MVP implementation

        // Setup the timestamp in ISO 8601 that the backend requires
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply { 
            timeZone = TimeZone.getTimeZone("UTC")
        }
        val currentTimestamp = sdf.format(Date())

        val packet = SignalPacket(
            phoneNumber = phone,
            timestamp = currentTimestamp,
            screenActiveLastMins = screenActiveMins,
            movementType = "STILL", // Hardcoded for this MVP stage, requires complicated ActivityTransition API
            lastInteractionTime = "",
            batteryLevel = batteryPct,
            isCharging = isCharging,
            networkType = networkType,
            dndActive = false
        )
        
        try {
            RetrofitClient.apiService.sendSignals(packet)
            println("Successfully synced signals to backend")
        } catch (e: Exception) {
            println("Failed to sync signals: \${e.message}")
        }
    }
}
