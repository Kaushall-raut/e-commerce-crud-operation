import { HttpErrorResponse } from '@angular/common/http';

export function apiErrorMessage(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    const detail: unknown = error.error?.detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      const messages = detail.map((entry: { msg?: string; loc?: unknown[] }) => {
        const field = Array.isArray(entry.loc) ? entry.loc[entry.loc.length - 1] : undefined;
        return `${field ? `${String(field)}: ` : ''}${entry.msg ?? 'Invalid value'}`;
      });
      if (messages.length) return messages.join(' · ');
    }
    if (error.status === 0) return 'Cannot reach the API. Check that FastAPI is running at 127.0.0.1:8000.';
    if (error.status === 404) return 'The requested record was not found.';
    if (error.status === 409) return typeof detail === 'string' ? detail : 'This change conflicts with existing order or inventory data.';
    return `Request failed (${error.status}). Please try again.`;
  }
  return 'Something went wrong. Please try again.';
}
