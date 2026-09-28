'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, Upload, ArrowLeftRight, Users, CreditCard, ChevronLeft, Building2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { useState } from 'react';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/upload', label: 'Cargar datos', icon: Upload },
  { href: '/reconcile', label: 'Conciliacion', icon: ArrowLeftRight },
  { href: '/accounts', label: 'Estado de cuenta', icon: Users },
  { href: '/movements', label: 'Movimientos', icon: CreditCard },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <aside
      className={cn(
        'flex flex-col border-r border-[var(--color-border)] bg-[var(--color-bg)] transition-all duration-200',
        collapsed ? 'w-16' : 'w-60',
      )}
    >
      <div className="flex h-14 items-center justify-between px-4 border-b border-[var(--color-border)]">
        {!collapsed && (
          <div className="flex items-center gap-2">
            <Building2 className="h-5 w-5 text-[var(--color-primary)]" />
            <span className="font-semibold text-lg tracking-tight">Contabilidad</span>
          </div>
        )}
        {collapsed && <Building2 className="h-5 w-5 text-[var(--color-primary)] mx-auto" />}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className={cn(
            'rounded-md p-1.5 text-[var(--color-text-tertiary)] hover:text-[var(--color-text)] hover:bg-[var(--color-surface-hover)]',
            collapsed && 'hidden',
          )}
        >
          <ChevronLeft className="h-4 w-4" />
        </button>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
                isActive
                  ? 'bg-[var(--color-primary-soft)] text-[var(--color-primary-text)]'
                  : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)] hover:text-[var(--color-text)]',
              )}
              title={collapsed ? item.label : undefined}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>

      {!collapsed && (
        <div className="border-t border-[var(--color-border)] p-4">
          <p className="text-xs text-[var(--color-text-tertiary)]">v0.1.0 MVP</p>
        </div>
      )}
    </aside>
  );
}