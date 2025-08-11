from typing import Dict, List, Any
import re
from datetime import datetime

class ComplianceChecker:
    def __init__(self):
        self.process_requirements = {
            'Company Incorporation': {
                'required_documents': [
                    'Articles of Association',
                    'Memorandum of Association',
                    'Board Resolution',
                    'UBO Declaration Form',
                    'Register of Members and Directors'
                ],
                'mandatory_clauses': [
                    'registered office',
                    'share capital',
                    'objects clause',
                    'liability clause',
                    'directors powers'
                ],
                'jurisdiction_requirements': ['ADGM', 'Abu Dhabi Global Market']
            },
            'Business Licensing': {
                'required_documents': [
                    'License Application Form',
                    'Business Plan',
                    'Articles of Association',
                    'Commercial License'
                ],
                'mandatory_clauses': [
                    'business activities',
                    'registered office',
                    'authorized activities'
                ],
                'jurisdiction_requirements': ['ADGM']
            },
            'Constitutional Amendments': {
                'required_documents': [
                    'Board Resolution',
                    'Shareholder Resolution',
                    'Amended Articles'
                ],
                'mandatory_clauses': [
                    'amendment clause',
                    'special resolution',
                    'effective date'
                ],
                'jurisdiction_requirements': ['ADGM']
            }
        }
        
        self.red_flag_patterns = [
            {
                'pattern': r'UAE Federal Court|Dubai Court|Abu Dhabi Court(?!.*ADGM)',
                'issue': 'Incorrect jurisdiction - should specify ADGM Courts',
                'severity': 'High',
                'category': 'jurisdiction'
            },
            {
                'pattern': r'UAE Commercial Code(?!.*ADGM)',
                'issue': 'Reference to UAE Commercial Code instead of ADGM regulations',
                'severity': 'High',
                'category': 'jurisdiction'
            },
            {
                'pattern': r'\[.*\]|\{.*\}|TBD|TO BE DETERMINED',
                'issue': 'Template placeholder not filled',
                'severity': 'Medium',
                'category': 'completeness'
            },
            {
                'pattern': r'shall be deemed|may be construed|could be interpreted',
                'issue': 'Ambiguous legal language',
                'severity': 'Medium',
                'category': 'clarity'
            },
            {
                'pattern': r'(?i)witness.*signature.*(?!.*ADGM)',
                'issue': 'Signature section may not comply with ADGM requirements',
                'severity': 'Low',
                'category': 'formatting'
            }
        ]
    
    def check_document(self, doc_data: Dict[str, Any], process_type: str) -> Dict[str, Any]:
        """Perform comprehensive compliance check"""
        issues = []
        
        # Check document type requirements
        doc_type_issues = self._check_document_type_requirements(doc_data, process_type)
        issues.extend(doc_type_issues)
        
        # Check for red flags
        red_flag_issues = self._detect_red_flags(doc_data)
        issues.extend(red_flag_issues)
        
        # Check mandatory clauses
        clause_issues = self._check_mandatory_clauses(doc_data, process_type)
        issues.extend(clause_issues)
        
        # Check jurisdiction compliance
        jurisdiction_issues = self._check_jurisdiction_compliance(doc_data, process_type)
        issues.extend(jurisdiction_issues)
        
        # Check formatting requirements
        format_issues = self._check_formatting_requirements(doc_data)
        issues.extend(format_issues)
        
        # Check signature requirements
        signature_issues = self._check_signature_requirements(doc_data)
        issues.extend(signature_issues)
        
        # Calculate compliance score
        total_checks = 6
        failed_checks = len(set(issue['category'] for issue in issues))
        compliance_score = max(0, (total_checks - failed_checks) / total_checks * 100)
        
        return {
            'is_compliant': len(issues) == 0,
            'compliance_score': compliance_score,
            'total_issues': len(issues),
            'issues': issues,
            'checked_categories': [
                'document_type',
                'red_flags',
                'mandatory_clauses',
                'jurisdiction',
                'formatting',
                'signatures'
            ]
        }
    
    def _check_document_type_requirements(self, doc_data: Dict[str, Any], process_type: str) -> List[Dict[str, Any]]:
        """Check if document type matches process requirements"""
        issues = []
        
        if process_type not in self.process_requirements:
            return issues
        
        requirements = self.process_requirements[process_type]
        doc_type = doc_data.get('document_type', 'Unknown')
        
        # Check if document type is in required documents list
        if doc_type not in requirements['required_documents'] and doc_type != 'Unknown Document Type':
            issues.append({
                'location': 'Document Type',
                'issue': f'Document type "{doc_type}" may not be required for {process_type}',
                'severity': 'Medium',
                'category': 'document_type',
                'suggestion': f'Verify if this document is needed for {process_type}'
            })
        
        return issues
    
    def _detect_red_flags(self, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect red flags in document content"""
        issues = []
        content = doc_data.get('content', '')
        
        for flag in self.red_flag_patterns:
            matches = re.finditer(flag['pattern'], content, re.IGNORECASE)
            
            for match in matches:
                # Find the paragraph containing the match
                location = self._find_paragraph_location(content, match.start())
                
                issues.append({
                    'location': location,
                    'issue': flag['issue'],
                    'severity': flag['severity'],
                    'category': flag['category'],
                    'suggestion': self._get_red_flag_suggestion(flag['category'], flag['issue']),
                    'matched_text': match.group()
                })
        
        return issues
    
    def _check_mandatory_clauses(self, doc_data: Dict[str, Any], process_type: str) -> List[Dict[str, Any]]:
        """Check for mandatory clauses based on process type"""
        issues = []
        
        if process_type not in self.process_requirements:
            return issues
        
        requirements = self.process_requirements[process_type]
        content = doc_data.get('content', '').lower()
        
        for clause in requirements['mandatory_clauses']:
            if clause.lower() not in content:
                issues.append({
                    'location': 'Document Content',
                    'issue': f'Missing mandatory clause: {clause}',
                    'severity': 'High',
                    'category': 'mandatory_clauses',
                    'suggestion': f'Add {clause} clause as required for {process_type}'
                })
        
        return issues
    
    def _check_jurisdiction_compliance(self, doc_data: Dict[str, Any], process_type: str) -> List[Dict[str, Any]]:
        """Check jurisdiction compliance"""
        issues = []
        
        if process_type not in self.process_requirements:
            return issues
        
        requirements = self.process_requirements[process_type]
        content = doc_data.get('content', '')
        
        # Check if ADGM jurisdiction is properly referenced
        adgm_mentioned = any(req in content for req in requirements['jurisdiction_requirements'])
        
        if not adgm_mentioned:
            issues.append({
                'location': 'Jurisdiction Clause',
                'issue': 'ADGM jurisdiction not properly specified',
                'severity': 'High',
                'category': 'jurisdiction',
                'suggestion': 'Specify ADGM as the governing jurisdiction and court system'
            })
        
        # Check for incorrect UAE federal references
        federal_patterns = [
            r'UAE Federal Court',
            r'Dubai International Financial Centre(?!.*ADGM)',
            r'UAE Commercial Code(?!.*ADGM)'
        ]
        
        for pattern in federal_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append({
                    'location': 'Jurisdiction Reference',
                    'issue': 'Incorrect reference to UAE federal jurisdiction',
                    'severity': 'High',
                    'category': 'jurisdiction',
                    'suggestion': 'Replace with ADGM jurisdiction and regulations'
                })
        
        return issues
    
    def _check_formatting_requirements(self, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check formatting requirements"""
        issues = []
        
        structure = doc_data.get('structure', {})
        
        # Check for signature section
        if not structure.get('has_signature_section', False):
            issues.append({
                'location': 'Document End',
                'issue': 'Missing signature section',
                'severity': 'Medium',
                'category': 'formatting',
                'suggestion': 'Add proper signature section with witness requirements'
            })
        
        # Check for date section
        if not structure.get('has_date_section', False):
            issues.append({
                'location': 'Document Header/Footer',
                'issue': 'Missing date section',
                'severity': 'Low',
                'category': 'formatting',
                'suggestion': 'Add document execution date'
            })
        
        # Check heading structure
        if len(structure.get('headings', [])) == 0:
            issues.append({
                'location': 'Document Structure',
                'issue': 'No proper heading structure found',
                'severity': 'Low',
                'category': 'formatting',
                'suggestion': 'Use proper heading styles for better document structure'
            })
        
        return issues
    
    def _check_signature_requirements(self, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check signature requirements"""
        issues = []
        content = doc_data.get('content', '').lower()
        
        # Required signature elements
        signature_elements = [
            ('signature', 'Signature line'),
            ('witness', 'Witness section'),
            ('date', 'Date field')
        ]
        
        missing_elements = []
        for element, description in signature_elements:
            if element not in content:
                missing_elements.append(description)
        
        if missing_elements:
            issues.append({
                'location': 'Signature Section',
                'issue': f'Missing signature elements: {", ".join(missing_elements)}',
                'severity': 'Medium',
                'category': 'signatures',
                'suggestion': 'Add complete signature section with all required elements'
            })
        
        return issues
    
    def _find_paragraph_location(self, content: str, position: int) -> str:
        """Find paragraph containing the position"""
        lines = content.split('\n')
        current_pos = 0
        
        for i, line in enumerate(lines):
            if current_pos <= position <= current_pos + len(line):
                return f'Paragraph {i + 1}: {line[:50]}...' if len(line) > 50 else f'Paragraph {i + 1}: {line}'
            current_pos += len(line) + 1  # +1 for newline
        
        return 'Unknown location'
    
    def _get_red_flag_suggestion(self, category: str, issue: str) -> str:
        """Get suggestion for red flag issue"""
        suggestions = {
            'jurisdiction': 'Update to specify ADGM as governing jurisdiction',
            'completeness': 'Fill in all template placeholders with actual values',
            'clarity': 'Use clear, definitive legal language',
            'formatting': 'Follow ADGM document formatting requirements'
        }
        
        return suggestions.get(category, 'Review and correct as per ADGM requirements')
    
    def generate_compliance_report(self, results: Dict[str, Any]) -> str:
        """Generate a detailed compliance report"""
        report = f"""
        ADGM COMPLIANCE ANALYSIS REPORT
        Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        OVERALL COMPLIANCE STATUS: {'COMPLIANT' if results['is_compliant'] else 'NON-COMPLIANT'}
        Compliance Score: {results['compliance_score']:.1f}%
        Total Issues Found: {results['total_issues']}
        
        ISSUES BREAKDOWN:
        """
        
        if results['issues']:
            severity_counts = {}
            for issue in results['issues']:
                severity = issue['severity']
                severity_counts[severity] = severity_counts.get(severity, 0) + 1
            
            for severity, count in severity_counts.items():
                report += f"- {severity} Priority: {count} issues\n"
            
            report += "\nDETAILED ISSUES:\n"
            for i, issue in enumerate(results['issues'], 1):
                report += f"""
                {i}. {issue['issue']}
                   Location: {issue['location']}
                   Severity: {issue['severity']}
                   Category: {issue['category']}
                   Suggestion: {issue['suggestion']}
                """
        else:
            report += "No compliance issues found."
        
        return report
