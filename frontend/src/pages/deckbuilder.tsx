import React, { useState } from 'react';
import CardFilterBar from './CardFilterBar';
import type { FilterState } from './CardFilterBar';
import { Button } from '@mui/material';

const CardSidebar = () => {
    const [filters, setFilters] = useState<FilterState>({
        set: [],
        type: [],
        color: [],
        cost: [],
        power: [],
        counter: [],
        rarity: [],
    });

    const handleSearch = () => {
        const params = new URLSearchParams();
        Object.entries(filters).forEach(([key, value]) => {
            if (Array.isArray(value) && value.length > 0) {
                params.append(key, value.join(','));
            }
        });
        fetch(`/api/cards?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                // TODO: Display card results in the UI
                console.log(data);
            });
    };

    return (
        <div className="card-sidebar">
            <div className="search-filters">
                {/* Top row: search input and control buttons */}
                <input type="text" className="search-input" placeholder="Search cards... (check tips for options)" />
                <div className="filter-row" style={{ display: 'flex', alignItems: 'center', gap: 8, marginTop: 8 }}>
                    <button className="sidebar-btn">EN <span role="img" aria-label="globe">🌐</span></button>
                    <button className="sidebar-btn">Share</button>
                    <button className="sidebar-btn clear-btn">Clear</button>
                    <button className="sidebar-btn search-btn" onClick={handleSearch}>Search</button>
                </div>
            </div>
            <CardFilterBar filters={filters} setFilters={setFilters} />
            <div className="card-list-display">
                {/* In the future, card search results will be mapped here */}
                <div className="card-placeholder"></div>
                <div className="card-placeholder"></div>
                <div className="card-placeholder"></div>
                <div className="card-placeholder"></div>
                <div className="card-placeholder"></div>
                <div className="card-placeholder"></div>
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

const DeckBuilderPage = () => {
  return (
    <div className="deck-builder-layout">
        <CardSidebar />
        <GameBoard />
    </div>
  );
};

export default DeckBuilderPage;
