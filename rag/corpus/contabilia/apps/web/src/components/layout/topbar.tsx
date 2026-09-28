'use client';

import { Search, Bell, User } from 'lucide-react';
import { useState } from 'react';

export function Topbar() {
  const [query, setQuery] = useState('');

  return (
    <header className="flex h-14 items-center justify-between border-b border-[var(--color-border)] px-6">
      <div className="flex items-center gap-3">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-[var(--color-text-tertiary)]" />
          <input
            type="text"
            placeholder="Buscar... (⌘K)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="h-9 w-80 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] pl-9 pr-3 text-sm text-[var(--color-text)] placeholder:text-[var(--color-text-tertiary)] focus:outline-none focus:border-[var(--color-primary)]"
          />
        </div>
      </div>

      <div className="flex items-center gap-2">
        <button className="rounded-lg p-2 text-[var(--color-text-tertiary)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-hover)]">
          <Bell className="h-4 w-4" />
        </button>
        <button className="rounded-lg p-2 text-[var(--color-text-tertiary)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-hover)]">
          <User className="h-4 w-4" />
        </button>
      </div>
    </header>
  );
}
