'use client';

import { useEffect, useState } from 'react';
import { formatCurrency } from '@/lib/utils';

const API_BASE = 'http://localhost:3001/api/v1';
const ORG_ID = 'default';

interface Customer {
  id: string;
  name: string;
  rut: string;
  pendingInvoices: number;
  totalPending: number;
  totalInvoiced: number;
  invoiceCount: number;
  lastPayment: string | null;
}

interface Invoice {
  id: string;
  number: string;
  amount: number;
  total: number;
  balance: number;
  issueDate: string;
  dueDate: string;
  status: string;
}

export default function AccountsPage() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/customers/${ORG_ID}`)
      .then((r) => r.json())
      .then((data) => setCustomers(data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (!selectedCustomer) {
      setInvoices([]);
      return;
    }
    fetch(`${API_BASE}/customers/${ORG_ID}/${selectedCustomer.id}/invoices`)
      .then((r) => r.json())
      .then((data) => setInvoices(data))
      .catch(console.error);
  }, [selectedCustomer]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-[var(--color-text-secondary)]">Cargando clientes...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Estado de cuenta</h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Vista por cliente con facturas pendientes y pagos aplicados
        </p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
          <div className="border-b border-[var(--color-border)] px-6 py-4">
            <h2 className="font-semibold">Clientes ({customers.length})</h2>
          </div>
          <div className="divide-y divide-[var(--color-border)]">
            {customers.map((customer) => (
              <button
                key={customer.id}
                onClick={() => setSelectedCustomer(customer)}
                className={`w-full px-6 py-4 text-left transition-colors ${
                  selectedCustomer?.id === customer.id ? 'bg-[var(--color-primary)]/5' : 'hover:bg-[var(--color-surface-hover)]'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">{customer.name}</p>
                    <p className="text-sm text-[var(--color-text-secondary)]">RUT: {customer.rut}</p>
                  </div>
                  <div className="text-right">
                    <p className="font-medium text-[var(--color-warning)]">{formatCurrency(customer.totalPending)}</p>
                    <p className="text-xs text-[var(--color-text-tertiary)]">{customer.pendingInvoices} facturas</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="lg:col-span-2">
          {selectedCustomer ? (
            <div className="space-y-4">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
                <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
                  <p className="text-sm text-[var(--color-text-secondary)]">Total pendiente</p>
                  <p className="mt-1 text-2xl font-bold text-[var(--color-warning)]">
                    {formatCurrency(selectedCustomer.totalPending)}
                  </p>
                </div>
                <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
                  <p className="text-sm text-[var(--color-text-secondary)]">Total facturado</p>
                  <p className="mt-1 text-2xl font-bold text-[var(--color-text)]">
                    {formatCurrency(selectedCustomer.totalInvoiced)}
                  </p>
                </div>
                <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
                  <p className="text-sm text-[var(--color-text-secondary)]">Ultimo pago</p>
                  <p className="mt-1 text-lg font-medium">
                    {selectedCustomer.lastPayment || 'Sin pagos'}
                  </p>
                </div>
              </div>

              <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
                <div className="border-b border-[var(--color-border)] px-6 py-4">
                  <h3 className="font-semibold">Facturas ({invoices.length})</h3>
                </div>
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[var(--color-border)] text-left text-sm text-[var(--color-text-secondary)]">
                      <th className="px-6 py-3 font-medium">Factura</th>
                      <th className="px-6 py-3 font-medium">Monto</th>
                      <th className="px-6 py-3 font-medium">Saldo</th>
                      <th className="px-6 py-3 font-medium">Vencimiento</th>
                      <th className="px-6 py-3 font-medium">Estado</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[var(--color-border)]">
                    {invoices.map((invoice) => (
                      <tr key={invoice.id} className="hover:bg-[var(--color-surface-hover)]">
                        <td className="px-6 py-3 font-medium">{invoice.number}</td>
                        <td className="px-6 py-3">{formatCurrency(invoice.amount)}</td>
                        <td className="px-6 py-3 font-medium">{formatCurrency(invoice.balance)}</td>
                        <td className="px-6 py-3 text-[var(--color-text-secondary)]">{invoice.dueDate}</td>
                        <td className="px-6 py-3">
                          <span
                            className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                              invoice.status === 'paid'
                                ? 'bg-green-500/10 text-green-400'
                                : invoice.status === 'overdue'
                                ? 'bg-red-500/10 text-red-400'
                                : 'bg-blue-500/10 text-blue-400'
                            }`}
                          >
                            {invoice.status === 'paid'
                              ? 'Pagada'
                              : invoice.status === 'overdue'
                              ? 'Vencida'
                              : 'Pendiente'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="flex h-64 items-center justify-center rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
              <p className="text-[var(--color-text-secondary)]">Selecciona un cliente para ver su estado de cuenta</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}