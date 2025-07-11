import React, { useState, useRef, useEffect } from 'react';
import CardFilterBar from './CardFilterBar';
import type { FilterState } from './CardFilterBar';
import { Button } from '@mui/material';

const CardSidebar = () => {
    const [filters, setFilters] = useState<FilterState>({
        set: '',
        type: '',
        color: '',
        cost: '',
        power: '',
        counter: '',
        rarity: '',
    });
    const [query, setQuery] = useState('');
    const [family, setFamily] = useState('');
    const [ability, setAbility] = useState('');
    const [trigger, setTrigger] = useState('');
    const [results, setResults] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSearch = async () => {
        setLoading(true);
        setError(null);
        setResults([]);
        // Build request body according to CardSearchRequest
        const body: any = {};
        if (query.trim()) body.query = query.trim();
        if (filters.set) body.set = filters.set;
        if (filters.type) body.type = filters.type;
        if (filters.cost !== '' && !isNaN(Number(filters.cost))) body.cost = Number(filters.cost);
        if (filters.power !== '' && !isNaN(Number(filters.power))) body.power = Number(filters.power);
        if (filters.counter !== '' && !isNaN(Number(filters.counter))) body.counter = String(filters.counter);
        if (filters.color) body.color = filters.color;
        if (family) body.family = family;
        if (ability) body.ability = ability;
        if (trigger) body.trigger = trigger;
        // rarity is not supported by backend, so skip
        // To explicitly search for cards without a counter, set counter to '-'
        if (filters.counter === '-') body.counter = '-';
        try {
            const res = await fetch('/cards', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            const data = await res.json();
            setResults(data.data || []);
        } catch (e: any) {
            setError(e.message || 'Unknown error');
        }
        setLoading(false);
    };

    return (
        <div className="card-sidebar">
            <div className="search-filters">
                {/* Top row: search input and control buttons */}
                <input
                  type="text"
                  className="search-input"
                  placeholder="Search cards... (check tips for options)"
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                />
                <div className="filter-row" style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
                    <button className="sidebar-btn">EN <span role="img" aria-label="globe">🌐</span></button>
                    <button className="sidebar-btn">Share</button>
                    <button className="sidebar-btn clear-btn" onClick={() => { setFilters({ set: '', type: '', color: '', cost: '', power: '', counter: '', rarity: '' }); setQuery(''); setFamily(''); setAbility(''); setTrigger(''); setResults([]); setError(null); }}>Clear</button>
                    <button className="sidebar-btn search-btn" onClick={handleSearch} disabled={loading}>Search</button>
                </div>
                <div className="filter-row" style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
                  <input type="text" placeholder="Family" value={family} onChange={e => setFamily(e.target.value)} style={{ flex: 1, borderRadius: 6, border: '1px solid #555', background: '#333', color: '#fff', padding: '8px 10px', fontSize: 15 }} />
                  <input type="text" placeholder="Ability" value={ability} onChange={e => setAbility(e.target.value)} style={{ flex: 1, borderRadius: 6, border: '1px solid #555', background: '#333', color: '#fff', padding: '8px 10px', fontSize: 15 }} />
                  <input type="text" placeholder="Trigger" value={trigger} onChange={e => setTrigger(e.target.value)} style={{ flex: 1, borderRadius: 6, border: '1px solid #555', background: '#333', color: '#fff', padding: '8px 10px', fontSize: 15 }} />
                </div>
            </div>
            <CardFilterBar filters={filters} setFilters={setFilters} />
            <div className="card-list-display">
                {loading && <div style={{ color: '#aaa', textAlign: 'center', marginTop: 20 }}>Loading...</div>}
                {error && <div style={{ color: '#e66', textAlign: 'center', marginTop: 20 }}>{error}</div>}
                {!loading && !error && results.length === 0 && <div className="card-placeholder">No results</div>}
                {!loading && !error && results.map((card, i) => (
                  <div key={card.id || i} className="card-placeholder" style={{ background: '#222', color: '#fff', padding: 8, minHeight: 120, border: '1px solid #444', borderRadius: 8, marginBottom: 8 }}>
                    <div style={{ fontWeight: 600 }}>{card.name}</div>
                    <div style={{ fontSize: 13, color: '#aaa' }}>{card.type} | {card.set} | Cost: {card.cost} | Power: {card.power} | Counter: {card.counter} | Color: {card.color} | Family: {card.family} | Ability: {card.ability} | Trigger: {card.trigger}</div>
                    {card.images && card.images.small && <img src={card.images.small} alt={card.name} style={{ width: 60, marginTop: 6, borderRadius: 4 }} />}
                  </div>
                ))}
            </div>
        </div>
    );
};

interface PlayerAreaProps {
  position: 'top' | 'bottom';
}

const PlayerArea: React.FC<PlayerAreaProps> = ({ position }) => {
  const isTopPlayer = position === 'top';
  return (
    <div className="player-area" data-position={position}>
      {/* Top DON!! row */}
      <div className="don-area" style={{ justifyContent: 'center', margin: '10px 0' }}>
        {Array(9).fill(0).map((_, i) => (
          <div key={i} className="card-slot don-slot">DON!!</div>
        ))}
      </div>
      {/* Top EVENT - LEADER - STAGE row */}
      <div className="leader-stage-area" style={{ display: 'flex', justifyContent: 'center', margin: '10px 0' }}>
        <div className="card-slot event-slot">EVENT</div>
        <div className="card-slot leader-slot">LEADER</div>
        <div className="card-slot stage-slot">STAGE</div>
      </div>
      {/* LIFE - CHARACTER - LIFE row */}
      <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
        {/* Left LIFE area + buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginRight: 12 }}>
          <button style={{ borderRadius: '50%', width: 26, height: 26, marginBottom: 4, fontWeight: 'bold', background: '#2226', color: '#fff', border: 'none' }}>+</button>
          {Array(5).fill(0).map((_, i) => (
            <div key={i} className="card-slot life-slot" style={{ marginBottom: 4 }}>LIFE</div>
          ))}
          <button style={{ borderRadius: '50%', width: 26, height: 26, marginTop: 4, fontWeight: 'bold', background: '#2226', color: '#fff', border: 'none' }}>-</button>
        </div>
        {/* Center CHARACTER grid */}
        <div className="character-area" style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gridTemplateRows: 'repeat(2, 1fr)', gap: 10, margin: '10px 0' }}>
          {Array(10).fill(0).map((_, i) => (
            <div key={i} className="card-slot character-slot">CHARACTER</div>
          ))}
        </div>
        {/* Right LIFE area + buttons */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginLeft: 12 }}>
          <button style={{ borderRadius: '50%', width: 26, height: 26, marginBottom: 4, fontWeight: 'bold', background: '#2226', color: '#fff', border: 'none' }}>+</button>
          {Array(5).fill(0).map((_, i) => (
            <div key={i} className="card-slot life-slot" style={{ marginBottom: 4 }}>LIFE</div>
          ))}
          <button style={{ borderRadius: '50%', width: 26, height: 26, marginTop: 4, fontWeight: 'bold', background: '#2226', color: '#fff', border: 'none' }}>-</button>
        </div>
      </div>
      {/* Bottom EVENT - LEADER - STAGE row */}
      <div className="leader-stage-area" style={{ display: 'flex', justifyContent: 'center', margin: '10px 0' }}>
        <div className="card-slot event-slot">EVENT</div>
        <div className="card-slot leader-slot">LEADER</div>
        <div className="card-slot stage-slot">STAGE</div>
      </div>
      {/* Bottom DON!! row */}
      <div className="don-area" style={{ justifyContent: 'center', margin: '10px 0' }}>
        {Array(9).fill(0).map((_, i) => (
          <div key={i} className="card-slot don-slot">DON!!</div>
        ))}
      </div>
    </div>
  );
};

const GameBoard = () => {
  return (
    <div className="game-board-container" style={{ position: 'relative' }}>
      {/* Floating Untap All / Clear All controls, aligned with the EVENT/LEADER/STAGE row, left of EVENT slot */}
      <div style={{
        position: 'absolute', left: 60, top: 270, zIndex: 10,
        display: 'flex', flexDirection: 'column', gap: 8, background: 'rgba(30,30,30,0.7)', borderRadius: 10, padding: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.12)'
      }}>
        <button style={{
          display: 'flex', alignItems: 'center', gap: 6,
          background: 'rgba(30,30,30,0.38)', color: '#fff', border: 'none', borderRadius: 5, padding: '6px 16px', fontWeight: 600, fontSize: 16, cursor: 'pointer'
        }}>
          <span role="img" aria-label="untap">🔄</span> Untap All
        </button>
        <button style={{
          background: 'rgba(30,30,30,0.38)', color: '#fff', border: 'none', borderRadius: 5, padding: '6px 16px', fontWeight: 600, fontSize: 16, cursor: 'pointer'
        }}>
          <span role="img" aria-label="clear">🗑️</span> Clear All
        </button>
      </div>
      <div className="game-board" style={{ gap: 0 }}>
        {/* Top DON!! row with + - buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '10px 0' }}>
          {/* DON!! + - group */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(30,30,30,0.38)', borderRadius: 12, padding: 4, marginRight: 8 }}>
            <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, marginBottom: 2 }}>+</button>
            <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>-</button>
          </div>
          <div className="don-area" style={{ display: 'flex', justifyContent: 'center' }}>
            {Array(9).fill(0).map((_, i) => (
              <div key={i} className="card-slot don-slot">DON!!</div>
            ))}
          </div>
        </div>
        {/* Top EVENT - LEADER - STAGE row */}
        <div className="leader-stage-area" style={{ display: 'flex', justifyContent: 'center', margin: '10px 0' }}>
          <div className="card-slot event-slot">EVENT</div>
          <div className="card-slot leader-slot">LEADER</div>
          <div className="card-slot stage-slot">STAGE</div>
        </div>
        {/* LIFE - CHARACTER - LIFE row */}
        <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
          {/* Left LIFE with + - group */}
          <div className="side-area life-area-left" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', background: 'rgba(30,30,30,0.38)', borderRadius: 12, padding: 8, marginRight: 10 }}>
            <div style={{ display: 'flex', flexDirection: 'row', gap: 6, marginBottom: 8 }}>
              <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>+</button>
              <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>-</button>
            </div>
            {Array(5).fill(0).map((_, i) => (
              <div key={i} className="card-slot life-slot">LIFE</div>
            ))}
          </div>
          {/* Center CHARACTER grid */}
          <div className="character-area" style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gridTemplateRows: 'repeat(2, 1fr)', gap: 10, margin: '10px 0' }}>
            {Array(10).fill(0).map((_, i) => (
              <div key={i} className="card-slot character-slot">CHARACTER</div>
            ))}
          </div>
          {/* Right LIFE with + - group */}
          <div className="side-area life-area-right" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', background: 'rgba(30,30,30,0.38)', borderRadius: 12, padding: 8, marginLeft: 10 }}>
            <div style={{ display: 'flex', flexDirection: 'row', gap: 6, marginBottom: 8 }}>
              <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>+</button>
              <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>-</button>
            </div>
            {Array(5).fill(0).map((_, i) => (
              <div key={i} className="card-slot life-slot">LIFE</div>
            ))}
          </div>
        </div>
        {/* Bottom EVENT - LEADER - STAGE row */}
        <div className="leader-stage-area" style={{ display: 'flex', justifyContent: 'center', margin: '10px 0' }}>
          <div className="card-slot event-slot">EVENT</div>
          <div className="card-slot leader-slot">LEADER</div>
          <div className="card-slot stage-slot">STAGE</div>
        </div>
        {/* Bottom DON!! row with + - buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '10px 0' }}>
          {/* DON!! + - group */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(30,30,30,0.38)', borderRadius: 12, padding: 4, marginRight: 8 }}>
            <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, marginBottom: 2 }}>+</button>
            <button style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>-</button>
          </div>
          <div className="don-area" style={{ display: 'flex', justifyContent: 'center' }}>
            {Array(9).fill(0).map((_, i) => (
              <div key={i} className="card-slot don-slot">DON!!</div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- ChatWidget Component ---
const ChatWidget: React.FC = () => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{role: 'user'|'assistant', content: string, thread_id?: string}[]>([]);
  const [input, setInput] = useState('');
  const [threadId, setThreadId] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user' as const, content: input, thread_id: threadId || undefined };
    setMessages(msgs => [...msgs, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const body: any = { message: input, agent_type: 'rulebook' };
      if (threadId) body.thread_id = threadId;
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      setMessages(msgs => [...msgs, { role: 'assistant' as const, content: data.response || '(no response)', thread_id: data.thread_id }]);
      if (data.thread_id) setThreadId(data.thread_id);
    } catch (e) {
      setMessages(msgs => [...msgs, { role: 'assistant' as const, content: 'Error: could not reach backend.' }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ position: 'fixed', bottom: 24, left: 24, zIndex: 1000 }}>
      {open ? (
        <div style={{ width: 340, background: '#23272f', borderRadius: 12, boxShadow: '0 2px 12px #0008', color: '#fff', display: 'flex', flexDirection: 'column', height: 420 }}>
          <div style={{ padding: '10px 16px', borderBottom: '1px solid #444', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontWeight: 600 }}>Chat</span>
            <button onClick={() => setOpen(false)} style={{ background: 'none', border: 'none', color: '#fff', fontSize: 20, cursor: 'pointer' }}>×</button>
          </div>
          <div style={{ flex: 1, overflowY: 'auto', padding: 12, background: '#23272f' }}>
            {messages.length === 0 && <div style={{ color: '#aaa', textAlign: 'center', marginTop: 40 }}>No messages yet.</div>}
            {messages.map((msg, i) => (
              <div key={i} style={{ margin: '8px 0', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                <span style={{
                  display: 'inline-block',
                  background: msg.role === 'user' ? '#3578e6' : '#444',
                  color: '#fff',
                  borderRadius: 8,
                  padding: '6px 12px',
                  maxWidth: '80%',
                  wordBreak: 'break-word',
                  fontSize: 15
                }}>{msg.content}</span>
                {msg.thread_id && <div style={{ fontSize: 10, color: '#888', marginTop: 2 }}>Thread: {msg.thread_id}</div>}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <div style={{ padding: 10, borderTop: '1px solid #444', background: '#23272f', display: 'flex', gap: 8 }}>
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter') sendMessage(); }}
              placeholder="Type a message..."
              style={{ flex: 1, borderRadius: 6, border: '1px solid #555', background: '#181a20', color: '#fff', padding: '8px 10px', fontSize: 15 }}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{ background: '#3578e6', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 16px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer' }}
            >Send</button>
          </div>
          <div style={{ padding: 8, borderTop: '1px solid #444', background: '#222', fontSize: 12, color: '#aaa' }}>
            <span>Thread ID: </span>
            <input
              type="text"
              value={threadId}
              onChange={e => setThreadId(e.target.value)}
              placeholder="(optional)"
              style={{ width: 120, borderRadius: 4, border: '1px solid #555', background: '#181a20', color: '#fff', padding: '2px 6px', fontSize: 12, marginLeft: 4 }}
              disabled={loading}
            />
          </div>
        </div>
      ) : (
        <button
          onClick={() => setOpen(true)}
          style={{ background: '#3578e6', color: '#fff', border: 'none', borderRadius: '50%', width: 56, height: 56, fontSize: 28, boxShadow: '0 2px 8px #0006', cursor: 'pointer' }}
          title="Open Chat"
        >💬</button>
      )}
    </div>
  );
};
// --- End ChatWidget ---

const DeckBuilderPage = () => {
  return (
    <div className="deck-builder-layout">
        <CardSidebar />
        <GameBoard />
        <ChatWidget />
    </div>
  );
};

export default DeckBuilderPage;
