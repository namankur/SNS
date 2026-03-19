package com.safeandsound.ui

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.safeandsound.utils.SharedPrefsHelper
import com.safeandsound.signals.TrackingService

class SetupActivity : ComponentActivity() {

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        // In a real product, we'd check each permission exactly.
        // For MVP, if they accepted what we asked, we proceed to start the service.
        checkAndStartService()
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        if (SharedPrefsHelper.isSetupComplete(this)) {
            checkAndStartService()
            finish()
            return
        }

        setContent {
            MaterialTheme {
                SetupScreenContent()
            }
        }
    }

    @OptIn(ExperimentalMaterial3Api::class)
    @Composable
    fun SetupScreenContent() {
        var phoneNumber by remember { mutableStateOf("") }
        var errorMessage by remember { mutableStateOf("") }
        var step by remember { mutableStateOf(1) } // 1: Phone, 2: Permissions

        Scaffold(
            topBar = { TopAppBar(title = { Text("Safe & Sound Setup") }) }
        ) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(24.dp),
                verticalArrangement = Arrangement.Center,
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                if (step == 1) {
                    Text("Enter this phone's number", style = MaterialTheme.typography.headlineSmall)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text("This links the app to your family dashboard.", color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    OutlinedTextField(
                        value = phoneNumber,
                        onValueChange = { phoneNumber = it },
                        label = { Text("Phone Number (e.g., +919876543210)") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    
                    if (errorMessage.isNotEmpty()) {
                        Text(errorMessage, color = MaterialTheme.colorScheme.error)
                        Spacer(modifier = Modifier.height(16.dp))
                    }

                    Button(
                        onClick = {
                            if (phoneNumber.length > 5) {
                                SharedPrefsHelper.savePhoneNumber(this@SetupActivity, phoneNumber)
                                step = 2
                            } else {
                                errorMessage = "Please enter a valid phone number"
                            }
                        },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Next")
                    }
                } else {
                    Text("Permissions Needed", style = MaterialTheme.typography.headlineSmall)
                    Spacer(modifier = Modifier.height(16.dp))
                    Text("We need a few permissions to silently collect signals (like battery and movement) so your family knows you are okay.")
                    Spacer(modifier = Modifier.height(24.dp))
                    
                    Button(
                        onClick = { requestBasePermissions() },
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Text("Grant Permissions & Complete")
                    }
                    
                    Spacer(modifier = Modifier.height(16.dp))
                    TextButton(onClick = { requestUsageStatsPermission() }) {
                        Text("Usage Access (For Screen Time)")
                    }
                }
            }
        }
    }

    private fun requestBasePermissions() {
        val permissionsToRequest = mutableListOf<String>()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            permissionsToRequest.add(Manifest.permission.ACTIVITY_RECOGNITION)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        
        if (permissionsToRequest.isNotEmpty()) {
            permissionLauncher.launch(permissionsToRequest.toTypedArray())
        } else {
            checkAndStartService()
        }
    }

    private fun requestUsageStatsPermission() {
        startActivity(Intent(Settings.ACTION_USAGE_ACCESS_SETTINGS))
    }

    private fun checkAndStartService() {
        SharedPrefsHelper.setSetupComplete(this, true)
        val intent = Intent(this, TrackingService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        
        // MVP: Just show a toast or transition, but for now we finish to hide the app
        finish()
    }
}
