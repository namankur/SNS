import React, { useEffect, useState } from 'react';
import { supabase } from '../supabaseClient';

export default function Dashboard() {
    const [dearOnes, setDearOnes] = useState([]);
    const [callerName, setCallerName] = useState('...');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchDearOnes() {
            let callerId = '00000000-0000-0000-0000-000000000000';
            const token = localStorage.getItem('token');
            if (token) {
                try {
                    const payload = JSON.parse(atob(token.split('.')[1]));
                    callerId = payload.sub;
                } catch (e) {
                    console.error("Invalid token format");
                }
            }
            
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
                    lastSync: 'Status available on WhatsApp',
                    score: 'Secured ✅'
                })));
            }
            setLoading(false);
        }
        fetchDearOnes();
    }, []);

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

                                <a
                                    href={`https://wa.me/14155238886?text=${encodeURIComponent(person.nickname)}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="block text-center w-full bg-orange-500 hover:bg-orange-600 text-white p-3 rounded-xl font-bold shadow-sm transition-colors"
                                >
                                    Check Now via WhatsApp
                                </a>
                            </div>
                        ))}
            </div>
        </div>
    );
}
