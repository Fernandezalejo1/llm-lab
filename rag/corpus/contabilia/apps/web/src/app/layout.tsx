import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Contabilia - Conciliación Bancaria Automatizada',
  description: 'Automatiza la identificación de pagos, aplicación de cobros y conciliación bancaria',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es" className="dark">
      <body>{children}</body>
    </html>
  );
}
