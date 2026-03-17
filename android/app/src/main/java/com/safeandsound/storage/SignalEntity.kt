package com.safeandsound.storage

import androidx.room.Entity
import androidx.room.PrimaryKey
import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query

@Entity(tableName = "signals")
data class SignalEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val timestamp: Long,
    val screenActiveMins: Int,
    val movementType: String,
    val lastInteractionTime: String,
    val batteryLevel: Int,
    val isCharging: Boolean,
    val networkType: String,
    val dndActive: Boolean,
    val isSynced: Boolean = false
)

@Dao
interface SignalDao {
    @Insert
    suspend fun insert(signal: SignalEntity)

    @Query("SELECT * FROM signals WHERE isSynced = 0")
    suspend fun getUnsynced(): List<SignalEntity>

    @Query("UPDATE signals SET isSynced = 1 WHERE id IN (:ids)")
    suspend fun markSynced(ids: List<Long>)

    @Query("DELETE FROM signals WHERE timestamp < :timestamp")
    suspend fun deleteOlderThan(timestamp: Long)
}
