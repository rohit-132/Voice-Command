import React from 'react';
import { ShoppingBag, Sparkles } from 'lucide-react';
import VoiceController from './components/VoiceController';
import ShoppingList from './components/ShoppingList';
import Suggestions from './components/Suggestions';
import SearchResults from './components/SearchResults';
import { useShopping } from './context/ShoppingContext';

const StatusBanner = () => {
  const { statusMessage } = useShopping();

  if (!statusMessage.text) return null;

  return (
    <div className={`status-banner ${statusMessage.type}`}>
      {statusMessage.text}
    </div>
  );
};

function App() {
  return (
    <div className="app-container">
      <header className="page-header glass-panel">
        <div className="header-copy">
          <span className="eyebrow">Voice-first shopping</span>
          <h1>VoiceCart</h1>
          <p>Talk, search, and manage your grocery list with a polished voice experience designed for modern demos.</p>
          <div className="hero-stats">
            <div>
              <strong>12+</strong>
              <span>languages</span>
            </div>
            <div>
              <strong>Instant</strong>
              <span>voice parsing</span>
            </div>
            <div>
              <strong>Smart</strong>
              <span>suggestions</span>
            </div>
          </div>
        </div>

        <div className="hero-graphic">
          <div className="hero-chip">
            <ShoppingBag size={18} color="var(--accent-primary)" />
            VoiceCart pro
          </div>
          <div className="hero-glow" />
          <div className="hero-panel-copy">
            <h2>Speak your shopping list</h2>
            <p>Use the mic to add items, search products, and keep your list organized without typing.</p>
          </div>
        </div>
      </header>

      <StatusBanner />

      <div className="main-grid">
        <VoiceController />
        <div className="side-panel">
          <SearchResults />
          <Suggestions />
        </div>
      </div>

      <section className="list-panel glass-panel">
        <div className="section-head">
          <div>
            <h2>My List</h2>
            <p>Quickly review and adjust your shopping cart with responsive controls.</p>
          </div>
          <Sparkles size={20} color="var(--accent-secondary)" />
        </div>
        <ShoppingList />
      </section>
    </div>
  );
}

export default App;
