import type { AppMenuItem, AppMenuL3Item } from './types'

type MenuDomainInput = {
  id: string
  label: string
  path: string
  icon: string
  children: Array<{
    id: string
    label: string
    path: string
    status?: AppMenuL3Item['status']
    l3: string[]
    mappedExistingModule?: string
  }>
}

function l3Items(labels: string[], mappedExistingModule?: string, status: AppMenuL3Item['status'] = 'planned'): AppMenuL3Item[] {
  return labels.map((label, index) => ({
    id: `${label.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}-${index + 1}`,
    label,
    status,
    mappedExistingModule,
    disabled: status !== 'implemented' && status !== 'mapped',
  }))
}

const domains: MenuDomainInput[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    path: '/dashboard',
    icon: 'D',
    children: [
      { id: 'workspace-overview', label: 'Workspace Overview', path: '/dashboard', status: 'mapped', l3: ['Workspace Risk Signal', 'Role Workspace Context', 'Assigned Workspace Actions', 'Workspace Health Readiness', 'Workspace Evidence Pack', 'Workspace Governance Audit'] },
      { id: 'dashboard-executive', label: 'Executive Overview', path: '/dashboard', status: 'mapped', l3: ['Portfolio Overview', 'Site Health', 'Critical Alarms', 'Open Faults', 'Open Work Orders', 'Energy Exceptions', 'ESG Snapshot', 'Service Risk', 'Customer Delivery View'] },
      { id: 'dashboard-operations', label: 'Operations Snapshot', path: '/dashboard', status: 'mapped', l3: ["Today's Operations", 'Live Situation', 'Risk Summary', 'System Availability', 'Fault Impact', 'Maintenance Status', 'Energy Status', 'Compliance Status'] },
      { id: 'portfolio-operations', label: 'Portfolio Operations', path: '/dashboard', status: 'mapped', l3: ['Portfolio Risk Signal', 'Cross-site Context Map', 'SLA Exposure Actions', 'Partner Exposure Governance', 'Portfolio Evidence Pack', 'Portfolio Readiness Quality'] },
      { id: 'industry-view', label: 'Industry View', path: '/dashboard', status: 'mapped', l3: ['Active Industry Context', 'Scenario Risk Signals', 'Industry KPI Actions', 'Industry Risk Governance', 'Industry Evidence Pack', 'Industry Readiness Quality'] },
      { id: 'customer-success', label: 'Customer Success', path: '/dashboard', status: 'mapped', l3: ['Customer Health Signal', 'Delivery Milestone Context', 'Acceptance Workflow Actions', 'Open Customer Risk Governance', 'Customer Evidence Pack', 'Success Readiness Quality'] },
      { id: 'service-risk', label: 'Service Risk', path: '/dashboard', status: 'mapped', l3: ['Service Risk Signal', 'Customer Impact Context', 'SLA Mitigation Actions', 'Risk Owner Governance', 'Service Risk Evidence', 'Recovery Readiness Quality'] },
      { id: 'partner-system-status', label: 'Partner System Status', path: '/dashboard', status: 'mapped', l3: ['Partner System Risk Signal', 'Connected System Context', 'Data Freshness Actions', 'Partner SLA Governance', 'Partner Evidence Pack', 'Integration Readiness Quality'] },
      { id: 'delivery-readiness', label: 'Delivery Readiness', path: '/dashboard', status: 'mapped', l3: ['Release Risk Signal', 'Package Context Map', 'Handoff Workflow Actions', 'Deployment Governance Audit', 'Delivery Evidence Pack', 'Readiness Quality Gate'] },
    ],
  },
  {
    id: 'command-center',
    label: 'Command Center',
    path: '/console/operations',
    icon: 'C',
    children: [
      { id: 'operations-command-center', label: 'Operations Console', path: '/console/operations', status: 'implemented', l3: ['Operations Board', 'Live Situation', 'Event Stream', 'Active Tasks', 'Escalations', 'Service Impact', 'Evidence Timeline', 'Decision Log'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'incident-management', label: 'Incident Management', path: '/console/operations', status: 'mapped', l3: ['Active Incidents', 'Incident Detail', 'Related Alarms', 'Related Faults', 'Impacted Assets', 'Response Actions', 'Communications', 'Closure Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'shift-management', label: 'Shift Management', path: '/console/operations', status: 'mapped', l3: ['Shift Risk Signal', 'Handover Context Notes', 'Open Item Actions', 'Critical Watchlist Governance', 'Operator Assignment Readiness', 'Shift Evidence Audit'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'service-impact', label: 'Service Impact', path: '/console/operations', status: 'mapped', l3: ['Customer Impact', 'Operational Impact', 'Affected Systems', 'Affected Assets', 'SLA Exposure', 'Recovery Priority', 'Impact Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'decision-log', label: 'Decision Log', path: '/ucde/evidence', status: 'mapped', l3: ['Decision Risk Signal', 'Decision Context Detail', 'Decision Owner Actions', 'Approval Chain Governance', 'Decision Evidence Pack', 'Export Readiness Audit'], mappedExistingModule: 'EvidenceCenter' },
    ],
  },
  {
    id: 'assets-locations',
    label: 'Assets & Locations',
    path: '/assets/topology',
    icon: 'A',
    children: [
      { id: 'site-portfolio', label: 'Site Portfolio', path: '/assets/topology', status: 'mapped', l3: ['Portfolio List', 'Site Health', 'Site Risk', 'Site Energy', 'Site Compliance', 'Site Reports'], mappedExistingModule: 'AssetsTopology' },
      { id: 'buildings-zones', label: 'Buildings / Floors / Zones', path: '/assets/topology', status: 'mapped', l3: ['Building Risk Signal', 'Floor Zone Context', 'Occupancy Action View', 'Zone Condition Governance', 'Zone Asset Evidence', 'Location Readiness Quality'], mappedExistingModule: 'AssetsTopology' },
      { id: 'space-mapping', label: 'Space Mapping', path: '/assets/topology', status: 'mapped', l3: ['Asset-to-Space Mapping', 'System-to-Space Mapping', 'Tag-to-Space Mapping', 'Floor Plan Binding', 'Mapping Gaps', 'Mapping Evidence'], mappedExistingModule: 'AssetsTopology' },
      { id: 'system-registry', label: 'System Registry', path: '/assets/topology', status: 'mapped', l3: ['System List', 'System Topology', 'System Health', 'System Alarms', 'System Faults', 'System Evidence', 'System Reports'], mappedExistingModule: 'AssetsTopology' },
      { id: 'asset-registry', label: 'Asset Registry', path: '/one/assets/context', status: 'implemented', l3: ['Asset List', 'Asset Detail', 'Asset Context', 'Asset Relationships', 'Asset Health', 'Asset History', 'Asset Evidence'], mappedExistingModule: 'AssetContext' },
      { id: 'equipment', label: 'Equipment', path: '/assets/topology', status: 'mapped', l3: ['Equipment List', 'Equipment Detail', 'Runtime Status', 'Maintenance History', 'Fault History', 'Spare / Vendor Info', 'Evidence'], mappedExistingModule: 'AssetsTopology' },
      { id: 'points-tags', label: 'Points & Tags', path: '/assets/topology', status: 'mapped', l3: ['Point List', 'Tag Mapping', 'Live Values', 'Point Quality', 'Point Trends', 'Mapping Gaps', 'Import / Export'], mappedExistingModule: 'AssetsTopology' },
      { id: 'controllers-gateways', label: 'Controllers & Gateways', path: '/uedge/diagnostics', status: 'mapped', l3: ['Controller List', 'Gateway List', 'Connectivity Status', 'Protocol Status', 'Edge Gateway Mapping', 'Link Gateway Mapping', 'Diagnostics'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'asset-graph', label: 'Asset Graph', path: '/one/assets/context', status: 'implemented', l3: ['Relationship Graph', 'Dependency View', 'Impact Path', 'Upstream / Downstream', 'Asset Context Projection', 'Evidence Links', 'Data Quality'], mappedExistingModule: 'AssetContext' },
      { id: 'floor-plan-hmi', label: 'Floor Plan / HMI Map', path: '/one/airport/assets-topology', status: 'mapped', l3: ['Floor Plan Risk Signal', 'Site Building Context', 'Zone Overlay Actions', 'Asset Alarm Relationship', 'Energy Overlay Evidence', 'HMI Map Readiness Audit'] },
      { id: 'digital-twin', label: 'Digital Twin', path: '/one/airport/assets-topology', status: 'mapped', l3: ['Twin Risk Signal', 'Asset System Context', 'Space Twin Relationship', 'Fault Impact Actions', 'Scenario Governance', 'Twin Evidence Readiness'] },
      { id: 'security-life-safety-assets', label: 'Security & Life Safety Assets', path: '/one/airport/overview', status: 'mapped', l3: ['Access Events', 'Door Status', 'CCTV Events', 'Fire System Status', 'Life Safety Events', 'Security Evidence', 'Compliance Reports'] },
      { id: 'data-center-assets', label: 'Data Center Assets', path: '/one/airport/overview', status: 'mapped', l3: ['Data Hall Health', 'Power Chain', 'Cooling Chain', 'Environmental Status', 'Capacity Risk', 'Critical Alarms', 'IDC Reports'] },
    ],
  },
  {
    id: 'work-management',
    label: 'Work Management',
    path: '/one/umms/workspace',
    icon: 'W',
    children: [
      { id: 'work-orders', label: 'Work Orders', path: '/one/umms/workspace', status: 'implemented', l3: ['Open Work Orders', 'Assigned Work Orders', 'Emergency Work Orders', 'Fault-linked Work Orders', 'Preventive Work Orders', 'Corrective Work Orders', 'Work Order Detail', 'Closure Evidence'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'preventive-maintenance', label: 'Preventive Maintenance', path: '/one/umms/workspace', status: 'implemented', l3: ['PM Calendar', 'PM Templates', 'PM Schedule', 'PM Checklist', 'PM Completion', 'PM Evidence', 'PM Reports'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'corrective-maintenance', label: 'Corrective Maintenance', path: '/one/umms/workspace', status: 'implemented', l3: ['Fault-linked Work Orders', 'Manual Work Orders', 'Technician Assignment', 'Action Tracking', 'Parts / Vendor Notes', 'Closure Review', 'History'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'engineer-workload', label: 'Engineer Workload', path: '/one/umms/workspace', status: 'implemented', l3: ['Engineer Calendar', 'Assignment Load', 'Skill / Discipline', 'Shift Availability', 'Escalation Owner', 'Next Due', 'Workload Evidence'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'sla-escalation', label: 'SLA & Escalation', path: '/one/umms/workspace', status: 'implemented', l3: ['SLA Dashboard', 'Breach Risk', 'Escalation Queue', 'Supervisor Review', 'Customer Impact', 'SLA Evidence', 'Aging Buckets'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'maintenance-analytics', label: 'Maintenance Analytics', path: '/one/umms/workspace', status: 'implemented', l3: ['MTTR', 'MTBF', 'Repeated Failures', 'Technician Load', 'Asset Reliability', 'Predictive Risk', 'Improvement Plan'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'inventory', label: 'Inventory', path: '/one/umms/workspace', status: 'mapped', l3: ['Stock Risk Signal', 'Spare Part Context', 'Material Request Actions', 'Critical Spare Governance', 'Inventory Evidence Pack', 'Supply Readiness Quality'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'vendors', label: 'Vendors', path: '/one/umms/workspace', status: 'mapped', l3: ['Vendor Risk Signal', 'Contract Coverage Context', 'Service Level Actions', 'Warranty Governance', 'Vendor Evidence Pack', 'Vendor Readiness Quality'], mappedExistingModule: 'UmmsMaintenance' },
      { id: 'maintenance-configuration', label: 'Maintenance Configuration', path: '/one/umms/workspace', status: 'implemented', l3: ['Work Order Types', 'Priority Matrix', 'Assignment Rules', 'Checklist Templates', 'SLA Rules', 'Vendor / Team Setup', 'Evidence Rules'], mappedExistingModule: 'UmmsMaintenance' },
    ],
  },
  {
    id: 'faults-events',
    label: 'Faults & Events',
    path: '/one/airport/alarms-events',
    icon: 'F',
    children: [
      { id: 'alarm-console', label: 'Alarm Console', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Active Alarms', 'Critical Alarms', 'Acknowledgement', 'Shelving', 'Suppression', 'Escalation', 'Operator Notes'] },
      { id: 'event-timeline', label: 'Event Timeline', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Event Stream', 'Event Filters', 'Event Detail', 'Related Assets', 'Related Faults', 'Related Work Orders', 'Evidence Timeline'] },
      { id: 'alarm-rules', label: 'Alarm Rules', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Priority Rules', 'Escalation Rules', 'Notification Rules', 'Suppression Rules', 'Routing Rules', 'Rule Evidence', 'Rule Audit'] },
      { id: 'alarm-analytics', label: 'Alarm Analytics', path: '/one/airport/alarms-events', status: 'mapped', l3: ['Alarm Volume', 'Alarm Flood', 'Repeated Alarms', 'Nuisance Alarms', 'Top Assets', 'Top Systems', 'SLA Impact'] },
      { id: 'fault-console', label: 'Fault Console', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Active Faults', 'Critical Faults', 'Fault Detail', 'Correlation', 'Root Cause Analysis', 'Recommended Actions', 'Fault Evidence'] },
      { id: 'detection-correlation', label: 'Detection & Correlation', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Detection Rules', 'Correlation Rules', 'Event Clustering', 'Related Alarms', 'Related Assets', 'Confidence Score', 'Rule Evidence'] },
      { id: 'diagnostics', label: 'Diagnostics', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Diagnostic Queue', 'System Diagnostics', 'Asset Diagnostics', 'OT / Network Diagnostics', 'Hardware Diagnostics', 'Diagnostic Evidence', 'Diagnostic History'] },
      { id: 'remediation', label: 'Remediation', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Recommended Actions', 'Manual Actions', 'Work Order Creation', 'Escalation', 'SLA Tracking', 'Closure Notes', 'Closure Evidence'] },
      { id: 'fault-analytics', label: 'Fault Analytics', path: '/one/airport/fault-cases', status: 'mapped', l3: ['Fault Trends', 'Top Fault Types', 'Repeat Faults', 'MTTR', 'Downtime Impact', 'Reliability Score', 'Improvement Actions'] },
      { id: 'event-evidence', label: 'Event Evidence', path: '/ucde/evidence', status: 'mapped', l3: ['Evidence Chain', 'UCDE Trace', 'Operator Actions', 'Export Package', 'Audit Trail'], mappedExistingModule: 'EvidenceCenter' },
    ],
  },
  {
    id: 'energy-sustainability',
    label: 'Energy & Sustainability',
    path: '/uesg/sustainability',
    icon: 'E',
    children: [
      { id: 'energy-dashboard', label: 'Energy Dashboard', path: '/uesg/sustainability', status: 'implemented', l3: ['Consumption Overview', 'Demand / Peak', 'Energy Intensity', 'Meter Health', 'Energy Exceptions', 'Energy Forecast', 'Energy Reports'], mappedExistingModule: 'UesgSustainability' },
      { id: 'metering', label: 'Metering', path: '/uesg/sustainability', status: 'mapped', l3: ['Meter Risk Signal', 'Meter Mapping Context', 'Reading Quality Actions', 'Meter Fault Governance', 'Meter Evidence Export', 'Meter Readiness Quality'], mappedExistingModule: 'UesgSustainability' },
      { id: 'energy-faults', label: 'Energy Faults', path: '/uesg/sustainability', status: 'mapped', l3: ['High Consumption', 'Unoccupied Consumption', 'Weekend Consumption', 'Peak Demand', 'Meter Offline', 'Meter Flatline', 'Energy Fault Evidence'], mappedExistingModule: 'UesgSustainability' },
      { id: 'sustainability', label: 'Sustainability', path: '/uesg/sustainability', status: 'implemented', l3: ['Carbon Overview', 'ESG Metrics', 'Green Mark Support', 'Utility Baseline', 'Reduction Initiatives', 'Sustainability Evidence', 'ESG Reports'], mappedExistingModule: 'UesgSustainability' },
      { id: 'optimization', label: 'Optimization', path: '/uesg/sustainability', status: 'mapped', l3: ['Energy Opportunities', 'Setpoint Review', 'Schedule Review', 'Equipment Efficiency', 'Anomaly Detection', 'Savings Estimate', 'Action Plan'], mappedExistingModule: 'UesgSustainability' },
      { id: 'energy-compliance', label: 'Compliance', path: '/uesg/sustainability', status: 'mapped', l3: ['Energy Compliance', 'ESG Compliance', 'Audit Evidence', 'Report Export', 'Submission Package', 'Historical Records'], mappedExistingModule: 'UesgSustainability' },
      { id: 'data-center-energy', label: 'Data Center Energy', path: '/uesg/sustainability', status: 'mapped', l3: ['UPS', 'PDU', 'Switchgear', 'Generator', 'Power Metering', 'Power Alarms', 'Power Trends'], mappedExistingModule: 'UesgSustainability' },
    ],
  },
  {
    id: 'data-intelligence',
    label: 'Data & Intelligence',
    path: '/one/assets/context',
    icon: 'I',
    children: [
      { id: 'data-model', label: 'Data Model', path: '/assets/topology', status: 'mapped', l3: ['Model Risk Signal', 'Canonical Object Context', 'Schema Action Workflow', 'Data Dictionary Governance', 'Model Evidence Pack', 'Schema Readiness Quality'], mappedExistingModule: 'AssetsTopology' },
      { id: 'data-lake', label: 'Data Lake', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Data Freshness Risk', 'Landing Store Context', 'Retention Action Workflow', 'Lineage Governance Audit', 'Data Quality Evidence', 'Lake Readiness Quality'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'asset-graph-intelligence', label: 'Asset Graph Intelligence', path: '/one/assets/context', status: 'implemented', l3: ['Relationship Graph', 'Dependency View', 'Impact Path', 'System-to-Asset Mapping', 'Asset-to-Point Mapping', 'Fault Impact Graph', 'Maintenance Impact Graph', 'Evidence-linked Graph'], mappedExistingModule: 'AssetContext' },
      { id: 'knowledge-base', label: 'Knowledge Base', path: '/one/nexus-ai/branch-audit', status: 'mapped', l3: ['Fault Knowledge', 'Maintenance Knowledge', 'Energy Knowledge', 'Asset Manuals', 'SOP Library', 'RCA Library', 'Troubleshooting Guides', 'Vendor Knowledge', 'Knowledge Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'ai-model-hub', label: 'AI Model Hub', path: '/one/nexus-ai/branch-audit', status: 'mapped', l3: ['Model Registry', 'Model Versioning', 'Fault Models', 'Energy Models', 'Maintenance Models', 'Risk Models', 'Model Evaluation', 'Human Approval', 'Model Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'nexusai', label: 'NexusAI Insights', path: '/one/nexus-ai/branch-audit', status: 'implemented', l3: ['Insight Overview', 'Fault Insights', 'Energy Insights', 'Maintenance Insights', 'Risk Insights', 'Branch Audit', 'AI Evidence'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'recommendations', label: 'Recommendations', path: '/one/nexus-ai/branch-audit', status: 'innovation', l3: ['Recommendation Risk Signal', 'Decision Support Context', 'Recommended Action Workflow', 'Human Approval Governance', 'Confidence Evidence Pack', 'Recommendation Readiness Quality'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'forecasting', label: 'Forecasting', path: '/one/nexus-ai/branch-audit', status: 'innovation', l3: ['Forecast Risk Signal', 'Capacity Forecast Context', 'Prediction Review Actions', 'Model Governance Audit', 'Forecast Evidence Pack', 'Forecast Readiness Quality'], mappedExistingModule: 'NexusBranchAudit' },
      { id: 'data-evidence-center', label: 'Evidence Center', path: '/ucde/evidence', status: 'implemented', l3: ['Evidence Chain', 'Source Evidence', 'Decision Evidence', 'Fault Evidence', 'Maintenance Evidence', 'Energy Evidence', 'Report Evidence', 'Hash / Signature', 'Export Evidence'], mappedExistingModule: 'EvidenceCenter' },
      { id: 'data-governance', label: 'Data Governance', path: '/system/audit-logs', status: 'mapped', l3: ['Data Ownership', 'Data Classification', 'Data Quality Rules', 'Access Policy', 'Retention Policy', 'Lineage Review', 'Data Audit', 'Governance Evidence'], mappedExistingModule: 'AuditLogsView' },
    ],
  },
  {
    id: 'reports-documents',
    label: 'Reports & Documents',
    path: '/reports',
    icon: 'R',
    children: [
      { id: 'report-center', label: 'Report Center', path: '/reports', status: 'implemented', l3: ['Report Risk Signal', 'Operations Report Context', 'Report Generation Actions', 'Report Governance Audit', 'Report Evidence Pack', 'Report Readiness Quality'], mappedExistingModule: 'ReportsView' },
      { id: 'export-center', label: 'Export Center', path: '/reports', status: 'implemented', l3: ['PDF Export', 'Excel Export', 'Evidence Bundle', 'Customer Handoff Package', 'Scheduled Exports', 'Export History', 'Export Audit'], mappedExistingModule: 'ReportsView' },
      { id: 'compliance-center', label: 'Compliance Center', path: '/reports', status: 'mapped', l3: ['IEC 62443 Evidence', 'ESG Evidence', 'Green Mark Evidence', 'Customer Acceptance', 'Audit Checklist', 'Compliance Gap', 'Compliance Reports'], mappedExistingModule: 'ReportsView' },
      { id: 'document-library', label: 'Document Library', path: '/reports', status: 'mapped', l3: ['Document Register', 'Drawing Library', 'O&M Manuals', 'Method Statements', 'Test Reports', 'Vendor Documents', 'Revision History', 'Document Evidence'], mappedExistingModule: 'ReportsView' },
      { id: 'drawing-bim-documents', label: 'Drawing & BIM Documents', path: '/one/airport/assets-topology', status: 'mapped', l3: ['As-built Drawings', 'Single Line Diagrams', 'Control Schematics', 'Floor Plans', 'BIM References', 'Drawing Approval', 'Drawing Evidence'] },
      { id: 'asset-document-binding', label: 'Asset Document Binding', path: '/one/assets/context', status: 'mapped', l3: ['Asset-linked Documents', 'System-linked Documents', 'Equipment Manuals', 'Warranty Certificates', 'Spare Parts Documents', 'Maintenance Procedures', 'Document-to-Asset Evidence'], mappedExistingModule: 'AssetContext' },
      { id: 'handover-package-docs', label: 'Handover Package', path: '/reports', status: 'mapped', l3: ['Customer Handover Index', 'FAT / SAT Records', 'Commissioning Records', 'Training Records', 'Acceptance Checklist', 'Export Package', 'Handover Evidence'], mappedExistingModule: 'ReportsView' },
      { id: 'document-governance', label: 'Document Governance', path: '/ucde/evidence', status: 'mapped', l3: ['Version Control', 'Approval Workflow', 'Access Control', 'Retention Policy', 'Change Request', 'Document Audit Trail', 'Signature / Hash'], mappedExistingModule: 'EvidenceCenter' },
    ],
  },
  {
    id: 'governance-security',
    label: 'Governance & Security',
    path: '/console/operations',
    icon: 'G',
    children: [
      { id: 'security-overview', label: 'Security Overview', path: '/console/operations', status: 'mapped', l3: ['Security Dashboard', 'Login Risk', 'Active Sessions', 'Privileged Users', 'Security Events', 'Policy Violations', 'Security Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'access-control', label: 'Access Control', path: '/system/permissions', status: 'implemented', l3: ['Users', 'Roles', 'Permissions', 'Teams', 'Workspace Access', 'Workspace Role Mapping', 'Workspace Permission Matrix', 'Workspace Audit', 'MFA / 2FA Policy', 'Session Policy', 'Access Review', 'Identity Audit'], mappedExistingModule: 'PermissionListView' },
      { id: 'policy-governance', label: 'Policy Governance', path: '/one/code/policy-gate', status: 'implemented', l3: ['Security Policies', 'Approval Policies', 'Data Access Policies', 'AI Usage Policies', 'Evidence Policies', 'Retention Policies', 'Policy Exceptions', 'Policy Audit'], mappedExistingModule: 'CodePolicyGate' },
      { id: 'compliance-control', label: 'Compliance Control', path: '/reports', status: 'mapped', l3: ['IEC 62443 Control Mapping', 'ISO 27001 Mapping', 'Cybersecurity Checklist', 'OT Security Baseline', 'Data Protection Review', 'Audit Readiness', 'Compliance Evidence'], mappedExistingModule: 'ReportsView' },
      { id: 'governance-audit-trail', label: 'Audit Trail', path: '/system/audit-logs', status: 'implemented', l3: ['Login Audit', 'User Action Audit', 'Configuration Audit', 'Data Access Audit', 'Report Export Audit', 'AI Decision Audit', 'Evidence Audit', 'Tamper Review'], mappedExistingModule: 'AuditLogsView' },
      { id: 'risk-control-register', label: 'Risk & Control Register', path: '/console/operations', status: 'mapped', l3: ['Risk Register', 'Control Register', 'Open Findings', 'Mitigation Actions', 'Responsible Owners', 'Review Schedule', 'Risk Evidence'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'cybersecurity-operations', label: 'Cybersecurity Operations', path: '/uedge/diagnostics', status: 'mapped', l3: ['Asset Vulnerability', 'Network Exposure', 'OT Security Events', 'Security Incident Queue', 'Threat Intelligence', 'Remediation Tracking', 'Cyber Evidence'], mappedExistingModule: 'UedgeDiagnostics' },
    ],
  },
  {
    id: 'integration-partner-hub',
    label: 'Integration & Partner Hub',
    path: '/uedge/setup',
    icon: 'P',
    children: [
      { id: 'integration-overview', label: 'Integration Overview', path: '/uedge/setup', status: 'mapped', l3: ['Integration Landscape', 'Connected Systems', 'Data Flow Status', 'Integration Risk', 'Partner SLA Exposure', 'Data Freshness', 'Integration Evidence'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'partner-registry', label: 'Partner Registry', path: '/console/operations', status: 'mapped', l3: ['Partner List', 'Partner Profile', 'System Ownership', 'Support Contact', 'SLA Ownership', 'Maintenance Window', 'Contract Evidence', 'Partner Risk'], mappedExistingModule: 'PlatformOperationsDashboard' },
      { id: 'connector-marketplace', label: 'Connector Marketplace', path: '/uedge/setup', status: 'mapped', l3: ['Available Connectors', 'Installed Connectors', 'Industry Connectors', 'Protocol Adapters', 'Connector Compatibility', 'Connector Health', 'Connector Version', 'Connector Approval', 'Connector Evidence'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'protocol-gateway-operations', label: 'Protocol & Gateway Operations', path: '/uedge/diagnostics', status: 'mapped', l3: ['BACnet Operations', 'Modbus Operations', 'OPC UA Operations', 'MQTT Operations', 'REST / Webhook Operations', 'SQL Read-only Source', 'File / Excel Import', 'SNMP / ONVIF Source', 'EDGE Gateway Mapping', 'LINK Gateway Mapping', 'Queue & Delivery', 'Offline Buffer', 'Gateway Diagnostics'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'data-onboarding', label: 'Data Onboarding', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Guided Onboarding', 'Source Registration', 'Data Contract', 'Field Mapping', 'Unit Mapping', 'Status Mapping', 'Severity Mapping', 'Timestamp Rule', 'Tag Mapping', 'Object Mapping', 'Validation Result', 'Mapping Gaps', 'Onboarding Evidence'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'industry-connectors', label: 'Industry Connectors', path: '/uedge/setup', status: 'mapped', l3: ['Building Systems', 'Shopping Mall Systems', 'Airport Systems', 'Data Center Systems', 'Oil & Gas Systems', 'Coking Plant Systems', 'Industrial Utility Systems', 'Multi-site Portfolio Systems'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'api-event-exchange', label: 'API & Event Exchange', path: '/uedge/diagnostics', status: 'mapped', l3: ['API Catalog', 'API Credentials', 'Webhook Subscriptions', 'Event Topics', 'Payload Monitor', 'Error Codes', 'Rate Limits', 'Partner Sandbox', 'API Test Console', 'API Audit'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'integration-testing-certification', label: 'Integration Testing & Certification', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Sandbox Test', 'Connectivity Test', 'Data Quality Test', 'Contract Test', 'Mapping Test', 'Load Test', 'Failover Test', 'Cyber Review', 'Production Readiness', 'Test Evidence'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'integration-health-observability', label: 'Integration Health & Observability', path: '/uedge/diagnostics', status: 'mapped', l3: ['Integration Health', 'Data Freshness', 'Queue Depth', 'Failure Rate', 'Latency Exposure', 'Error Trend', 'Partner SLA Exposure', 'Observability Evidence'], mappedExistingModule: 'UedgeDiagnostics' },
      { id: 'integration-governance', label: 'Integration Governance', path: '/system/audit-logs', status: 'mapped', l3: ['Integration Approval', 'Partner Access Review', 'Data Sharing Policy', 'Credential Governance', 'Security Review', 'Change History', 'Partner SLA Review', 'Integration Audit', 'Integration Evidence'], mappedExistingModule: 'AuditLogsView' },
    ],
  },
  {
    id: 'industry-solutions',
    label: 'Industry Solutions',
    path: '/dashboard',
    icon: 'S',
    children: [
      { id: 'industry-overview', label: 'Industry Overview', path: '/dashboard', status: 'mapped', l3: ['Active Industry Profile', 'Scenario Packages', 'Industry KPI Set', 'Industry Risk Model', 'Industry SLA Model', 'Industry Evidence Pack', 'Industry Readiness'] },
      { id: 'industry-package-manager', label: 'Industry Package Manager', path: '/dashboard', status: 'mapped', l3: ['Enabled Industry Packages', 'Industry KPI Configuration', 'Industry Risk Rules', 'Industry Report Pack', 'Industry Evidence Pack', 'Industry Connector Pack', 'Industry Playbooks', 'Industry Governance Rules'] },
      { id: 'commercial-building', label: 'Commercial Building', path: '/one/airport/overview', status: 'mapped', l3: ['Comfort & Occupancy', 'Tenant Service', 'Public Area Health', 'Lift / Escalator Operations', 'HVAC Performance', 'Building Energy Pack', 'Building Service Evidence'] },
      { id: 'shopping-mall', label: 'Shopping Mall', path: '/one/airport/overview', status: 'mapped', l3: ['Tenant Impact', 'Footfall & Service Risk', 'Public Safety', 'Parking & Access', 'Retail Metering', 'Lift / Escalator Downtime', 'Mall Operations Evidence'] },
      { id: 'airport', label: 'Airport', path: '/one/airport/overview', status: 'mapped', l3: ['Terminal Operations', 'Passenger Impact', 'Gate / Flight Impact', 'Baggage System Risk', 'Security Lane Risk', 'Airside / Landside Service Risk', 'Airport Partner Systems', 'Airport Evidence Pack'] },
      { id: 'data-center', label: 'Data Center', path: '/one/airport/overview', status: 'mapped', l3: ['Availability Overview', 'Power Chain Risk', 'Cooling & Thermal Risk', 'Rack & Capacity', 'PUE & Energy', 'Maintenance Window', 'DCIM / ITSM Integration', 'Uptime Evidence Pack'] },
      { id: 'oil-gas-plant', label: 'Oil & Gas Plant', path: '/one/airport/overview', status: 'mapped', l3: ['Process Unit Health', 'Critical Equipment Risk', 'Gas & Fire Risk', 'Pipeline / Tank / Valve', 'Permit-to-Work', 'Shutdown Exposure', 'Safety Barrier Status', 'Safety Evidence Pack'] },
      { id: 'coking-plant', label: 'Coking Plant', path: '/one/airport/overview', status: 'mapped', l3: ['Coke Oven Battery', 'Gas Safety', 'Dust Collection Risk', 'Desulfurization Status', 'Quenching System', 'Emission Risk', 'Production Continuity', 'Environmental Evidence Pack'] },
      { id: 'industrial-facility', label: 'Industrial Facility', path: '/one/airport/overview', status: 'mapped', l3: ['Production Line Health', 'Utility Island', 'Workshop Operations', 'Safety Zone', 'Critical Equipment', 'Industrial Energy', 'Industrial Evidence Pack'] },
      { id: 'multi-site-portfolio', label: 'Multi-site Portfolio', path: '/dashboard', status: 'mapped', l3: ['Cross-site Risk', 'Site Benchmark', 'Energy Benchmark', 'SLA Benchmark', 'Partner Benchmark', 'Executive Portfolio Pack'] },
    ],
  },
  {
    id: 'administration',
    label: 'Administration',
    path: '/system',
    icon: 'A',
    children: [
      { id: 'platform-setup', label: 'Platform Setup', path: '/system/settings', status: 'implemented', l3: ['Site Settings', 'System Settings', 'Notification Settings', 'Evidence Settings', 'Report Settings', 'Configuration Audit'], mappedExistingModule: 'SystemSettingsView' },
      { id: 'deployment-installation', label: 'Deployment & Installation', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Deployment Readiness', 'Installer Console', 'Server Precheck', 'Package Integrity', 'Deployment Evidence'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'engineering-operations', label: 'Engineering Operations', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Engineer Tools', 'Foundation Diagnostics', 'Offline Handoff', 'Diagnostics Evidence', 'Engineering Audit'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'health-inspection', label: 'Health & Inspection', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Healthcheck Preview', 'Inspection Queue', 'Diagnostic Queue', 'System Diagnostics', 'Health Evidence'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'backup-recovery', label: 'Backup & Recovery', path: '/system', status: 'mapped', l3: ['Backup Plan', 'Restore Plan', 'Recovery Evidence', 'Rollback Plan', 'DR Readiness', 'Recovery Reports'] },
      { id: 'resilience-operations', label: 'Resilience Operations', path: '/console/foundation-diagnostics/workspace', status: 'mapped', l3: ['Failover Readiness', 'Rollback Readiness', 'Continuity Plan', 'Recovery Drill', 'Resilience Evidence'], mappedExistingModule: 'FoundationDiagnosticsWorkspace' },
      { id: 'app-package-marketplace', label: 'App & Package Marketplace', path: '/system', status: 'mapped', l3: ['Package Risk Signal', 'Installed Package Context', 'Package Approval Actions', 'Entitlement Governance Audit', 'Package Evidence Pack', 'Marketplace Readiness Quality'] },
      { id: 'license-entitlement', label: 'License & Entitlement', path: '/system', status: 'mapped', l3: ['License Risk Signal', 'Edition Entitlement Context', 'Renewal Action Workflow', 'Usage Governance Audit', 'License Evidence Pack', 'Entitlement Readiness Quality'] },
      { id: 'workspace-configuration', label: 'Workspace Configuration', path: '/system/settings', status: 'implemented', l3: ['Workspace Access', 'Workspace Role Mapping', 'Workspace Permission Matrix', 'Workspace Audit', 'Workspace Defaults', 'Workspace Evidence'], mappedExistingModule: 'SystemSettingsView' },
      { id: 'customer-portal-configuration', label: 'Customer Portal Configuration', path: '/system/settings', status: 'mapped', l3: ['Portal Branding', 'Customer Visibility', 'Portal Reports', 'Customer Evidence', 'Portal Audit'], mappedExistingModule: 'SystemSettingsView' },
      { id: 'feature-flags', label: 'Feature Flags', path: '/system/settings', status: 'implemented', l3: ['Feature Flags', 'Module Flags', 'Role Visibility', 'Package Flags', 'Flag Audit'], mappedExistingModule: 'SystemSettingsView' },
    ],
  },
]

export const fallbackMenuItems: AppMenuItem[] = domains.map((domain) => ({
  id: domain.id,
  label: domain.label,
  path: domain.path,
  icon: domain.icon,
  source: 'static',
  children: domain.children.map((child) => ({
    id: child.id,
    label: child.label,
    path: child.path,
    source: 'static',
    l3Items: l3Items(child.l3, child.mappedExistingModule, child.status),
  })),
}))
