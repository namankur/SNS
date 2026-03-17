package com.safeandsound.utils

import android.content.Context
import android.content.Intent
import android.os.Build
import android.provider.Settings
import android.os.PowerManager

class BatteryOptimizationHelper(private val context: Context) {
    
    fun isIgnoringBatteryOptimizations(): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val pm = context.getSystemService(Context.POWER_SERVICE) as PowerManager
            return pm.isIgnoringBatteryOptimizations(context.packageName)
        }
        return true
    }

    fun getBatteryOptimizationIntent(): Intent {
        val manufacturer = Build.MANUFACTURER.lowercase()
        return when {
            manufacturer.contains("xiaomi") -> {
                Intent("miui.intent.action.APP_PERM_EDITOR").apply {
                    setClassName("com.miui.securitycenter", "com.miui.permcenter.permissions.PermissionsEditorActivity")
                    putExtra("extra_pkgname", context.packageName)
                }
            }
            manufacturer.contains("samsung") -> {
                Intent().apply {
                    setClassName("com.samsung.android.lool", "com.samsung.android.sm.ui.battery.BatteryActivity")
                }
            }
            else -> {
                Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS)
            }
        }
    }
}
