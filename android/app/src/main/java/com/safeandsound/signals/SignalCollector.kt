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
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.app.usage.UsageEvents
import android.app.usage.UsageStatsManager
import kotlinx.coroutines.*
import com.safeandsound.api.RetrofitClient
import com.safeandsound.api.SignalPacket
import com.safeandsound.utils.SharedPrefsHelper
import java.text.SimpleDateFormat
import java.util.*

class SignalCollector(private val context: Context) : SensorEventListener {
    
    private val job = SupervisorJob()
    private val scope = CoroutineScope(Dispatchers.IO + job)
    
    private val sensorManager = context.getSystemService(Context.SENSOR_SERVICE) as SensorManager
    private var lastLightValue: Float = 100f
    private var lastProximityValue: Float = 5f
    private var lastAccelValues = FloatArray(3) { 0f }
    
    fun startCollecting() {
        // Register sensors
        sensorManager.getDefaultSensor(Sensor.TYPE_LIGHT)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_PROXIMITY)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)?.let {
            sensorManager.registerListener(this, it, SensorManager.SENSOR_DELAY_NORMAL)
        }
        
        scope.launch {
            while (isActive) {
                collectAndSend()
                delay(5 * 60 * 1000L) // 5 minutes
            }
        }
    }
    
    fun stopCollecting() {
        sensorManager.unregisterListener(this)
        job.cancel()
    }
    
    override fun onSensorChanged(event: SensorEvent?) {
        event ?: return
        when (event.sensor.type) {
            Sensor.TYPE_LIGHT -> lastLightValue = event.values[0]
            Sensor.TYPE_PROXIMITY -> lastProximityValue = event.values[0]
            Sensor.TYPE_ACCELEROMETER -> {
                System.arraycopy(event.values, 0, lastAccelValues, 0, event.values.size)
            }
        }
    }
    
    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}

    private fun getAppCategory(packageName: String): String {
        val p = packageName.lowercase()
        return when {
            p.contains("whatsapp") || p.contains("messenger") || p.contains("tele") || p.contains("viber") -> "COMMUNICATION"
            p.contains("facebook") || p.contains("insta") || p.contains("twitter") || p.contains("tik") || p.contains("snap") -> "SOCIAL"
            p.contains("youtube") || p.contains("netflix") || p.contains("spotify") || p.contains("prime") || p.contains("music") -> "ENTERTAINMENT"
            p.contains("health") || p.contains("fit") || p.contains("medi") || p.contains("doc") -> "HEALTH"
            p.contains("bank") || p.contains("pay") || p.contains("wallet") || p.contains("finance") -> "FINANCE"
            p.isEmpty() -> "NONE"
            else -> "UTILITY"
        }
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
        
        // 2. Network
        val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork
        val caps = connectivityManager.getNetworkCapabilities(network)
        val networkType = when {
            caps == null -> "offline"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) -> "WIFI"
            caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR) -> "CELLULAR"
            else -> "UNKNOWN"
        }
        val isWifi = networkType == "WIFI"
        
        // 3. Screen (Real Tracking)
        val powerManager = context.getSystemService(Context.POWER_SERVICE) as PowerManager
        val isScreenOn = powerManager.isInteractive
        if (isScreenOn) {
            SharedPrefsHelper.saveLastActiveTime(context, System.currentTimeMillis())
        }
        val lastActive = SharedPrefsHelper.getLastActiveTime(context)
        val diffMins = (System.currentTimeMillis() - lastActive) / (1000 * 60)
        
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
        
        // 5. Environmental Context (Privacy Safe)
        val lightLevel = when {
            lastLightValue < 10f -> "DARK"
            lastLightValue > 500f -> "BRIGHT"
            else -> "NORMAL"
        }
        val orientation = if (Math.abs(lastAccelValues[2]) > 8.5) "FLAT" else "TILTED"
        val prox = if (lastProximityValue < 1f) "NEAR" else "FAR"

        // 6. App Usage (Mapping to categories for privacy)
        var appCategory = "NONE"
        try {
            val usageStatsManager = context.getSystemService(Context.USAGE_STATS_SERVICE) as UsageStatsManager
            val endTime = System.currentTimeMillis()
            val startTime = endTime - 1000 * 60 * 10 // 10 mins back
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
            appCategory = getAppCategory(lastPkg)
        } catch (e: Exception) { }

        // Timestamp
        val sdf = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply { 
            timeZone = TimeZone.getTimeZone("UTC")
        }
        val currentTimestamp = sdf.format(Date())

        val packet = SignalPacket(
            phoneNumber = phone,
            timestamp = currentTimestamp,
            screenActiveLastMins = diffMins.toInt(),
            movementType = "STILL", 
            lastInteractionTime = "",
            batteryLevel = batteryPct,
            isCharging = isCharging,
            isWifi = isWifi,
            networkType = networkType,
            dndActive = (ringerModeStr == "SILENT"),
            ringerMode = ringerModeStr,
            ringerVolume = ringerVolPct,
            isHeadphonePlugged = headphonesOn,
            ambientLight = lightLevel,
            phoneOrientation = orientation,
            proximity = prox,
            appCategory = appCategory
        )
        
        try {
            RetrofitClient.apiService.sendSignals(packet)
            println("Successfully synced signals to backend")
        } catch (e: Exception) {
            println("Failed to sync signals: ${e.message}")
        }
    }
}

