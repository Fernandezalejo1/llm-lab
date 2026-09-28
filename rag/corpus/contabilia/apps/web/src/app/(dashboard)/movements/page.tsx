'use client';

import { useEffect, useState } from 'react';
import { formatCurrency } from '@/lib/utils';

const API_BASE = 'http://localhost:3001/api/v1';
const ORG_ID = 'default';

interface Movement {
  id: string;
  date: string;
  description: string;
  reference: string | null;
  movementType: string;
  amount: number;
  currency: string;
  balance: number;
  status: string;
  sequence: number;
  sourceFile: string | null;
}

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  reconciled: { label: 'Conciliado', color: 'bg-green-500/10 text-green-400' },
  identified: { label: 'Identificado', color: 'bg-blue-500/10 text-blue-400' },
  pending: { label: 'Pendiente', color: 'bg-yellow-500/10 text-yellow-400' },
  unidentified: { label: 'Sin Identificar', color: 'bg-red-500/10 text-red-400' },
};

export default function MovementsPage() {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/bank-movements/${ORG_ID}`)
      .then((r) => r.json())
      .then((data) => setMovements(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--color-text-secondary)]">Cargando movimientos...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Movimientos Bancarios</h1>
          <p className="text-sm text-[var(--color-text-secondary)]">
            {movements.length} movimientos
          </p>
        </div>
        <a
          href="/upload"
          className="rounded-lg bg-[var(--color-primary)] px-4 py-2 text-sm font-medium text-[var(--color-primary-foreground)] hover:opacity-90 transition-opacity"
        >
          Importar extracto
        </a>
      </div>

      <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
        <table className="w-full">
          <thead>
            <tr className="border-b border-[var(--color-border)] text-left text-sm text-[var(--color-text-secondary)]">
              <th className="px-6 py-3 font-medium">#</th>
              <th className="px-6 py-3 font-medium">Fecha</th>
              <th className="px-6 py-3 font-medium">Descripcion</th>
              <th className="px-6 py-3 font-medium">Monto</th>
              <th className="px-6 py-3 font-medium">Estado</th>
              <th className="px-6 py-3 font-medium">Fuente</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[var(--color-border)]">
            {movements.map((m) => {
              const statusInfo = STATUS_CONFIG[m.status] || STATUS_CONFIG.pending;
              return (
                <tr key={m.id} className="hover:bg-[var(--color-surface-hover)]">
                  <td className="px-6 py-3 text-sm text-[var(--color-text-tertiary)]">{m.sequence}</td>
                  <td className="px-6 py-3 text-sm">{m.date}</td>
                  <td className="px-6 py-3">
                    <div className="font-medium text-sm">{m.description}</div>
                    {m.reference && (
                      <div className="text-xs text-[var(--color-text-tertiary)] mt-0.5">{m.reference}</div>
                    )}
                  </td>
                  <td className="px-6 py-3 font-medium">
                    <span className={m.movementType === 'credit' ? 'text-green-400' : 'text-red-400'}>
                      {m.movementType === 'credit' ? '+' : '-'}{formatCurrency(m.amount)}
                    </span>
                  </td>
                  <td className="px-6 py-3">
                    <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${statusInfo.color}`}>
                      {statusInfo.label}
                    </span>
                  </td>
                  <td className="px-6 py-3 text-xs text-[var(--color-text-tertiary)]">
                    {m.sourceFile || '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}