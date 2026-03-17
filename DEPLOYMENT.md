# Safe & Sound - Deployment Checklist

## 1. BACKEND DEPLOYMENT (Railway.app)
1. **Create Railway project**: Go to Railway.app and create a new project.
2. **Connect GitHub repository**: Select the repository where `backend/` lives.
3. **Set all environment variables**:
    ```text
    SUPABASE_URL=...
    SUPABASE_SERVICE_KEY=...
    ANTHROPIC_API_KEY=...
    TWILIO_ACCOUNT_SID=...
    TWILIO_AUTH_TOKEN=...
    TWILIO_WHATSAPP_NUMBER=...
    EXOTEL_API_KEY=...
    EXOTEL_API_TOKEN=...
    EXOTEL_VIRTUAL_NUMBER=...
    JWT_SECRET_KEY=...
    REDIS_URL=...
    ```
4. **Configure continuous deployment**: Ensure it builds from `main`.
5. **Set up health check endpoint**: Ensure `/health` endpoint is polled to prevent cold boots.

## 2. DATABASE (Supabase)
1. Go to Supabase SQL editor.
2. Run the `backend/schema.sql` script to create all tables.
3. Enable Row Level Security (RLS) on all tables.
    ```sql
    -- Example RLS Policy
    ALTER TABLE signals ENABLE ROW LEVEL SECURITY;
    CREATE POLICY "Users view own signals" ON signals FOR SELECT USING (auth.uid() = user_id);
    ```
4. Set up database backups daily (Pro tier recommended).

## 3. WHATSAPP WEBHOOK (Twilio)
1. Go to Twilio Console -> Active Numbers -> WhatsApp.
2. In the WhatsApp Sandbox/Production, set the Webhook URL for incoming messages:
    * `https://yourdomain.railway.app/webhook/whatsapp` (HTTP POST)
3. Test with 5 real phone numbers using Sandbox.
4. Apply for WhatsApp Business API approval for live launch.

## 4. MISSED CALL (Exotel)  
1. Purchase an Indian virtual number from Exotel.
2. Configure App builder passthrough webhook to point to:
    * `https://yourdomain.railway.app/webhook/missed-call`
3. Verify missed calls trigger a webhook in under 3 seconds.

## 5. ANDROID APP DISTRIBUTION
### MVP (Before Play Store):
1. Build signed APK:
    ```bash
    cd android && ./gradlew assembleRelease
    ```
2. Host APK at: `yourdomain.com/app/safeandsound.apk`
3. Send download link via WhatsApp to beta users.
4. Include clear instructions: *"Settings -> Security -> Install from unknown sources"*

### Play Store (After 100 beta users):
1. Pay $25 for Google Play Console account.
2. Prepare store listing in Hindi + English.
3. Add Privacy Policy URL.
4. Submit for review (takes 3-7 days).

## 6. MONITORING
1. Set up Railway logs monitoring.
2. Create alert if error rate > 5% using external tool (e.g. Sentry/Datadog if scaling).
3. Create alert if response time > 10 seconds.
4. Review weekly active usage via Supabase Dashboards.
