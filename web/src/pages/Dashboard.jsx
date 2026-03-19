import React, { useEffect, useState } from 'react';
import { supabase } from '../supabaseClient';

export default function Dashboard() {
    const [dearOnes, setDearOnes] = useState([]);
    const [callerName, setCallerName] = useState('...');
    const [loading, setLoading] = useState(true);
    const [checkingId, setCheckingId] = useState(null);

    const getCallerId = () => {
        const token = localStorage.getItem('token');
        if (token) {
            try {
                const payload = JSON.parse(atob(token.split('.')[1]));
                return payload.sub;
            } catch (e) {
                console.error("Invalid token format");
            }
        }
        return '00000000-0000-0000-0000-000000000000';
    };

    useEffect(() => {
        async function fetchDearOnes() {
            const callerId = getCallerId();
            
            // 1. Get caller's own name
            const { data: userData } = await supabase
                .from('users')
                .select('name')
                .eq('user_id', callerId)
                .single();
            if (userData?.name) {
                setCallerName(userData.name);
            }

            // 2. Get dear ones
            const { data, error } = await supabase
                .from('caller_dear_one_links')
                .select(`
          nickname,
          dear_one_id,
          users!dear_one_id ( name, phone_number )
        `)
                .eq('caller_id', callerId);

            if (data) {
                setDearOnes(data.map(link => ({
                    id: link.dear_one_id,
                    name: `${link.users.name || 'User'} (${link.nickname})`,
                    nickname: link.nickname,
                    status: 'Active',
                    lastSync: 'Status available via SMS',
                    score: 'Secured ✅'
                })));
            }
            setLoading(false);
        }
        fetchDearOnes();
    }, []);

    const handleCheckNow = async (nickname) => {
        setCheckingId(nickname);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(
                `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/family/check/${encodeURIComponent(nickname)}`,
                {
                    headers: { 'Authorization': `Bearer ${token}` }
                }
            );
            const data = await res.json();
            alert(data.message || 'Check request sent!');
        } catch (err) {
            alert('Failed to send check request. Is the backend running?');
        }
        setCheckingId(null);
    };

    return (
        <div className="min-h-screen bg-gray-50 p-4">
            <div className="max-w-md mx-auto space-y-6">
                <div className="flex justify-between items-center bg-white p-4 rounded-2xl shadow-sm">
                    <div>
                        <h1 className="text-xl font-bold">Safe & Sound</h1>
                        <p className="text-sm text-gray-500">Welcome back, {callerName}</p>
                    </div>
                    <div className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-xs font-bold">Free Tier</div>
                </div>

                <h2 className="text-lg font-semibold ml-2">Linked Dear Ones</h2>

                {loading ? <p className="ml-2 text-gray-500">Loading...</p> :
                    dearOnes.length === 0 ? <p className="ml-2 text-gray-500">No dear ones linked yet.</p> :
                        dearOnes.map(person => (
                            <div key={person.id} className="bg-white p-5 rounded-2xl shadow-sm space-y-4 border-l-4 border-green-500">
                                <div className="flex justify-between items-start">
                                    <div>
                                        <h3 className="text-lg font-bold">{person.name}</h3>
                                        <p className="text-sm text-gray-500">Last sync: {person.lastSync}</p>
                                    </div>
                                    <div className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                                        Score: {person.score}
                                    </div>
                                </div>

                                <button
                                    onClick={() => handleCheckNow(person.nickname)}
                                    disabled={checkingId === person.nickname}
                                    className="block text-center w-full bg-orange-500 hover:bg-orange-600 text-white p-3 rounded-xl font-bold shadow-sm transition-colors disabled:opacity-50"
                                >
                                    {checkingId === person.nickname ? 'Checking...' : 'Check Now via SMS'}
                                </button>
                            </div>
                        ))}
            </div>
        </div>
    );
}
