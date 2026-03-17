import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function Invite() {
    const navigate = useNavigate();
    const location = useLocation();
    const data = location.state || {};
    
    // Safely parse the backend response
    const inviteStatus = data.invite_status || 'unknown';
    const messageBody = data.message_body || 'No message preview available.';
    const errorMessage = data.invite_error || 'Unknown Twilio error';
    
    // Check if the actual Twilio sending failed
    const isError = inviteStatus === 'failed';

    return (
        <div className="min-h-screen bg-orange-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full text-center space-y-6 bg-white p-6 rounded-2xl shadow-sm">
                
                {isError ? (
                    <>
                        <h2 className="text-2xl font-bold text-red-600">Invite Failed ❌</h2>
                        <div className="bg-red-50 text-red-800 p-4 rounded-xl text-left text-sm space-y-2">
                            <p><strong>Twilio Error:</strong></p>
                            <p className="font-mono bg-red-100 p-2 rounded">{errorMessage}</p>
                            <p className="mt-4 text-xs">Note: If you are using a Twilio Sandbox, the recipient number must send "join [your-sandbox-word]" to the Twilio number first.</p>
                        </div>
                    </>
                ) : (
                    <>
                        <h2 className="text-2xl font-bold text-green-600">Invite Sent on WhatsApp! ✅</h2>
                        <div className="bg-green-50 text-green-800 p-4 rounded-xl text-left text-sm space-y-2 whitespace-pre-wrap">
                            <p><strong>Preview of message sent:</strong></p>
                            <p>{messageBody}</p>
                        </div>
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
