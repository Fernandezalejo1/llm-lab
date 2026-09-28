'use client';

import { useEffect, useState } from 'react';
import { TrendingUp, Clock, AlertTriangle, BarChart3, Users, DollarSign, RefreshCw } from 'lucide-react';
import { formatCurrency, cn } from '@/lib/utils';
import { getDashboardStats, getDashboardWeekly, type DashboardStats, type WeeklyDay } from '@/lib/api';

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [weekly, setWeekly] = useState<WeeklyDay[]>([]);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    Promise.all([getDashboardStats(), getDashboardWeekly()])
      .then(([s, w]) => { setStats(s); setWeekly(w.weeklyData || []); })
      .catch(console.error)
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent" />
      </div>
    );
  }

  const statCards = [
    { label: 'Facturas', value: String(stats?.totalInvoices || 0), sub: `${stats?.paidInvoices || 0} pagadas`, icon: DollarSign, color: 'text-green-400' },
    { label: 'Pendientes', value: String(stats?.pendingInvoices || 0), sub: formatCurrency(stats?.totalPending || 0), icon: Clock, color: 'text-yellow-400' },
    { label: 'Vencidas', value: String(stats?.overdueInvoices || 0), sub: 'Requieren atencion', icon: AlertTriangle, color: 'text-red-400' },
    { label: 'Movimientos', value: String(stats?.totalMovements || 0), sub: `${stats?.identifiedMovements || 0} identificados`, icon: BarChart3, color: 'text-blue-400' },
    { label: 'Automatizacion', value: `${stats?.automationRate || 0}%`, sub: 'Tasa de identificacion', icon: TrendingUp, color: 'text-purple-400' },
    { label: 'Clientes', value: String(stats?.totalCustomers || 0), sub: formatCurrency(stats?.totalInvoiced || 0), icon: Users, color: 'text-orange-400' },
  ];

  const maxWeekly = Math.max(...weekly.map((d) => d.reconciled + d.pending), 1);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-sm text-[var(--color-text-secondary)]">Resumen de conciliacion bancaria</p>
        </div>
        <button
          onClick={load}
          className="flex items-center gap-2 rounded-lg border border-[var(--color-border)] px-3 py-2 text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
        >
          <RefreshCw className="h-4 w-4" />
          Actualizar
        </button>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
        {statCards.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4 hover:border-[var(--color-border-hover)] transition-colors"
          >
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs text-[var(--color-text-secondary)]">{stat.label}</span>
              <stat.icon className={cn('h-4 w-4', stat.color)} />
            </div>
            <div className="text-2xl font-bold">{stat.value}</div>
            <div className="text-xs text-[var(--color-text-tertiary)] mt-1">{stat.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5 lg:col-span-2">
          <h2 className="text-sm font-medium mb-4">Movimientos Semanales</h2>
          <div className="flex items-end gap-2 h-40">
            {weekly.length > 0
              ? weekly.map((d) => {
                  const total = d.reconciled + d.pending;
                  const h1 = total > 0 ? Math.max((d.reconciled / maxWeekly) * 120, 2) : 2;
                  const h2 = total > 0 ? Math.max((d.pending / maxWeekly) * 120, 2) : 0;
                  return (
                    <div key={d.day} className="flex-1 flex flex-col items-center gap-1">
                      <div className="w-full rounded-t-md bg-[var(--color-primary)] opacity-60" style={{ height: `${h1}px` }} />
                      {h2 > 0 && <div className="w-full rounded-t-md bg-[var(--color-warning)] opacity-60" style={{ height: `${h2}px` }} />}
                      <span className="text-xs text-[var(--color-text-tertiary)] mt-1">{d.day}</span>
                    </div>
                  );
                })
              : ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom'].map((day) => (
                  <div key={day} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full rounded-t-md bg-[var(--color-border)] h-2" />
                    <span className="text-xs text-[var(--color-text-tertiary)] mt-1">{day}</span>
                  </div>
                ))}
          </div>
          <div className="flex items-center gap-4 mt-4 text-xs text-[var(--color-text-tertiary)]">
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[var(--color-primary)]" /> Identificado</span>
            <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full bg-[var(--color-warning)]" /> Pendiente</span>
          </div>
        </div>

        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-5">
          <h2 className="text-sm font-medium mb-4">Resumen</h2>
          <div className="flex flex-col items-center justify-center py-4">
            <div className="text-4xl font-bold text-[var(--color-primary)]">{stats?.automationRate || 0}%</div>
            <div className="text-xs text-[var(--color-text-secondary)] mt-1">Automatizacion</div>
          </div>
          <div className="space-y-3 mt-4">
            {[
              { label: 'Total facturado', value: formatCurrency(stats?.totalInvoiced || 0) },
              { label: 'Total pendiente', value: formatCurrency(stats?.totalPending || 0) },
              { label: 'Total pagado', value: formatCurrency(stats?.totalPaid || 0) },
              { label: 'Sin identificar', value: String(stats?.unmatchedMovements || 0) },
            ].map((item) => (
              <div key={item.label} className="flex justify-between text-sm">
                <span className="text-[var(--color-text-secondary)]">{item.label}</span>
                <span className="font-medium">{item.value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}