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
    label: 'Upload Data',
    iconName: 'UploadCloud',
    description: 'Multi-source batch uploads (50+ records)'
  },
  {
    path: '/history',
    label: 'History',
    iconName: 'History',
    description: 'Audit trails & batch reconciliation logs'
  },
  {
    path: '/reports',
    label: 'Reports',
    iconName: 'FileText',
    description: 'Financial audit reports & analytics exports'
  },
  {
    path: '/settings',
    label: 'Settings',
    iconName: 'Settings',
    description: 'Tolerances, endpoints & rules'
  }
];

export const STATUS_COLORS = {
  MATCHED: {
    bg: 'bg-emerald-500/10',
    border: 'border-emerald-500/30',
    text: 'text-emerald-400',
    badge: 'emerald',
    hex: '#10b981'
  },
  REVIEW: {
    bg: 'bg-amber-500/10',
    border: 'border-amber-500/30',
    text: 'text-amber-400',
    badge: 'amber',
    hex: '#f59e0b'
  },
  EXCEPTION: {
    bg: 'bg-rose-500/10',
    border: 'border-rose-500/30',
    text: 'text-rose-400',
    badge: 'rose',
    hex: '#f43f5e'
  }
};

export const SEVERITY_COLORS = {
  CRITICAL: {
    bg: 'bg-rose-500/15',
    border: 'border-rose-500/40',
    text: 'text-rose-400',
    dot: 'bg-rose-500'
  },
  HIGH: {
    bg: 'bg-orange-500/15',
    border: 'border-orange-500/40',
    text: 'text-orange-400',
    dot: 'bg-orange-500'
  },
  MEDIUM: {
    bg: 'bg-amber-500/15',
    border: 'border-amber-500/40',
    text: 'text-amber-400',
    dot: 'bg-amber-500'
  },
  LOW: {
    bg: 'bg-blue-500/15',
    border: 'border-blue-500/40',
    text: 'text-blue-400',
    dot: 'bg-blue-500'
  }
};
