import React from 'react';
import { Search, X, Plus } from 'lucide-react';
import { useShopping } from '../context/ShoppingContext';

const SearchResults = () => {
  const { searchResults, clearSearch, addItem } = useShopping();

  if (!searchResults) return null;

  return (
    <div className="search-panel glass-panel">
      <div className="panel-header">
        <div>
          <h3 className="section-title">
            <Search size={20} color="var(--accent-primary)" />
            Search Results
          </h3>
          <p className="panel-subtitle">"{searchResults.query}" {searchResults.maxPrice ? `under $${searchResults.maxPrice}` : ''}</p>
        </div>
        <button onClick={clearSearch} className="icon-btn secondary" aria-label="Close search">
          <X size={20} />
        </button>
      </div>

      {searchResults.results.length === 0 ? (
        <p className="empty-state">No matching items found in the catalog.</p>
      ) : (
        <ul className="item-list">
          {searchResults.results.map((item) => (
            <li key={`search-${item.id}`} className="list-item">
              <div className="item-details">
                <span className="item-name">{item.name}</span>
                <div className="item-meta">
                  <span className="category-tag">{item.category}</span>
                  <span>${item.price.toFixed(2)}</span>
                </div>
              </div>
              <button 
                onClick={() => {
                  addItem(item.name, 1, item.category);
                  clearSearch();
                }} 
                className="icon-btn success"
              >
                <Plus size={20} /> Add
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchResults;
