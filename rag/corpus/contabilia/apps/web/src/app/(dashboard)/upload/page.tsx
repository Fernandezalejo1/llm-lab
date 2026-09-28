'use client';

import { useState, useCallback } from 'react';
import Link from 'next/link';
import { uploadFile, type UploadResult } from '@/lib/api';
import { FileText, CreditCard, Upload, CheckCircle, AlertCircle, ArrowLeft } from 'lucide-react';
import { cn } from '@/lib/utils';

type UploadStep = 'select' | 'uploading' | 'preview' | 'done';

export default function UploadPage() {
  const [step, setStep] = useState<UploadStep>('select');
  const [fileType, setFileType] = useState<'invoices' | 'bank' | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFile = useCallback(async (selectedFile: File) => {
    if (!fileType) return;
    setFile(selectedFile);
    setStep('uploading');
    setError(null);

    try {
      const res = await uploadFile(selectedFile, fileType);
      setResult(res);
      setStep('preview');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error desconocido');
      setStep('select');
    }
  }, [fileType]);

  const handleReset = () => {
    setStep('select');
    setFileType(null);
    setFile(null);
    setResult(null);
    setError(null);
  };

  const handleConfirm = () => {
    setStep('done');
  };

  const columns = result?.data?.[0] ? Object.keys(result.data[0]) : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Cargar datos</h1>
        <p className="text-sm text-[var(--color-text-secondary)]">
          Sube tus facturas pendientes o extractos bancarios para conciliar
        </p>
      </div>

      {/* Step: Select file type */}
      {step === 'select' && !fileType && (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          <button
            onClick={() => setFileType('invoices')}
            className="group rounded-xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-8 text-left transition-all hover:border-[var(--color-primary)] hover:bg-[var(--color-primary)]/5"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--color-primary)]/10 group-hover:bg-[var(--color-primary)]/20">
              <FileText className="h-6 w-6 text-[var(--color-primary)]" />
            </div>
            <h3 className="text-lg font-semibold">Facturas pendientes</h3>
            <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
              Excel o CSV con: cliente, RUT, numero de factura, importe, fecha, saldo pendiente
            </p>
            <p className="mt-3 text-xs text-[var(--color-text-tertiary)]">Formatos: CSV, XLSX, XLS</p>
          </button>

          <button
            onClick={() => setFileType('bank')}
            className="group rounded-xl border-2 border-[var(--color-border)] bg-[var(--color-surface)] p-8 text-left transition-all hover:border-[var(--color-info)] hover:bg-[var(--color-info)]/5"
          >
            <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--color-info)]/10 group-hover:bg-[var(--color-info)]/20">
              <CreditCard className="h-6 w-6 text-[var(--color-info)]" />
            </div>
            <h3 className="text-lg font-semibold">Extracto bancario</h3>
            <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
              Excel o CSV con: fecha, descripcion, referencia, cargo, abono
            </p>
            <p className="mt-3 text-xs text-[var(--color-text-tertiary)]">Formatos: CSV, XLSX, XLS</p>
          </button>
        </div>
      )}

      {/* Step: Upload file */}
      {step === 'select' && fileType && (
        <div className="space-y-4">
          <button
            onClick={() => setFileType(null)}
            className="flex items-center gap-2 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text)]"
          >
            <ArrowLeft className="h-4 w-4" />
            Cambiar tipo
          </button>

          <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-6">
            <h3 className="mb-4 font-semibold">
              Subir {fileType === 'invoices' ? 'facturas' : 'extracto bancario'}
            </h3>

            <div className="rounded-lg border-2 border-dashed border-[var(--color-border)] p-12 text-center hover:border-[var(--color-primary)]/50 transition-colors">
              <input
                type="file"
                accept=".csv,.xlsx,.xls"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFile(f);
                }}
                className="hidden"
                id="file-upload"
              />
              <label htmlFor="file-upload" className="cursor-pointer">
                <Upload className="mx-auto mb-4 h-10 w-10 text-[var(--color-text-tertiary)]" />
                <p className="mb-2 text-[var(--color-text-secondary)]">
                  <span className="font-medium text-[var(--color-primary)]">Click para seleccionar</span> o arrastra un archivo
                </p>
                <p className="text-xs text-[var(--color-text-tertiary)]">CSV, XLSX o XLS (max 10MB)</p>
              </label>
            </div>

            {error && (
              <div className="mt-4 flex items-center gap-2 rounded-lg bg-[var(--color-error)]/10 p-4 text-sm text-[var(--color-error)]">
                <AlertCircle className="h-4 w-4 shrink-0" />
                {error}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step: Uploading */}
      {step === 'uploading' && (
        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-12 text-center">
          <div className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-2 border-[var(--color-primary)] border-t-transparent" />
          <p className="text-[var(--color-text-secondary)]">Procesando archivo...</p>
          {file && <p className="mt-1 text-xs text-[var(--color-text-tertiary)]">{file.name}</p>}
        </div>
      )}

      {/* Step: Preview */}
      {step === 'preview' && result && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold">Vista previa</h3>
              <p className="text-sm text-[var(--color-text-secondary)]">
                {result.totalRows} registros encontrados, {result.created} creados en base de datos
              </p>
            </div>
            <div className="flex gap-2">
              <button
                onClick={handleReset}
                className="rounded-lg border border-[var(--color-border)] px-4 py-2 text-sm text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
              >
                Cancelar
              </button>
              <button
                onClick={handleConfirm}
                className="rounded-lg bg-[var(--color-primary)] px-4 py-2 text-sm font-medium text-black hover:opacity-90"
              >
                Continuar
              </button>
            </div>
          </div>

          <div className="overflow-x-auto rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)]">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)]">
                  {columns.map((col) => (
                    <th key={col} className="px-4 py-3 text-left font-medium text-[var(--color-text-secondary)]">
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--color-border)]">
                {result.data.slice(0, 10).map((row, i) => (
                  <tr key={i} className="hover:bg-[var(--color-surface-hover)]">
                    {columns.map((col) => (
                      <td key={col} className="px-4 py-3 text-[var(--color-text)]">
                        {String(row[col] ?? '')}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            {result.data.length > 10 && (
              <div className="border-t border-[var(--color-border)] px-4 py-3 text-sm text-[var(--color-text-secondary)]">
                Mostrando 10 de {result.data.length} registros
              </div>
            )}
          </div>
        </div>
      )}

      {/* Step: Done */}
      {step === 'done' && result && (
        <div className="rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-[var(--color-success)]/10">
            <CheckCircle className="h-8 w-8 text-[var(--color-success)]" />
          </div>
          <h2 className="text-2xl font-bold">Datos importados</h2>
          <p className="mt-2 text-[var(--color-text-secondary)]">
            {result.created} registros creados de {result.totalRows} en el archivo
          </p>
          <p className="mt-1 text-sm text-[var(--color-text-tertiary)]">
            {file?.name}
          </p>
          <div className="mt-6 flex justify-center gap-4">
            <Link
              href="/reconcile"
              className="rounded-lg bg-[var(--color-primary)] px-6 py-3 font-medium text-black hover:opacity-90"
            >
              Ir a conciliacion
            </Link>
            <button
              onClick={handleReset}
              className="rounded-lg border border-[var(--color-border)] px-6 py-3 text-[var(--color-text-secondary)] hover:bg-[var(--color-surface-hover)]"
            >
              Cargar otro archivo
            </button>
          </div>
        </div>
      )}
    </div>
  );
}