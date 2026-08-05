import React, { useState, useEffect } from 'react';

const AdminPage = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [tickets, setTickets] = useState([]);
  const [resolutionText, setResolutionText] = useState({});

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      if (res.ok) {
        setIsLoggedIn(true);
        fetchTickets();
      } else {
        alert('Invalid credentials');
      }
    } catch (err) {
      alert('Failed to connect to server.');
    }
  };

  const fetchTickets = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/admin/tickets');
      const data = await res.json();
      setTickets(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleResolve = async (ticketId) => {
    const resolution = resolutionText[ticketId] || 'Resolved by admin.';
    try {
      await fetch(`http://localhost:8000/api/admin/tickets/${ticketId}/resolve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ resolution })
      });
      fetchTickets();
    } catch (err) {
      alert('Failed to resolve ticket.');
    }
  };

  if (!isLoggedIn) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: 'var(--bg-primary)' }}>
        <form onSubmit={handleLogin} style={{ background: 'var(--bg-secondary)', padding: '40px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '16px', width: '300px' }}>
          <h2 style={{ color: 'var(--text-primary)', textAlign: 'center', marginBottom: '8px' }}>Admin Login</h2>
          <input 
            type="text" 
            placeholder="Username" 
            value={username} 
            onChange={(e) => setUsername(e.target.value)}
            style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}
          />
          <input 
            type="password" 
            placeholder="Password" 
            value={password} 
            onChange={(e) => setPassword(e.target.value)}
            style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}
          />
          <button type="submit" style={{ padding: '12px', borderRadius: '8px', background: 'var(--accent-color)', color: 'var(--text-primary)', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}>Login</button>
        </form>
      </div>
    );
  }

  return (
    <div style={{ padding: '40px', maxWidth: '1000px', margin: '0 auto', color: 'var(--text-primary)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <h1>Admin Dashboard</h1>
        <button onClick={fetchTickets} style={{ padding: '8px 16px', borderRadius: '8px', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', cursor: 'pointer' }}>Refresh</button>
      </div>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        {tickets.map(ticket => (
          <div key={ticket.id} style={{ background: 'var(--bg-secondary)', borderRadius: '12px', border: `1px solid ${ticket.status === 'resolved' ? 'var(--success-color)' : 'var(--border-color)'}`, overflow: 'hidden' }}>
            <div style={{ padding: '16px 24px', background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ margin: 0 }}>Ticket #{ticket.id}</h3>
              <span style={{ 
                padding: '4px 12px', 
                borderRadius: '100px', 
                fontSize: '0.85rem', 
                background: ticket.status === 'resolved' ? 'rgba(74, 222, 128, 0.1)' : 'rgba(250, 204, 21, 0.1)',
                color: ticket.status === 'resolved' ? 'var(--success-color)' : 'var(--warning-color)'
              }}>
                {ticket.status.toUpperCase()}
              </span>
            </div>
            <div style={{ padding: '24px' }}>
              <div style={{ marginBottom: '24px' }}>
                <h4 style={{ color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '0.9rem', textTransform: 'uppercase' }}>AI Summary</h4>
                <p style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6', background: 'var(--bg-primary)', padding: '16px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  {ticket.summary}
                </p>
              </div>
              
              {ticket.status !== 'resolved' ? (
                <div style={{ display: 'flex', gap: '12px' }}>
                  <input 
                    type="text" 
                    placeholder="Resolution notes..." 
                    value={resolutionText[ticket.id] || ''}
                    onChange={(e) => setResolutionText({...resolutionText, [ticket.id]: e.target.value})}
                    style={{ flex: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', background: 'var(--bg-primary)', color: 'var(--text-primary)' }}
                  />
                  <button 
                    onClick={() => handleResolve(ticket.id)}
                    style={{ padding: '12px 24px', borderRadius: '8px', background: 'var(--success-color)', color: '#000', border: 'none', cursor: 'pointer', fontWeight: 'bold' }}
                  >
                    Resolve
                  </button>
                </div>
              ) : (
                <div>
                  <h4 style={{ color: 'var(--text-secondary)', marginBottom: '8px', fontSize: '0.9rem', textTransform: 'uppercase' }}>Resolution</h4>
                  <p style={{ color: 'var(--success-color)' }}>✓ {ticket.resolution}</p>
                </div>
              )}
            </div>
          </div>
        ))}
        {tickets.length === 0 && (
          <div style={{ textAlign: 'center', padding: '60px', color: 'var(--text-secondary)', border: '1px dashed var(--border-color)', borderRadius: '12px' }}>
            No tickets found.
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPage;
