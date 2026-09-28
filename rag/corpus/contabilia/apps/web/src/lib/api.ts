const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api/v1';
const ORG_ID = 'default';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${body}`);
  }
  return res.json();
}

// Dashboard
export const getDashboardStats = () => apiFetch<DashboardStats>(`/dashboard/stats/${ORG_ID}`);
export const getDashboardWeekly = () => apiFetch<{ weeklyData: WeeklyDay[] }>(`/dashboard/weekly/${ORG_ID}`);

// Customers
export const getCustomers = () => apiFetch<Customer[]>(`/customers/${ORG_ID}`);
export const getCustomerInvoices = (customerId: string) =>
  apiFetch<Invoice[]>(`/customers/${ORG_ID}/${customerId}/invoices`);

// Bank movements
export const getMovements = (status?: string) => {
  const qs = status ? `?status=${status}` : '';
  return apiFetch<Movement[]>(`/bank-movements/${ORG_ID}${qs}`);
};

// Ingestion
export const uploadFile = async (file: File, type: 'invoices' | 'bank'): Promise<UploadResult> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('organizationId', ORG_ID);
  const endpoint = type === 'invoices' ? '/ingestion/invoices' : '/ingestion/bank-statements';
  const res = await fetch(`${API_BASE}${endpoint}`, { method: 'POST', body: formData });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new Error(`Upload error ${res.status}: ${body}`);
  }
  return res.json();
};

// Matching
export const confirmMatch = (movementId: string, customerId: string) =>
  apiFetch(`/matching/confirm/${movementId}`, {
    method: 'POST',
    body: JSON.stringify({ customerId, organizationId: ORG_ID }),
  });

export const runMatching = (bankStatementId?: string) =>
  apiFetch('/matching/run', {
    method: 'POST',
    body: JSON.stringify({ organizationId: ORG_ID, bankStatementId }),
  });

export { API_BASE, ORG_ID };
// Types
export interface DashboardStats {
  totalCustomers: number;
  totalInvoices: number;
  pendingInvoices: number;
  overdueInvoices: number;
  paidInvoices: number;
  totalInvoiced: number;
  totalPending: number;
  totalPaid: number;
  totalMovements: number;
  identifiedMovements: number;
  unmatchedMovements: number;
  automationRate: number;
}

export interface WeeklyDay {
  day: string;
  reconciled: number;
  pending: number;
}

export interface Customer {
  id: string;
  name: string;
  rut: string;
  pendingInvoices: number;
  totalPending: number;
  totalInvoiced: number;
  invoiceCount: number;
  lastPayment: string | null;
}

export interface Invoice {
  id: string;
  number: string;
  amount: number;
  total: number;
  balance: number;
  issueDate: string;
  dueDate: string;
  status: string;
}

export interface Movement {
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

export interface UploadResult {
  success: boolean;
  fileName: string;
  totalRows: number;
  created: number;
  data: Record<string, string | number>[];
}