/**
 * Formatting utility functions for finance metrics and dates.
 */

export const formatCurrency = (amount, currency = 'USD') => {
  if (amount === null || amount === undefined || isNaN(amount)) return '--';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(amount);
};

export const formatPercent = (value, decimals = 1) => {
  if (value === null || value === undefined || isNaN(value)) return '--%';
  return `${Number(value).toFixed(decimals)}%`;
};

export const formatNumber = (value) => {
  if (value === null || value === undefined || isNaN(value)) return '--';
  return new Intl.NumberFormat('en-US').format(value);
};

export const formatTimestamp = (dateInput) => {
  if (!dateInput) return '--';
  const date = new Date(dateInput);
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date);
};
