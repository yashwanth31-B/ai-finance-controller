import React from 'react';
import PageHeader from '../components/PageHeader';
import PlaceholderCard from '../components/PlaceholderCard';
import { FileText } from 'lucide-react';

export const Reports = () => {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Financial Audit Reports & Analytics"
        description="Exportable reconciliation summary reports, compliance audit trails, and PDF analytics."
      />
      <PlaceholderCard
        title="Audit Reports Module"
        description="Comprehensive PDF/CSV report generation and automated compliance export pipelines will be integrated in upcoming evaluation phases."
        icon={FileText}
        badge="Phase 9"
      />
    </div>
  );
};

export default Reports;
