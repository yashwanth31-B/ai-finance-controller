/**
 * Navigation routes and application constants.
 */

export const NAV_ITEMS = [
  {
    path: '/',
    label: 'Dashboard',
    iconName: 'LayoutDashboard',
    description: 'Executive overview & reconciliation KPIs'
  },
  {
    path: '/reconciliation',
    label: 'Reconciliation',
    iconName: 'GitCompare',
    description: '3-way multi-source matching engine'
  },
  {
    path: '/exceptions',
    label: 'Exceptions',
    iconName: 'AlertTriangle',
    description: 'Unresolved discrepancy management'
  },
  {
    path: '/upload',
    label: 'Data Ingestion',
    iconName: 'UploadCloud',
    description: 'Multi-source batch uploads (50+ records)'
  },
  {
    path: '/history',
    label: 'Run History',
    iconName: 'History',
    description: 'Audit trails & batch reconciliation logs'
  },
  {
    path: '/settings',
    label: 'Settings',
    iconName: 'Settings',
    description: 'Tolerances, endpoints & rules'
  }
];

export const DATA_SOURCES = [
  {
    id: 'invoices',
    name: 'Invoice Systems',
    type: 'ERP / Billing',
    badge: 'Source 1',
    description: 'Accounts receivable & payable invoice ledgers'
  },
  {
    id: 'bank',
    name: 'Bank Transactions',
    type: 'Core Banking',
    badge: 'Source 2',
    description: 'Direct feeds, MT940 / CAMT / CSV bank statements'
  },
  {
    id: 'gateways',
    name: 'Payment Gateways',
    type: 'Settlement',
    badge: 'Source 3',
    description: 'Razorpay, Stripe & processor settlement records'
  }
];
