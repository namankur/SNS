import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Register() {
    const [step, setStep] = useState(1);
    const [phone, setPhone] = useState('');
    const [otp, setOtp] = useState('');
    const [name, setName] = useState('');
    const [dearOneName, setDearOneName] = useState('');
    const [dearOnePhone, setDearOnePhone] = useState('');
    const [relation, setRelation] = useState('Maa');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSendOTP = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone_number: phone, name: 'Caller', role: 'caller' })
            });
            const data = await res.json();
            if (res.ok) setStep(2);
            else setError(data.detail || 'Failed to send OTP. Is the backend running?');
        } catch (err) {
            setError('Network error. Please make sure the Python backend is running on port 8000.');
        }
        setLoading(false);
    };

    const handleVerifyOTP = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/auth/verify-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone_number: phone, otp })
            });
            const data = await res.json();
            if (res.ok) {
                localStorage.setItem('token', data.token);
                setStep(3);
            } else {
                setError(data.detail || 'Invalid OTP');
            }
        } catch (err) {
            setError('Network Error.');
        }
        setLoading(false);
    };

    const handleSetup = async () => {
        setLoading(true);
        setError('');
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/family/link`, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ dear_one_phone: dearOnePhone, nickname: dearOneName })
            });
            const data = await res.json();
            if (res.ok) {
                navigate('/invite', { state: data });
            } else {
                setError(data.detail || 'Failed to setup Dear One');
            }
        } catch (err) {
            setError('Network error. Failed to setup Dear One.');
        }
        setLoading(false);
    };

    const renderStep = () => {
        switch (step) {
            case 1:
                return (
                    <div className="space-y-4">
                        <h2 className="text-2xl font-bold">Step 1: Your Phone Number</h2>
                        {error && <p className="text-red-500 text-sm">{error}</p>}
                        <input type="tel" value={phone} onChange={e => setPhone(e.target.value)} placeholder="+91 98765 43210" className="w-full p-4 border rounded-xl text-lg" />
                        <button onClick={handleSendOTP} disabled={loading} className="w-full bg-orange-500 text-white p-4 rounded-xl font-bold">
                            {loading ? 'Sending...' : 'Send OTP'}
                        </button>
                    </div>
                );
            case 2:
                return (
                    <div className="space-y-4">
                        <h2 className="text-2xl font-bold">Step 2: Enter OTP</h2>
                        {error && <p className="text-red-500 text-sm">{error}</p>}
                        <input type="text" value={otp} onChange={e => setOtp(e.target.value)} placeholder="1234" className="w-full p-4 border rounded-xl text-lg tracking-widest text-center" />
                        <button onClick={handleVerifyOTP} disabled={loading} className="w-full bg-orange-500 text-white p-4 rounded-xl font-bold">
                            {loading ? 'Verifying...' : 'Verify'}
                        </button>
                    </div>
                );
            case 3:
                return (
                    <div className="space-y-4">
                        <h2 className="text-2xl font-bold">Step 3: Setup Dear One</h2>
                        <input type="text" value={dearOneName} onChange={e => setDearOneName(e.target.value)} placeholder="Their Name (e.g. Savitri)" className="w-full p-4 border rounded-xl text-lg" />
                        <input type="tel" value={dearOnePhone} onChange={e => setDearOnePhone(e.target.value)} placeholder="Their Phone Number" className="w-full p-4 border rounded-xl text-lg" />
                        <select value={relation} onChange={e => setRelation(e.target.value)} className="w-full p-4 border rounded-xl text-lg bg-white">
                            <option value="Maa">Maa</option>
                            <option value="Papa">Papa</option>
                            <option value="Dadi">Dadi</option>
                            <option value="Other">Other</option>
                        </select>
                        <button onClick={handleSetup} disabled={loading} className="w-full bg-orange-500 text-white p-4 rounded-xl font-bold">
                            {loading ? 'Sending Invite...' : 'Save & Invite'}
                        </button>
                    </div>
                );
            default: return null;
        }
    }

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
            <div className="max-w-md w-full bg-white p-6 rounded-2xl shadow-sm">
                {renderStep()}
            </div>
        </div>
    );
}
