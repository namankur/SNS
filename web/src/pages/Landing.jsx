import React from 'react';
import { Link } from 'react-router-dom';

export default function Landing() {
    return (
        <div className="min-h-screen bg-orange-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full text-center space-y-8">
                <h1 className="text-4xl font-bold text-gray-900">Maa ne phone nahi uthaya? (V2)</h1>
                <p className="text-xl text-gray-700">Chinta mat karein — Safe & Sound hai</p>

                <div className="bg-white p-6 rounded-2xl shadow-sm space-y-4">
                    <h2 className="font-semibold text-lg">How it works:</h2>
                    <ol className="text-left list-decimal list-inside space-y-2 text-gray-600">
                        <li>Register yourself as a caller</li>
                        <li>Install small app on Dear One's phone</li>
                        <li>Just WhatsApp "Maa" to check on them</li>
                    </ol>
                </div>

                <Link
                    to="/register"
                    className="block w-full bg-orange-500 hover:bg-orange-600 text-white text-lg font-bold py-4 rounded-xl transition shadow-md"
                >
                    Start Free Setup
                </Link>

                <p className="text-sm text-gray-500 font-medium">
                    No GPS. No surveillance. Just peace of mind.
                </p>
            </div>
        </div>
    );
}
