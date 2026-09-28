'use client';

import { useEffect, useState } from 'react';
import { formatCurrency } from '@/lib/utils';

const API_BASE = 'http://localhost:3001/api/v1';
const ORG_ID = 'default';

type TabType = 'pending' | 'identified' | 'reconciled';

interface Movement {
  id: string;
  date: string;
  description: string;
  reference: string | null;
  amount: number;
  movementType: string;
  currency: string;
  balance: number;
  status: string;
  sequence: number;
  sourceFile: string | null;
}

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  reconciled: { label: 'Confirmado', color: 'bg-green-500/10 text-green-400' },
  identified: { label: 'Identificado', color: 'bg-blue-500/10 text-blue-400' },
  pending: { label: 'Pendiente', color: 'bg-yellow-500/10 text-yellow-400' },
  unidentified: { label: 'Sin identificar', color: 'bg-red-500/10 text-red-400' },
};

export default function ReconcilePage() {
  const [movements, setMovements] = useState<Movement[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>('pending');
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);

  useEffect(() => {
    fetch(`${API_BASE}/bank-movements/${ORG_ID}`)
      .then((r) => r.json())
      .then((data) => setMovements(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const tabCounts = {
    pending: movements.filter((m) => m.status === 'pending').length,
    identified: movements.filter((m) => m.status === 'identified').length,
    reconciled: movements.filter((m) => m.status === 'reconciled').length,
  };

  const filteredMovements = movements.filter((m) => {
    if (activeTab === 'pending') return m.status === 'pending' || m.status === 'unidentified';
    if (activeTab === 'identified') return m.status === 'identified';
    return m.status === 'reconciled';
  });

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id],
    );
  };

  const handleConfirmSelected = async () => {
    for (const id of selectedIds) {
      await fetch(`${API_BASE}/matching/confirm/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ customerId: '', organizationId: ORG_ID }),
      });
    }
    setSelectedIds([]);
    const r = await fetch(`${API_BASE}/bank-movements/${ORG_ID}`);
    setMovements(await r.json());
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--color-text-secondary)]">Cargando movimientos...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Conciliacion</h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Revisa y confirma los pagos identificados por el sistema
        </p>
      </div>

      <div className="flex gap-1 rounded-lg border border-[var(--color-border)] bg-[var(--color-surface)] p-1">
        {(['pending', 'identified', 'reconciled'] as TabType[]).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab
                ? 'bg-[var(--color-primary)] text-[var(--color-primary-foreground)]'
                : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]'
            }`}
          >
            {tab === 'pending' ? 'Pendientes' : tab === 'identified' ? 'Identificados' : 'Confirmados'} ({tabCounts[tab]})
          </button>
        ))}
      </div>

      {activeTab === 'pending' && selectedIds.length > 0 && (
        <div className="flex items-center justify-between rounded-xl border border-[var(--color-primary)] bg-[var(--color-primary)]/5 p-4">
          <span className="text-sm">{selectedIds.length} movimiento(s) seleccionado(s)</span>
          <div className="flex gap-2">
            <button
              onClick={handleConfirmSelected}
              className="rounded-lg bg-[var(--color-primary)] px-4 py-2 text-sm font-medium text-[var(--color-primary-foreground)] hover:opacity-90"
            >
              Confirmar seleccion
            </button>
            <button
              onClick={() => setSelectedIds([])}
              className="rounded-lg border border-[var(--color-border)] px-4 py-2 text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
            >
              Limpiar
            </button>
          </div>
        </div>
      )}

      <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
        <div className="divide-y divide-[var(--color-border)]">
          {filteredMovements.length === 0 ? (
            <div className="px-6 py-12 text-center text-[var(--color-text-secondary)]">
              No hay movimientos en esta categoria
            </div>
          ) : (
            filteredMovements.map((movement) => {
              const statusInfo = STATUS_CONFIG[movement.status] || STATUS_CONFIG.pending;
              return (
                <div
                  key={movement.id}
                  className={`flex items-center gap-4 px-6 py-4 ${
                    selectedIds.includes(movement.id) ? 'bg-[var(--color-primary)]/5' : ''
                  }`}
                >
                  {activeTab === 'pending' && (
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(movement.id)}
                      onChange={() => toggleSelect(movement.id)}
                      className="h-5 w-5 rounded border-[var(--color-border)] accent-[var(--color-primary)]"
                    />
                  )}

                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <p className="font-medium">{movement.description}</p>
                      <span className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${statusInfo.color}`}>
                        {statusInfo.label}
                      </span>
                    </div>
                    <p className="text-sm text-[var(--color-text-secondary)]">{movement.date}</p>
                  </div>

                  <div className="text-right">
                    <p className={`font-medium ${movement.movementType === 'credit' ? 'text-green-400' : 'text-red-400'}`}>
                      {movement.movementType === 'credit' ? '+' : '-'}{formatCurrency(movement.amount)}
                    </p>
                    <p className="text-xs text-[var(--color-text-tertiary)]">Saldo: {formatCurrency(movement.balance)}</p>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}