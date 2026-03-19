import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Invite() {
    const navigate = useNavigate();
    const location = useLocation();
    const data = location.state || {};
    
    // Safely parse the backend response
    const inviteStatus = data.invite_status || 'unknown';
    const smsStatus = data.sms_status || 'unknown';
    const whatsappStatus = data.whatsapp_status || 'skipped';
    const messageBody = data.message_body || 'No message preview available.';
    const smsError = data.sms_error || 'Unknown error';
    
    // Check if the actual SMS sending failed
    const isError = smsStatus === 'failed' || smsStatus === 'no_twilio_client';

    return (
        <div className="min-h-screen bg-orange-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full text-center space-y-6 bg-white p-6 rounded-2xl shadow-sm">
                
                {isError ? (
                    <>
                        <h2 className="text-2xl font-bold text-red-600">Invite Failed ❌</h2>
                        <div className="bg-red-50 text-red-800 p-4 rounded-xl text-left text-sm space-y-2">
                            <p><strong>Error:</strong></p>
                            <p className="font-mono bg-red-100 p-2 rounded">{smsError}</p>
                            <p className="mt-4 text-xs">Please ensure the backend is running and Twilio credentials are configured correctly.</p>
                        </div>
                    </>
                ) : (
                    <>
                        <h2 className="text-2xl font-bold text-green-600">Invite Sent via SMS! ✅</h2>
                        <div className="bg-green-50 text-green-800 p-4 rounded-xl text-left text-sm space-y-2">
                            <p><strong>Message sent:</strong></p>
                            <p className="whitespace-pre-wrap">{messageBody}</p>
                        </div>
                        <p className="text-xs text-gray-400">SMS: {smsStatus} | WhatsApp: {whatsappStatus}</p>
                    </>
                )}

                <button
                    onClick={() => navigate('/dashboard')}
                    className="w-full bg-gray-900 text-white p-4 rounded-xl font-bold mt-4 hover:bg-gray-800 transition-colors"
                >
                    Go to Dashboard
                </button>
            </div>
        </div>
    );
}
