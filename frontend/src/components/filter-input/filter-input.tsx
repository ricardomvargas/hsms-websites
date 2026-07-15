import { useEffect, useState } from 'react';

import './styles/styles.css';

interface FilterInputProps {
  onFilter: (query: string) => void;
  filterActive: boolean;
}

export function FilterInput({ onFilter, filterActive }: FilterInputProps) {
  const [inputValue, setInputValue] = useState('');

  useEffect(() => {
    if (!filterActive) {
      setInputValue('');
    }
  }, [filterActive]);

  const handleFilter = () => {
    const trimmed = inputValue.trim();
    if (trimmed.length === 0) {
      if (filterActive) {
        onFilter('');
      }
      return;
    }
    onFilter(trimmed);
  };

  const handleClear = () => {
    setInputValue('');
    onFilter('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleFilter();
    }
  };

  return (
    <div className="filter-input">
      <input
        className="filter-input__input"
        type="text"
        placeholder="Search company name..."
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
      />
      <button
        className="filter-input__btn filter-input__btn--filter"
        onClick={handleFilter}
      >
        Filter
      </button>
      <button
        className="filter-input__btn filter-input__btn--clear"
        onClick={handleClear}
        disabled={!filterActive}
      >
        X
      </button>
    </div>
  );
}
