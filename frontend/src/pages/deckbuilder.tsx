import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import CardFilterBar from './CardFilterBar';
import type { FilterState } from './CardFilterBar';
import { Button } from '@mui/material';
import { DndProvider, useDrag, useDrop } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';

// Define a type for Card object
interface Card {
  id?: string;
  name: string;
  images: { small: string; large?: string };
  [key: string]: any;
}
// Define a type for setHoveredCard
// hoveredCard: { card: Card, source: 'left' | 'right' } | null

type SetHoveredCard = (card: { card: Card, source: 'left' | 'right' } | null) => void;

const CardSidebar = ({ setHoveredCard }: { setHoveredCard: SetHoveredCard }) => {
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
        // Only use 'name' for the main search box, remove all 'query'
        if (query.trim()) body.name = query.trim();
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

        // If body is still empty, send {query: ""} to avoid backend 400
        if (Object.keys(body).length === 0) {
          setError("Please enter a search term or select at least one filter.");
          setLoading(false);
          return;
        }

        try {
            console.log(body);
            body.query = "";
            console.log('http://localhost:8000/cards/');
            const res = await fetch('http://localhost:8000/cards', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body)
            });
            if (res.status === 404) {
                setResults([]);
                setError(null);
                setLoading(false);
                return;
            }
            if (!res.ok) throw new Error(`API error: ${res.status}`);
            const data = await res.json();
            // Deduplicate by id or code
            const unique = Array.from(new Map((data.data || []).map((card: any) => [(card.id || card.code || card.name), card])).values());
            setResults(unique);
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
                  <input type="text" placeholder="Family" value={family} onChange={e => setFamily(e.target.value)} style={{ width: '30%', borderRadius: 6, border: '1px solid #555', background: '#333', color: '#fff', padding: '8px 10px', fontSize: 15 }} />
                  <input type="text" placeholder="Ability" value={ability} onChange={e => setAbility(e.target.value)} style={{ width: '30%', borderRadius: 6, border: '1px solid #555', background: '#333', color: '#fff', padding: '8px 10px', fontSize: 15 }} />
                  <input type="text" placeholder="Trigger" value={trigger} onChange={e => setTrigger(e.target.value)} style={{ width: '30%', borderRadius: 6, border: '1px solid #555', background: '#333', color: '#fff', padding: '8px 10px', fontSize: 15 }} />
                </div>
            </div>
            <CardFilterBar filters={filters} setFilters={setFilters} />
            <div className="card-list-display" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginTop: 24 }}>
                {loading && <div style={{ color: '#aaa', textAlign: 'center', marginTop: 20 }}>Loading...</div>}
                {error && error !== 'No results' && <div style={{ color: '#e66', textAlign: 'center', marginTop: 20 }}>{error}</div>}
                {!loading && !error && results.length === 0 && <div className="card-placeholder">No results</div>}
                {!loading && !error && results.map((card, i) => (
                  card.images && card.images.small ? (
                    <div key={card.id || i} className="card-image-cell" style={{ background: '#222', border: '1px solid #444', borderRadius: 12, padding: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 0, width: 80, height: 110, margin: '0 auto' }}>
                      <DraggableCardImage card={card} setHoveredCard={setHoveredCard} />
                  </div>
                  ) : null
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

// Draggable card image for search results
const DraggableCardImage = ({ card, setHoveredCard }: { card: Card, setHoveredCard: SetHoveredCard }) => {
  const [{ isDragging }, drag] = useDrag(() => ({
    type: 'CARD',
    item: { card },
    collect: (monitor) => ({
      isDragging: !!monitor.isDragging(),
    }),
  }));
  return (
    <img
      ref={drag}
      src={card.images.small}
      alt={card.name}
      style={{
        opacity: isDragging ? 0.5 : 1,
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        cursor: 'grab',
        borderRadius: 8,
      }}
      onMouseEnter={() => setHoveredCard && setHoveredCard({ card, source: 'left' })}
      onMouseLeave={() => setHoveredCard && setHoveredCard(null)}
    />
  );
};
// Droppable board slot for any slot type
const DroppableBoardSlot = ({ card, onDropCard, slotType, style, row, setHoveredCard, onRotateCard }: {
  card: Card | null;
  onDropCard: (card: Card | null) => void;
  slotType?: string;
  style?: React.CSSProperties;
  row?: number;
  setHoveredCard?: SetHoveredCard;
  onRotateCard?: () => void; // Callback for rotating the card
}) => {
  const [{ isOver }, drop] = useDrop(() => ({
    accept: 'CARD',
    drop: (item: { card: Card }) => onDropCard(item.card),
    collect: (monitor) => ({
      isOver: !!monitor.isOver(),
    }),
  }));
  const [hover, setHover] = useState(false);
  // Show delete button for non-LIFE/DON slots and only on hover
  const showDelete = card && slotType !== 'LIFE' && slotType !== 'DON' && hover;
  // Show rotate button for all slots with a card and on hover
  const showRotate = card && hover;
  // Position: top row (row 0) => left-top; bottom row (row 1) => left-bottom
  const deleteBtnPos = row === 1
    ? { left: -32, bottom: 0 }
    : { left: -32, top: 0 };
  const rotateBtnPos = row === 1
    ? { right: -32, bottom: 0 }
    : { right: -32, top: 0 };
  // Define a shared style for the rotate button for clarity and consistency
  const rotateBtnStyle: React.CSSProperties = {
    position: 'absolute' as 'absolute', // Ensure correct type for CSSProperties
    background: 'rgba(30,30,30,0.85)',
    color: '#fff',
    border: 'none',
    borderRadius: 6,
    width: 28,
    height: 28,
    fontSize: 18,
    cursor: 'pointer',
    zIndex: 10,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 2px 8px #0006',
    transition: 'background 0.2s',
  };
  return (
    <div
      ref={drop}
      className={`card-slot ${slotType?.toLowerCase() || ''}-slot`}
      style={{
        border: isOver ? '2px solid #3578e6' : '2px dashed #666',
        borderRadius: 10,
        width: 80,
        height: 110,
        background: card ? 'rgba(0,0,0,0.7)' : 'rgba(0,0,0,0.4)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        ...style,
      }}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
    >
      {showDelete && (
        <button
          onClick={e => { e.stopPropagation(); onDropCard(null); }}
          style={{
            position: 'absolute',
            ...deleteBtnPos,
            background: 'rgba(30,30,30,0.85)',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            width: 28,
            height: 28,
            fontSize: 18,
            cursor: 'pointer',
            zIndex: 10,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px #0006',
          }}
          title="Remove card"
        >🗑️</button>
      )}
      {showRotate && slotType === 'DON' && (
        <button
          onClick={e => { e.stopPropagation(); onRotateCard && onRotateCard(); }}
          style={{
            position: 'absolute',
            top: 4,
            right: 4,
            background: 'rgba(30,30,30,0.85)',
            color: '#fff',
            border: 'none',
            borderRadius: 6,
            width: 28,
            height: 28,
            fontSize: 18,
            cursor: 'pointer',
            zIndex: 20, // Ensure button is above card
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 2px 8px #0006',
            transition: 'background 0.2s',
          }}
          title="Rotate card"
        >⟳</button>
      )}
      {showRotate && slotType !== 'DON' && (
        <button
          onClick={e => { e.stopPropagation(); onRotateCard && onRotateCard(); }}
          style={{
            ...rotateBtnStyle,
            ...(row === 1 ? { right: -32, bottom: 0 } : { right: -32, top: 0 })
          }}
          title="Rotate card"
        >⟳</button>
      )}
      {card ? (
        <img
          src={card.images.small}
          alt={card.name}
          // Rotate the card if card.rotated is true
          style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 8, transform: card.rotated ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }}
          onMouseEnter={() => setHoveredCard && setHoveredCard({ card, source: 'right' })}
          onMouseLeave={() => setHoveredCard && setHoveredCard(null)}
        />
      ) : (
        slotType
      )}
    </div>
  );
};

// Remove all useState for board state in GameBoard, only use props from parent
const GameBoard = ({
  setHoveredCard,
  characterCards, setCharacterCards,
  lifeCardsLeft, setLifeCardsLeft,
  lifeCardsRight, setLifeCardsRight,
  eventCardTop, setEventCardTop,
  leaderCardTop, setLeaderCardTop,
  stageCardTop, setStageCardTop,
  eventCardBottom, setEventCardBottom,
  leaderCardBottom, setLeaderCardBottom,
  stageCardBottom, setStageCardBottom,
  donCardsTop, setDonCardsTop,
  donCardsBottom, setDonCardsBottom,
  clearAll,
}: {
  setHoveredCard: SetHoveredCard;
  characterCards: (Card | null)[];
  setCharacterCards: React.Dispatch<React.SetStateAction<(Card | null)[]>>;
  lifeCardsLeft: (Card | null)[];
  setLifeCardsLeft: React.Dispatch<React.SetStateAction<(Card | null)[]>>;
  lifeCardsRight: (Card | null)[];
  setLifeCardsRight: React.Dispatch<React.SetStateAction<(Card | null)[]>>;
  eventCardTop: Card | null;
  setEventCardTop: (card: Card | null) => void;
  leaderCardTop: Card | null;
  setLeaderCardTop: (card: Card | null) => void;
  stageCardTop: Card | null;
  setStageCardTop: (card: Card | null) => void;
  eventCardBottom: Card | null;
  setEventCardBottom: (card: Card | null) => void;
  leaderCardBottom: Card | null;
  setLeaderCardBottom: (card: Card | null) => void;
  stageCardBottom: Card | null;
  setStageCardBottom: (card: Card | null) => void;
  donCardsTop: (Card | null)[];
  setDonCardsTop: React.Dispatch<React.SetStateAction<(Card | null)[]>>;
  donCardsBottom: (Card | null)[];
  setDonCardsBottom: React.Dispatch<React.SetStateAction<(Card | null)[]>>;
  clearAll: () => void;
}) => {
  // All board state is now managed in DeckBuilderPage and passed as props
  // Remove all useState for board state here
  const [donCountTop, setDonCountTop] = useState(0);
  const [donCountBottom, setDonCountBottom] = useState(0);
  const DON_IMAGE = '/don.png'; // Place your DON!! image in public/don.png
  const defaultDonCard = { images: { small: DON_IMAGE }, name: 'DON!!' };
  const [lifeCountLeft, setLifeCountLeft] = useState(0);
  const [lifeCountRight, setLifeCountRight] = useState(0);
  const LIFE_IMAGE = '/life.png';
  const defaultLifeCard = { images: { small: LIFE_IMAGE }, name: 'LIFE' };
  // Add state for all slots
  // const [characterCards, setCharacterCards] = useState(Array(10).fill(null));
  // const [lifeCardsLeft, setLifeCardsLeft] = useState(Array(5).fill(null));
  // const [lifeCardsRight, setLifeCardsRight] = useState(Array(5).fill(null));
  // const [eventCardTop, setEventCardTop] = useState(null);
  // const [leaderCardTop, setLeaderCardTop] = useState(null);
  // const [stageCardTop, setStageCardTop] = useState(null);
  // const [eventCardBottom, setEventCardBottom] = useState(null);
  // const [leaderCardBottom, setLeaderCardBottom] = useState(null);
  // const [stageCardBottom, setStageCardBottom] = useState(null);
  // const [donCardsTop, setDonCardsTop] = useState(Array(9).fill(null));
  // const [donCardsBottom, setDonCardsBottom] = useState(Array(9).fill(null));
  // Add clearAll function
  // const clearAll = () => {
  //   // setCharacterCards(Array(10).fill(null));
  //   // setLifeCardsLeft(Array(5).fill(null));
  //   // setLifeCardsRight(Array(5).fill(null));
  //   // setEventCardTop(null);
  //   // setLeaderCardTop(null);
  //   // setStageCardTop(null);
  //   // setEventCardBottom(null);
  //   // setLeaderCardBottom(null);
  //   // setStageCardBottom(null);
  //   // setDonCardsTop(Array(9).fill(null));
  //   // setDonCardsBottom(Array(9).fill(null));
  // };
  // Add/Remove LIFE card for left area
  const handleAddLifeLeft = () => {
    setLifeCardsLeft(cards => {
      const idx = cards.findIndex(c => c === null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[idx] = defaultLifeCard;
      return newCards;
    });
  };
  const handleRemoveLifeLeft = () => {
    setLifeCardsLeft(cards => {
      const idx = cards.slice().reverse().findIndex(c => c !== null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[4 - idx] = null;
      return newCards;
    });
  };
  // Add/Remove LIFE card for right area
  const handleAddLifeRight = () => {
    setLifeCardsRight(cards => {
      const idx = cards.findIndex(c => c === null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[idx] = defaultLifeCard;
      return newCards;
    });
  };
  const handleRemoveLifeRight = () => {
    setLifeCardsRight(cards => {
      const idx = cards.slice().reverse().findIndex(c => c !== null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[4 - idx] = null;
      return newCards;
    });
  };
  // Add/Remove DON!! card for top area
  const handleAddDonTop = () => {
    setDonCardsTop(cards => {
      const idx = cards.findIndex(c => c === null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[idx] = defaultDonCard;
      return newCards;
    });
  };
  const handleRemoveDonTop = () => {
    setDonCardsTop(cards => {
      const idx = cards.slice().reverse().findIndex(c => c !== null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[8 - idx] = null;
      return newCards;
    });
  };
  // Add/Remove DON!! card for bottom area
  const handleAddDonBottom = () => {
    setDonCardsBottom(cards => {
      const idx = cards.findIndex(c => c === null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[idx] = defaultDonCard;
      return newCards;
    });
  };
  const handleRemoveDonBottom = () => {
    setDonCardsBottom(cards => {
      const idx = cards.slice().reverse().findIndex(c => c !== null);
      if (idx === -1) return cards;
      const newCards = [...cards];
      newCards[8 - idx] = null;
      return newCards;
    });
  };
  return (
    <div className="game-board-container" style={{ position: 'relative' }}>
      {/* Floating Untap All / Clear All controls, aligned with the EVENT/LEADER/STAGE row, left of EVENT slot */}
      <div style={{
        position: 'absolute', left: 10, top: 180, zIndex: 1002,
        display: 'flex', flexDirection: 'column', gap: 8, background: 'rgba(30,30,30,0.7)', borderRadius: 10, padding: 10, boxShadow: '0 2px 8px rgba(0,0,0,0.12)'
      }}>
        <button style={{
          display: 'flex', alignItems: 'center', gap: 6,
          background: 'rgba(30,30,30,0.38)', color: '#fff', border: 'none', borderRadius: 5, padding: '6px 16px', fontWeight: 600, fontSize: 16, cursor: 'pointer'
        }}>
          <span role="img" aria-label="untap">🔄</span> Untap All
        </button>
        <button
          onClick={clearAll}
          style={{
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
            <button onClick={handleAddDonTop} style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, marginBottom: 2 }}>+</button>
            <button onClick={handleRemoveDonTop} style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>-</button>
          </div>
          <div className="don-area" style={{ display: 'flex', justifyContent: 'center' }}>
            {donCardsTop.map((card, i) => (
              card ? (
                <DroppableBoardSlot
                  key={i}
                  card={card}
                  slotType="DON"
                  style={{ width: 80, height: 110, margin: 5, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onDropCard={droppedCard => {
                    // Replace the DON card at index i
                    setDonCardsTop(cards => {
                      const newCards = [...cards];
                      newCards[i] = droppedCard;
                      return newCards;
                    });
                  }}
                  setHoveredCard={setHoveredCard}
                  onRotateCard={() => {
                    // Toggle the rotated property for this DON card
                    setDonCardsTop(cards => {
                      const newCards = [...cards];
                      if (newCards[i]) newCards[i] = { ...newCards[i], rotated: !newCards[i].rotated };
                      return newCards;
                    });
                  }}
                />
              ) : (
              <div key={i} className="card-slot don-slot">DON!!</div>
              )
            ))}
          </div>
        </div>
        {/* Top EVENT - LEADER - STAGE row */}
        <div className="leader-stage-area" style={{ display: 'flex', justifyContent: 'center', margin: '10px 0' }}>
          <DroppableBoardSlot card={eventCardTop} slotType="EVENT" onDropCard={setEventCardTop} row={0} setHoveredCard={setHoveredCard} onRotateCard={() => eventCardTop && setEventCardTop({ ...eventCardTop, rotated: !eventCardTop.rotated })} />
          <DroppableBoardSlot card={leaderCardTop} slotType="LEADER" onDropCard={setLeaderCardTop} row={0} setHoveredCard={setHoveredCard} onRotateCard={() => leaderCardTop && setLeaderCardTop({ ...leaderCardTop, rotated: !leaderCardTop.rotated })} />
          <DroppableBoardSlot card={stageCardTop} slotType="STAGE" onDropCard={setStageCardTop} row={0} setHoveredCard={setHoveredCard} onRotateCard={() => stageCardTop && setStageCardTop({ ...stageCardTop, rotated: !stageCardTop.rotated })} />
        </div>
        {/* LIFE - CHARACTER - LIFE row */}
        <div style={{ display: 'flex', flexDirection: 'row', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
          {/* Left LIFE with label and buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginRight: 10 }}>
            <div style={{ color: '#ffe066', fontWeight: 800, fontSize: 16, marginBottom: 2, letterSpacing: 0.5, textShadow: '0 2px 8px #000, 0 0px 8px #ffe066' }}>Opponent Life</div>
            <div className="side-area life-area-left" style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: 'rgba(30,30,30,0.38)',
              borderRadius: 12,
              padding: 4,
              justifyContent: 'flex-start',
              marginTop: 0,
              marginBottom: 0,
            }}>
              <div style={{ display: 'flex', flexDirection: 'row', gap: 4, marginBottom: 4, zIndex: 2000, position: 'relative', pointerEvents: 'auto' }}>
                <button
                  onClick={e => { e.stopPropagation(); handleAddLifeLeft(); }}
                  style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, marginBottom: 2, boxShadow: '0 2px 8px #3578e6aa', zIndex: 2001, pointerEvents: 'auto' }}
                >+</button>
                <button
                  onClick={e => { e.stopPropagation(); handleRemoveLifeLeft(); }}
                  style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, boxShadow: '0 2px 8px #3578e6aa', zIndex: 2001, pointerEvents: 'auto' }}
                >-</button>
              </div>
              {lifeCardsLeft.map((card, i) => (
                <DroppableBoardSlot
                  key={i}
                  card={card}
                  slotType="LIFE"
                  style={{ width: 29, height: 29, marginBottom: i < 4 ? 2 : 0 }}
                  onDropCard={(droppedCard) => {
                    setLifeCardsLeft(cards => {
                      const newCards = [...cards];
                      newCards[i] = droppedCard;
                      return newCards;
                    });
                  }}
                  setHoveredCard={setHoveredCard}
                  onRotateCard={() => {
                    // Toggle the rotated property for this LIFE card
                    setLifeCardsLeft(cards => {
                      const newCards = [...cards];
                      if (newCards[i]) newCards[i] = { ...newCards[i], rotated: !newCards[i].rotated };
                      return newCards;
                    });
                  }}
                />
              ))}
            </div>
          </div>
          {/* Center CHARACTER grid */}
          <div className="character-area" style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gridTemplateRows: 'repeat(2, 1fr)', gap: 10, margin: '10px 0' }}>
            {characterCards.map((card, i) => (
              <DroppableBoardSlot
                key={i}
                card={card}
                slotType="CHARACTER"
                row={i < 5 ? 0 : 1}
                onDropCard={(droppedCard) => {
                  setCharacterCards(cards => {
                    const newCards = [...cards];
                    newCards[i] = droppedCard;
                    return newCards;
                  });
                }}
                setHoveredCard={setHoveredCard}
                onRotateCard={() => {
                  // Toggle the rotated property for this character card
                  setCharacterCards(cards => {
                    const newCards = [...cards];
                    if (newCards[i]) newCards[i] = { ...newCards[i], rotated: !newCards[i].rotated };
                    return newCards;
                  });
                }}
              />
            ))}
          </div>
          {/* Right LIFE with label and buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginLeft: 10 }}>
            <div className="side-area life-area-right" style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              background: 'rgba(30,30,30,0.38)',
              borderRadius: 12,
              padding: 4,
              justifyContent: 'flex-end',
              marginTop: 0,
              marginBottom: 0,
            }}>
              <div style={{ display: 'flex', flexDirection: 'row', gap: 4, marginBottom: 4, zIndex: 2000, position: 'relative', pointerEvents: 'auto' }}>
                <button
                  onClick={e => { e.stopPropagation(); handleAddLifeRight(); }}
                  style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, marginBottom: 2, boxShadow: '0 2px 8px #3578e6aa', zIndex: 2001, pointerEvents: 'auto' }}
                >+</button>
                <button
                  onClick={e => { e.stopPropagation(); handleRemoveLifeRight(); }}
                  style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, boxShadow: '0 2px 8px #3578e6aa', zIndex: 2001, pointerEvents: 'auto' }}
                >-</button>
              </div>
              {lifeCardsRight.map((card, i) => (
                <DroppableBoardSlot
                  key={i}
                  card={card}
                  slotType="LIFE"
                  style={{ width: 29, height: 29, marginBottom: i < 4 ? 2 : 0 }}
                  onDropCard={(droppedCard) => {
                    setLifeCardsRight(cards => {
                      const newCards = [...cards];
                      newCards[i] = droppedCard;
                      return newCards;
                    });
                  }}
                  setHoveredCard={setHoveredCard}
                  onRotateCard={() => {
                    // Toggle the rotated property for this LIFE card
                    setLifeCardsRight(cards => {
                      const newCards = [...cards];
                      if (newCards[i]) newCards[i] = { ...newCards[i], rotated: !newCards[i].rotated };
                      return newCards;
                    });
                  }}
                />
              )).reverse()}
            </div>
            <div style={{ color: '#ffe066', fontWeight: 800, fontSize: 16, marginTop: 2, letterSpacing: 0.5, textShadow: '0 2px 8px #000, 0 0px 8px #ffe066' }}>User Life</div>
          </div>
        </div>
        {/* Bottom EVENT - LEADER - STAGE row */}
        <div className="leader-stage-area" style={{ display: 'flex', justifyContent: 'center', margin: '10px 0' }}>
          <DroppableBoardSlot card={eventCardBottom} slotType="EVENT" onDropCard={setEventCardBottom} row={1} setHoveredCard={setHoveredCard} onRotateCard={() => eventCardBottom && setEventCardBottom({ ...eventCardBottom, rotated: !eventCardBottom.rotated })} />
          <DroppableBoardSlot card={leaderCardBottom} slotType="LEADER" onDropCard={setLeaderCardBottom} row={1} setHoveredCard={setHoveredCard} onRotateCard={() => leaderCardBottom && setLeaderCardBottom({ ...leaderCardBottom, rotated: !leaderCardBottom.rotated })} />
          <DroppableBoardSlot card={stageCardBottom} slotType="STAGE" onDropCard={setStageCardBottom} row={1} setHoveredCard={setHoveredCard} onRotateCard={() => stageCardBottom && setStageCardBottom({ ...stageCardBottom, rotated: !stageCardBottom.rotated })} />
        </div>
        {/* Bottom DON!! row with + - buttons */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', margin: '10px 0' }}>
          {/* DON!! + - group */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: 'rgba(30,30,30,0.38)', borderRadius: 12, padding: 4, marginRight: 8 }}>
            <button onClick={handleAddDonBottom} style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20, marginBottom: 2 }}>+</button>
            <button onClick={handleRemoveDonBottom} style={{ borderRadius: '50%', width: 28, height: 28, fontWeight: 'bold', background: '#3578e6', color: '#fff', border: 'none', fontSize: 20 }}>-</button>
          </div>
          <div className="don-area" style={{ display: 'flex', justifyContent: 'center' }}>
            {donCardsBottom.map((card, i) => (
              card ? (
                <DroppableBoardSlot
                  key={i}
                  card={card}
                  slotType="DON"
                  style={{ width: 80, height: 110, margin: 5, padding: 0, display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                  onDropCard={droppedCard => {
                    // Replace the DON card at index i
                    setDonCardsBottom(cards => {
                      const newCards = [...cards];
                      newCards[i] = droppedCard;
                      return newCards;
                    });
                  }}
                  setHoveredCard={setHoveredCard}
                  onRotateCard={() => {
                    // Toggle the rotated property for this DON card
                    setDonCardsBottom(cards => {
                      const newCards = [...cards];
                      if (newCards[i]) newCards[i] = { ...newCards[i], rotated: !newCards[i].rotated };
                      return newCards;
                    });
                  }}
                />
              ) : (
              <div key={i} className="card-slot don-slot">DON!!</div>
              )
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// --- ChatWidget with draggable, resizable, and multi-line input ---
const ChatWidget = forwardRef((props, ref) => {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<{role: 'user'|'assistant', content: string, thread_id?: string}[]>([]);
  const [input, setInput] = useState('');
  const [threadId, setThreadId] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  // Draggable state for chat button and window
  const [btnPos, setBtnPos] = useState({ x: 24, y: 400 });
  const [winPos, setWinPos] = useState({ x: 80, y: 120 });
  const [draggingBtn, setDraggingBtn] = useState(false);
  const [draggingWin, setDraggingWin] = useState(false);
  const [dragOffset, setDragOffset] = useState({ x: 0, y: 0 });
  // Resizable state for chat window
  const [winSize, setWinSize] = useState({ width: 360, height: 440 });
  const [resizing, setResizing] = useState(false);
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 360, height: 440 });

  useEffect(() => {
    if (open && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  // Expose setInputValue for parent to set chat input
  useImperativeHandle(ref, () => ({
    setInputValue: (value: string) => {
      setOpen(true);
      setInput(value);
    },
    sendBoardStateMessage: async (gameState: any) => {
      setOpen(true);
      setLoading(true);
      setMessages(msgs => [...msgs, { role: 'user', content: '[Board State Updated]\n' + JSON.stringify(gameState, null, 2) }]);
      try {
        const res = await fetch('http://localhost:8000/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agent_type: 'rulebook',
            message: 'Analyze the current board state and suggest possible moves.',
            game_state: gameState,
          }),
        });
        const data = await res.json();
        setMessages(msgs => [...msgs, { role: 'assistant', content: data.response || '(no response)', thread_id: data.thread_id }]);
        if (data.thread_id) setThreadId(data.thread_id);
      } catch (e) {
        setMessages(msgs => [...msgs, { role: 'assistant', content: 'Error: could not reach backend.' }]);
      }
      setLoading(false);
    }
  }));

  // Mouse event handlers for dragging button
  const onBtnMouseDown = (e: React.MouseEvent) => {
    setDraggingBtn(true);
    setDragOffset({ x: e.clientX - btnPos.x, y: e.clientY - btnPos.y });
    e.stopPropagation();
  };
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (draggingBtn) {
        setBtnPos({ x: e.clientX - dragOffset.x, y: e.clientY - dragOffset.y });
      }
      if (draggingWin) {
        setWinPos({ x: e.clientX - dragOffset.x, y: e.clientY - dragOffset.y });
      }
      if (resizing) {
        setWinSize({
          width: Math.max(320, resizeStart.width + (e.clientX - resizeStart.x)),
          height: Math.max(320, resizeStart.height + (e.clientY - resizeStart.y)),
        });
      }
    };
    const onUp = () => {
      setDraggingBtn(false);
      setDraggingWin(false);
      setResizing(false);
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
  }, [draggingBtn, draggingWin, dragOffset, resizing, resizeStart]);

  // Mouse event handlers for dragging window
  const onWinMouseDown = (e: React.MouseEvent) => {
    setDraggingWin(true);
    setDragOffset({ x: e.clientX - winPos.x, y: e.clientY - winPos.y });
    e.stopPropagation();
  };
  // Mouse event handler for resizing window
  const onResizeMouseDown = (e: React.MouseEvent) => {
    setResizing(true);
    setResizeStart({ x: e.clientX, y: e.clientY, width: winSize.width, height: winSize.height });
    e.stopPropagation();
  };

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: 'user' as const, content: input, thread_id: threadId || undefined };
    setMessages(msgs => [...msgs, userMsg]);
    setInput('');
    setLoading(true);
    try {
      const body: any = { message: input, agent_type: 'rulebook' };
      if (threadId) body.thread_id = threadId;
      const res = await fetch('http://localhost:8000/chat', {
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

  // Draggable/resizable chat button and window
  return (
    <>
      {!open && (
        <button
          onMouseDown={onBtnMouseDown}
          onClick={() => setOpen(true)}
          style={{
            position: 'fixed',
            left: btnPos.x,
            top: btnPos.y,
            background: '#3578e6', color: '#fff', border: 'none', borderRadius: '50%', width: 56, height: 56, fontSize: 28, boxShadow: '0 2px 8px #0006', cursor: 'pointer', zIndex: 2000
          }}
          title="Open Chat"
        >💬</button>
      )}
      {open && (
        <div
          style={{
            position: 'fixed',
            left: winPos.x,
            top: winPos.y,
            width: winSize.width,
            height: winSize.height,
            background: '#23272f',
            borderRadius: 12,
            boxShadow: '0 2px 12px #0008',
            color: '#fff',
            display: 'flex',
            flexDirection: 'column',
            zIndex: 3000,
            userSelect: resizing ? 'none' : 'auto',
          }}
        >
          {/* Draggable title bar */}
          <div
            onMouseDown={onWinMouseDown}
            style={{
              padding: '10px 16px',
              borderBottom: '1px solid #444',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              cursor: 'move',
              fontWeight: 600,
              background: 'rgba(30,30,30,0.92)',
              borderTopLeftRadius: 12,
              borderTopRightRadius: 12,
              userSelect: 'none',
            }}
          >
            <span>Chat</span>
            <button onClick={() => setOpen(false)} style={{ background: 'none', border: 'none', color: '#fff', fontSize: 20, cursor: 'pointer' }}>×</button>
          </div>
          {/* Chat messages */}
          <div style={{ flex: 1, overflowY: 'auto', padding: 12, background: '#23272f' }}>
            {messages.length === 0 && <div style={{ color: '#aaa', textAlign: 'center', marginTop: 40 }}>No messages yet.</div>}
            {messages.map((msg, i) => (
              <div key={i} style={{ margin: '8px 0', textAlign: msg.role === 'user' ? 'right' : 'left' }}>
                <span style={{
                  display: 'inline-block',
                  background: msg.role === 'user' ? '#3578e6' : '#444',
                  color: '#fff',
                  borderRadius: 8,
                  padding: msg.role === 'user' ? '6px 4px 6px 8px' : '6px 12px',
                  maxWidth: '80%',
                  wordBreak: 'break-word',
                  fontSize: 15,
                  marginLeft: 0,
                  marginRight: 0,
                  borderTopLeftRadius: 8,
                  borderBottomLeftRadius: 8,
                  borderTopRightRadius: 8,
                  borderBottomRightRadius: 8,
                }}>{msg.content}</span>
                {msg.thread_id && <div style={{ fontSize: 10, color: '#888', marginTop: 2 }}>Thread: {msg.thread_id}</div>}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          {/* Multi-line textarea input and controls */}
          <div style={{ padding: 10, borderTop: '1px solid #444', background: '#23272f', display: 'flex', gap: 8 }}>
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
              placeholder="Type a message... (Shift+Enter for newline)"
              style={{ flex: 1, borderRadius: 6, border: '1px solid #555', background: '#181a20', color: '#fff', padding: '8px 10px', fontSize: 15, minHeight: 38, maxHeight: 120, resize: 'vertical', lineHeight: 1.4 }}
              rows={2}
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              style={{ background: '#3578e6', color: '#fff', border: 'none', borderRadius: 6, padding: '8px 16px', fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer', alignSelf: 'flex-end' }}
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
          {/* Resize handle */}
          <div
            onMouseDown={onResizeMouseDown}
            style={{
              position: 'absolute',
              right: 2,
              bottom: 2,
              width: 18,
              height: 18,
              cursor: 'nwse-resize',
              zIndex: 4000,
              background: 'transparent',
              borderBottomRightRadius: 12,
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'flex-end',
              userSelect: 'none',
            }}
            title="Resize"
          >
            <svg width="18" height="18"><polyline points="4,18 18,18 18,4" style={{ fill: 'none', stroke: '#888', strokeWidth: 2 }} /></svg>
          </div>
        </div>
      )}
    </>
  );
});
// --- End ChatWidget ---

// Add exportGameState function to export the current board state as a JSON file
const exportGameState = (gameState: any) => {
  const blob = new Blob([JSON.stringify(gameState, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'game_state.json';
  a.click();
  URL.revokeObjectURL(url);
};

// 1. In DeckBuilderPage, lift all board state up from GameBoard
// 2. Pass all state and setters as props to GameBoard
// 3. Add an Update button and handler in DeckBuilderPage
// 4. Display backend analysis result in DeckBuilderPage

const DeckBuilderPage = () => {
  // State for hover preview
  const [hoveredCard, setHoveredCard] = useState<{ card: Card, source: 'left' | 'right' } | null>(null);
  // Board state lifted from GameBoard
  const [characterCards, setCharacterCards] = useState(Array(10).fill(null));
  const [lifeCardsLeft, setLifeCardsLeft] = useState(Array(5).fill(null));
  const [lifeCardsRight, setLifeCardsRight] = useState(Array(5).fill(null));
  // In DeckBuilderPage, initialize event/leader/stage card state as Card | null, not null only
  const [eventCardTop, setEventCardTop] = useState<Card | null>(null);
  const [leaderCardTop, setLeaderCardTop] = useState<Card | null>(null);
  const [stageCardTop, setStageCardTop] = useState<Card | null>(null);
  const [eventCardBottom, setEventCardBottom] = useState<Card | null>(null);
  const [leaderCardBottom, setLeaderCardBottom] = useState<Card | null>(null);
  const [stageCardBottom, setStageCardBottom] = useState<Card | null>(null);
  const [donCardsTop, setDonCardsTop] = useState(Array(9).fill(null));
  const [donCardsBottom, setDonCardsBottom] = useState(Array(9).fill(null));
  // Add clearAll function here to reset all board state
  const clearAll = () => {
    setCharacterCards(Array(10).fill(null));
    setLifeCardsLeft(Array(5).fill(null));
    setLifeCardsRight(Array(5).fill(null));
    setEventCardTop(null);
    setLeaderCardTop(null);
    setStageCardTop(null);
    setEventCardBottom(null);
    setLeaderCardBottom(null);
    setStageCardBottom(null);
    setDonCardsTop(Array(9).fill(null));
    setDonCardsBottom(Array(9).fill(null));
  };
  // State for backend analysis result
  // In DeckBuilderPage, remove agentAnalysis state and popup. Instead, send the board state as a message to the chat agent and display the response in the chat history.
  // 1. Remove agentAnalysis and setAgentAnalysis
  // 2. Add a ref to ChatWidget to call a sendBoardStateMessage function
  const chatRef = useRef<any>(null);
  // Handler to assemble board state and POST to backend /board/
  const handleUpdateBoardState = async () => {
    // User (bottom half)
    const userState = {
      life: lifeCardsRight.filter(x => x !== null).length,
      don: donCardsBottom.filter(x => x !== null).length,
      leader: leaderCardBottom,
      event: eventCardBottom,
      stage: stageCardBottom,
      character: characterCards.slice(5, 10).filter(x => x !== null),
    };
    // Opponent (top half)
    const opponentState = {
      life: lifeCardsLeft.filter(x => x !== null).length,
      don: donCardsTop.filter(x => x !== null).length,
      leader: leaderCardTop,
      event: eventCardTop,
      stage: stageCardTop,
      character: characterCards.slice(0, 5).filter(x => x !== null),
    };
    const gameState = {
      UserState: userState,
      OpponentState: opponentState,
    };
    try {
      const res = await fetch('http://localhost:8000/board/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gameState),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
    } catch (e: any) {
    }
  };
  return (
    <DndProvider backend={HTML5Backend}>
      <div className="deck-builder-layout" style={{ position: 'relative' }}>
        {/* Show preview on the right when hovering a card in the left search area */}
        {hoveredCard && hoveredCard.source === 'left' && (
          <div style={{ position: 'fixed', right: 40, top: 80, zIndex: 3000, background: 'rgba(30,30,30,0.95)', borderRadius: 16, boxShadow: '0 4px 24px #000a', padding: 16 }}>
            <img src={hoveredCard.card.images.large || hoveredCard.card.images.small} alt={hoveredCard.card.name} style={{ width: 320, height: 'auto', borderRadius: 12, boxShadow: '0 2px 12px #0008' }} />
            <div style={{ color: '#fff', fontWeight: 600, fontSize: 22, marginTop: 8 }}>{hoveredCard.card.name}</div>
          </div>
        )}
        {/* Show preview on the left when hovering a card in the right board area */}
        {hoveredCard && hoveredCard.source === 'right' && (
          <div style={{ position: 'fixed', left: 40, top: 80, zIndex: 3000, background: 'rgba(30,30,30,0.95)', borderRadius: 16, boxShadow: '0 4px 24px #000a', padding: 16 }}>
            <img src={hoveredCard.card.images.large || hoveredCard.card.images.small} alt={hoveredCard.card.name} style={{ width: 320, height: 'auto', borderRadius: 12, boxShadow: '0 2px 12px #0008' }} />
            <div style={{ color: '#fff', fontWeight: 600, fontSize: 22, marginTop: 8 }}>{hoveredCard.card.name}</div>
          </div>
        )}
        <CardSidebar setHoveredCard={setHoveredCard} />
        {/* Pass all board state and setters to GameBoard */}
        <GameBoard
          setHoveredCard={setHoveredCard}
          characterCards={characterCards} setCharacterCards={setCharacterCards}
          lifeCardsLeft={lifeCardsLeft} setLifeCardsLeft={setLifeCardsLeft}
          lifeCardsRight={lifeCardsRight} setLifeCardsRight={setLifeCardsRight}
          eventCardTop={eventCardTop} setEventCardTop={setEventCardTop}
          leaderCardTop={leaderCardTop} setLeaderCardTop={setLeaderCardTop}
          stageCardTop={stageCardTop} setStageCardTop={setStageCardTop}
          eventCardBottom={eventCardBottom} setEventCardBottom={setEventCardBottom}
          leaderCardBottom={leaderCardBottom} setLeaderCardBottom={setLeaderCardBottom}
          stageCardBottom={stageCardBottom} setStageCardBottom={setStageCardBottom}
          donCardsTop={donCardsTop} setDonCardsTop={setDonCardsTop}
          donCardsBottom={donCardsBottom} setDonCardsBottom={setDonCardsBottom}
          clearAll={clearAll}
        />
        {/* Export/Update buttons fixed to the right, symmetric to Untap/Clear on the left */}
        <div style={{
          position: 'fixed',
          right: 32,
          top: 180,
          zIndex: 1002,
          display: 'flex',
          flexDirection: 'column',
          gap: 12,
          background: 'rgba(30,30,30,0.7)',
          borderRadius: 16,
          padding: 16,
          boxShadow: '0 2px 8px rgba(0,0,0,0.12)'
        }}>
          {/* In the Export JSON button, ensure UserState is bottom half and OpponentState is top half */}
          <button
            onClick={() => {
              // User (bottom half)
              const userState = {
                life: lifeCardsRight.filter(x => x !== null).length,
                don: donCardsBottom.filter(x => x !== null).length,
                leader: leaderCardBottom,
                event: eventCardBottom,
                stage: stageCardBottom,
                character: characterCards.slice(5, 10).filter(x => x !== null),
              };
              // Opponent (top half)
              const opponentState = {
                life: lifeCardsLeft.filter(x => x !== null).length,
                don: donCardsTop.filter(x => x !== null).length,
                leader: leaderCardTop,
                event: eventCardTop,
                stage: stageCardTop,
                character: characterCards.slice(0, 5).filter(x => x !== null),
              };
              const gameState = {
                UserState: userState,
                OpponentState: opponentState,
              };
              exportGameState(gameState);
            }}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: 'rgba(30,30,30,0.38)', color: '#fff', border: 'none', borderRadius: 8,
              padding: '10px 24px', fontWeight: 600, fontSize: 17, cursor: 'pointer',
              minWidth: 120, justifyContent: 'center'
            }}
          >
            <span role="img" aria-label="export">📤</span> Export JSON
          </button>
          <button
            onClick={handleUpdateBoardState}
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              background: '#3578e6', color: '#fff', border: 'none', borderRadius: 8,
              padding: '10px 24px', fontWeight: 600, fontSize: 17, cursor: 'pointer',
              minWidth: 120, justifyContent: 'center'
            }}
          >
            <span role="img" aria-label="update">🔎</span> Update
          </button>
        </div>
        {/* Remove Agent Analysis popup, only show chat */}
        <ChatWidget ref={chatRef} />
    </div>
    </DndProvider>
  );
};

export default DeckBuilderPage;
