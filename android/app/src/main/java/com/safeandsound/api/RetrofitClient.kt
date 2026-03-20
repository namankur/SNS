package com.safeandsound.api

import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import java.util.concurrent.TimeUnit
import retrofit2.http.POST
import retrofit2.http.Body
import com.google.gson.annotations.SerializedName

object RetrofitClient {
    private const val BASE_URL = "https://sns-production-a328.up.railway.app/api/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}

interface ApiService {
    @POST("signals")
    suspend fun sendSignals(@Body signalPacket: SignalPacket): SignalResponse
}

data class SignalPacket(
    @SerializedName("phone_number") val phoneNumber: String, 
    @SerializedName("timestamp") val timestamp: String,
    @SerializedName("screen_active_last_mins") val screenActiveLastMins: Int,
    @SerializedName("movement_type") val movementType: String,
    @SerializedName("last_interaction_time") val lastInteractionTime: String,
    @SerializedName("battery_level") val batteryLevel: Int,
    @SerializedName("is_charging") val isCharging: Boolean,
    @SerializedName("is_wifi") val isWifi: Boolean,
    @SerializedName("network_type") val networkType: String,
    @SerializedName("dnd_active") val dndActive: Boolean,
    @SerializedName("ringer_mode") val ringerMode: String,
    @SerializedName("ringer_volume") val ringerVolume: Int,
    @SerializedName("is_headphone_plugged") val isHeadphonePlugged: Boolean,
    @SerializedName("ambient_light") val ambientLight: String,
    @SerializedName("phone_orientation") val phoneOrientation: String,
    @SerializedName("proximity") val proximity: String
)

data class SignalResponse(
    @SerializedName("status") val status: String,
    @SerializedName("message") val message: String
)
