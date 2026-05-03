import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export {
  calculateDistance,
  debounce,
  formatDate,
  formatDistance,
  formatFileSize,
  formatPercentScore,
  formatRelativeTime,
  generateId,
  getSeverityColor,
  getStatusColor,
  isEmpty,
  normalizePercentScore,
  sleep,
  truncate,
} from './utils/index';
