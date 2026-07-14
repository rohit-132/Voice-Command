import React from 'react';
import { Lightbulb, Plus } from 'lucide-react';
import { useShopping } from '../context/ShoppingContext';

const Suggestions = () => {
  const { suggestions, addItem } = useShopping();

  if (suggestions.length === 0) return null;

  return (
    <div className="suggestions-panel glass-panel">
      <div className="panel-header">
        <div>
          <h3 className="section-title">
            <Lightbulb size={18} color="var(--accent-secondary)" />
            Smart Suggestions
          </h3>
          <p className="panel-subtitle">Tap a suggestion to add it instantly.</p>
        </div>
      </div>
      <div className="suggestions-container">
        {suggestions.map((sug, idx) => (
          <button
            key={`${sug.item.name}-${idx}`}
            className="suggestion-chip"
            onClick={() => addItem(sug.item.name, 1, sug.item.category)}
          >
            <div className="suggestion-text">
              <span>{sug.item.name}</span>
              <small>{sug.reason}</small>
            </div>
            <Plus size={16} />
          </button>
        ))}
      </div>
    </div>
  );
};

export default Suggestions;
