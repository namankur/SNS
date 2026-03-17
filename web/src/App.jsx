import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Register from './pages/Register';
import Invite from './pages/Invite';
import Dashboard from './pages/Dashboard';
import StatusPage from './pages/StatusPage';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/register" element={<Register />} />
                <Route path="/invite" element={<Invite />} />
                <Route path="/my-status" element={<StatusPage />} />
                <Route path="/dashboard" element={<Dashboard />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
