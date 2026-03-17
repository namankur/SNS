package com.safeandsound.sync

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.WorkManager
import com.safeandsound.signals.SignalCollector
import com.safeandsound.storage.SignalEntity
// Assume Database and Network helpers exist
import java.util.concurrent.TimeUnit

class SignalSyncWorker(
    appContext: Context, 
    workerParams: WorkerParameters
) : CoroutineWorker(appContext, workerParams) {

    override suspend fun doWork(): Result {
        val collector = SignalCollector(applicationContext)
        
        // 1. Collect
        val battery = collector.collectBattery()
        val dnd = collector.collectDND()
        val network = collector.collectNetwork()
        val screen = collector.collectScreenActivity()
        val move = collector.collectMovement()
        val lastInt = collector.collectLastInteraction()

        @Suppress("UNUSED_VARIABLE") // TODO: Use once Room DB is integrated
        val newSignal = SignalEntity(
            timestamp = System.currentTimeMillis(),
            screenActiveMins = screen,
            movementType = move,
            lastInteractionTime = lastInt,
            batteryLevel = battery.first,
            isCharging = battery.second,
            networkType = network,
            dndActive = dnd
        )

        // 2. Save
        // db.signalDao().insert(newSignal)
        
        // 3. Sync if Network Available
        if (network != "NONE") {
            // val unsynced = db.signalDao().getUnsynced()
            // POST to /api/signals
            // if success: db.signalDao().markSynced(syncedIds)
        }

        return Result.success()
    }

    companion object {
        fun schedule(context: Context) {
            val request = PeriodicWorkRequestBuilder<SignalSyncWorker>(15, TimeUnit.MINUTES)
                .build() // No battery constraints (we want it to run even on low battery)

            WorkManager.getInstance(context).enqueueUniquePeriodicWork(
                "SignalSync",
                ExistingPeriodicWorkPolicy.KEEP,
                request
            )
        }
    }
}
