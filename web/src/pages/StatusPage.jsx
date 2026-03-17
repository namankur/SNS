import React, { useState } from 'react';

export default function StatusPage() {
    const [paused, setPaused] = useState(false);

    return (
        <div className="min-h-screen bg-orange-50 p-4">
            <div className="max-w-md mx-auto space-y-6 bg-white p-6 rounded-2xl shadow-sm">
                <h1 className="text-2xl font-bold text-center">Aapka Status</h1>

                <div className="space-y-4">
                    <div className="p-4 bg-gray-50 rounded-xl border space-y-2">
                        <h2 className="font-semibold">Aaj kisne check kiya:</h2>
                        <ul className="text-sm text-gray-600 list-disc ml-4">
                            <li>Rahul (10:30 AM)</li>
                        </ul>
                    </div>

                    <button
                        className="w-full bg-green-500 text-white p-5 rounded-xl font-bold text-lg shadow-sm"
                        onClick={() => alert('Green status sent to all callers!')}
                    >
                        Main theek hoon! 👍
                    </button>

                    <button
                        onClick={() => setPaused(!paused)}
                        className={`w-full p-5 rounded-xl font-bold text-lg shadow-sm ${paused ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'}`}
                    >
                        {paused ? 'Checks are Paused ⏸️' : 'Aaj checks band karo ⏸️'}
                    </button>
                </div>

                <div className="text-xs text-gray-500 text-center mt-8">
                    <p>Privacy Info:</p>
                    <p>This app does NOT track your location or messages.</p>
                </div>
            </div>
        </div>
    );
}
