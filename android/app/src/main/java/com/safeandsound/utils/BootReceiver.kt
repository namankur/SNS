package com.safeandsound.utils

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.safeandsound.sync.SignalSyncWorker

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Restart WorkManager periodic job after device reboot
            SignalSyncWorker.schedule(context)
        }
    }
}
