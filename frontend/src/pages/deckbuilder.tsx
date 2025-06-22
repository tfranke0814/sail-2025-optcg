import React from 'react';

const CardSidebar = () => {
    return (
        <div className="card-sidebar">
            <div className="search-filters">
                <input type="text" className="search-input" placeholder="Search cards... (check tips for options)" />
                <div className="filter-row">
                    <button className="sidebar-btn">EN</button>
                    <button className="sidebar-btn">Share</button>
                    <button className="sidebar-btn clear-btn">Clear</button>
                </div>
                <div className="filter-grid">
                    <select><option>Set</option></select>
                    <select><option>Type</option></select>
                    <select><option>Color</option></select>
                    <select><option>Cost</option></select>
                    <select><option>Power</option></select>
                    <select><option>Counter</option></select>
                    <select><option>Rarity</option></select>
                </div>
            </div>
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
       <div className="top-section">
        <div className="don-controls">
            <div className="don-counter">0/0</div>
            <button className="control-button">+</button>
            <button className="control-button">-</button>
        </div>
        <div className="don-area">
          {Array(10).fill(0).map((_, i) => (
            <div key={i} className="card-slot don-slot">DON!!</div>
          ))}
        </div>
      </div>
      <div className="main-section">
        <div className="side-area life-area-left">
            <div className="life-controls">
                <button className="control-button">+</button>
                <button className="control-button">-</button>
            </div>
            {Array(5).fill(0).map((_, i) => (
                <div key={i} className="card-slot life-slot">LIFE</div>
            ))}
        </div>
        <div className="center-field">
          {!isTopPlayer && (
            <div className="board-controls">
              <button className="action-button">Untap All</button>
              <button className="action-button">Clear All</button>
            </div>
          )}
          <div className="leader-stage-area">
            <div className="card-slot event-slot">EVENT</div>
            <div className="card-slot leader-slot">LEADER</div>
            <div className="card-slot stage-slot">STAGE</div>
          </div>
          <div className="character-area">
            {Array(10).fill(0).map((_, i) => (
              <div key={i} className="card-slot character-slot">CHARACTER</div>
            ))}
          </div>
        </div>
        <div className="side-area life-area-right">
             <div className="life-controls">
                <button className="control-button">+</button>
                <button className="control-button">-</button>
            </div>
            {Array(5).fill(0).map((_, i) => (
                <div key={i} className="card-slot life-slot">LIFE</div>
            ))}
        </div>
      </div>
    </div>
  )
}

const GameBoard = () => {
  return (
    <div className="game-board-container">
      <div className="game-board">
        <PlayerArea position="top" />
        <PlayerArea position="bottom" />
      </div>
       <div className="logo-area">
         {/* Placeholder for logo */}
         <div className="logo-placeholder"></div>
      </div>
    </div>
  );
}

const DeckBuilderPage = () => {
  return (
    <div className="deck-builder-layout">
        <CardSidebar />
        <GameBoard />
    </div>
  );
};

export default DeckBuilderPage;
