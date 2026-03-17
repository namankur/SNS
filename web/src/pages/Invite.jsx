import React from 'react';
import { useNavigate } from 'react-router-dom';

export default function Invite() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-orange-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full text-center space-y-6 bg-white p-6 rounded-2xl shadow-sm">
                <h2 className="text-2xl font-bold">Invite Sent on WhatsApp! ✅</h2>

                <div className="bg-green-50 text-green-800 p-4 rounded-xl text-left text-sm space-y-2">
                    <p><strong>Preview of message sent:</strong></p>
                    <p>"Namaste Savitri ji 🙏<br />Rahul ne aapke liye Safe & Sound setup kiya hai. Yeh aapko track nahi karta — sirf aapke phone ki basic activity dekhta hai.<br /><br />App install karne ke liye:<br /><a href="https://awqhrmnfxsdqospuiamm.supabase.co/storage/v1/object/public/releases/app-debug.apk" className="text-blue-600 underline">Download App</a><br />Koi sawaal? Reply karein."</p>
                </div>

                <button
                    onClick={() => navigate('/dashboard')}
                    className="w-full bg-gray-900 text-white p-4 rounded-xl font-bold mt-4"
                >
                    Go to Dashboard
                </button>
            </div>
        </div>
    );
}
