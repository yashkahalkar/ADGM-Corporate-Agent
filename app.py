import streamlit as st
import os
import tempfile
import json
from datetime import datetime

# Streamlit secrets integration
def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable with Streamlit secrets fallback"""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        value = os.getenv(key, default)
        if not value and default is None:
            st.error(f"❌ Missing: {key}")
            st.write("Set this in Streamlit Cloud → Settings → Secrets")
            st.stop()
        return value or default

# Import components
from components.document_parser import DocumentParser
from components.rag_engine import RAGEngine
from components.compliance_checker import ComplianceChecker
from components.comment_injector import CommentInjector
from models.gemini_client import GeminiClient

# Load environment variables
def get_env_var(key: str, default: str = None) -> str:
    """Get environment variable with Streamlit secrets fallback"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        return st.secrets[key]
    except (KeyError, FileNotFoundError, AttributeError):
        # Fallback to environment variables (for local development)
        value = os.getenv(key, default)
        if not value and default is None:
            st.error(f"❌ Missing required environment variable: {key}")
            st.write("Please set this in Streamlit Secrets or your .env file")
            st.stop()
        return value or default

# Page configuration
st.set_page_config(
    page_title="ADGM Corporate Agent",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2c5aa0;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .status-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
    }
    .error-box {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

class ADGMCorporateAgent:
    def __init__(self):
        self.document_parser = DocumentParser()
        self.rag_engine = RAGEngine()
        self.compliance_checker = ComplianceChecker()
        self.comment_injector = CommentInjector()
        self.gemini_client = GeminiClient()
        
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'processed_documents' not in st.session_state:
            st.session_state.processed_documents = []

    def render_header(self):
        """Render application header"""
        st.markdown('<h1 class="main-header">⚖️ ADGM Corporate Agent</h1>', unsafe_allow_html=True)
        st.markdown("**AI-Powered Legal Document Analysis & Compliance Assistant**")
        st.markdown("---")

    def render_sidebar(self):
        """Render sidebar with options"""
        st.sidebar.header("🎛️ Control Panel")
        
        # Process type selection
        process_types = [
            "Company Incorporation",
            "Business Licensing", 
            "Constitutional Amendments",
            "Corporate Restructuring",
            "Regulatory Compliance",
            "General Document Review"
        ]
        
        selected_process = st.sidebar.selectbox(
            "Select Legal Process:",
            process_types,
            help="Choose the type of legal process for targeted analysis"
        )
        
        # Analysis options
        st.sidebar.header("📋 Analysis Options")
        check_compliance = st.sidebar.checkbox("Compliance Checking", value=True)
        detect_red_flags = st.sidebar.checkbox("Red Flag Detection", value=True)
        suggest_improvements = st.sidebar.checkbox("Improvement Suggestions", value=True)
        add_comments = st.sidebar.checkbox("Add Document Comments", value=True)
        
        return {
            'process_type': selected_process,
            'check_compliance': check_compliance,
            'detect_red_flags': detect_red_flags,
            'suggest_improvements': suggest_improvements,
            'add_comments': add_comments
        }

    def render_file_upload(self):
        """Render file upload section"""
        st.markdown('<h2 class="section-header">📄 Document Upload</h2>', unsafe_allow_html=True)
        
        uploaded_files = st.file_uploader(
            "Upload Legal Documents (.docx files)",
            type=['docx'],
            accept_multiple_files=True,
            help="Upload ADGM legal documents for analysis"
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded successfully!")
            
            # Display uploaded files
            st.markdown("**Uploaded Files:**")
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name} ({file.size / 1024:.1f} KB)")
                
        return uploaded_files

    def process_documents(self, uploaded_files, options):
        """Process uploaded documents"""
        if not uploaded_files:
            return None
            
        st.markdown('<h2 class="section-header">🔄 Processing Documents</h2>', unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        results = {
            'process_type': options['process_type'],
            'documents': [],
            'overall_compliance': True,
            'total_issues': 0,
            'summary': {}
        }
        
        for i, uploaded_file in enumerate(uploaded_files):
            # Update progress
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            status_text.text(f"Processing {uploaded_file.name}...")
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name
            
            try:
                # Parse document
                doc_data = self.document_parser.parse_document(tmp_file_path)
                doc_data['filename'] = uploaded_file.name
                
                # Analyze with RAG
                if options['check_compliance'] or options['detect_red_flags']:
                    analysis = self.rag_engine.analyze_document(
                        doc_data['content'], 
                        options['process_type']
                    )
                    doc_data['rag_analysis'] = analysis
                
                # Check compliance
                if options['check_compliance']:
                    compliance_result = self.compliance_checker.check_document(
                        doc_data, options['process_type']
                    )
                    doc_data['compliance'] = compliance_result
                    
                    if not compliance_result['is_compliant']:
                        results['overall_compliance'] = False
                        results['total_issues'] += len(compliance_result['issues'])
                
                # Add comments if requested
                if options['add_comments'] and doc_data.get('compliance'):
                    commented_doc_path = self.comment_injector.add_comments(
                        tmp_file_path, doc_data['compliance']['issues']
                    )
                    doc_data['commented_document_path'] = commented_doc_path
                
                results['documents'].append(doc_data)
                
            except Exception as e:
                st.error(f"Error processing {uploaded_file.name}: {str(e)}")
            finally:
                # Clean up temporary file
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
        
        progress_bar.progress(1.0)
        status_text.text("Processing complete!")
        
        return results

    def render_results(self, results):
        """Render analysis results - SIMPLIFIED VERSION"""
        if not results:
            return
            
        st.markdown('<h2 class="section-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
        
        # Overall summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Documents Processed", len(results['documents']))
        with col2:
            st.metric("Total Issues Found", results['total_issues'])
        with col3:
            compliance_status = "✅ Compliant" if results['overall_compliance'] else "❌ Non-Compliant"
            st.metric("Overall Status", compliance_status)
        with col4:
            completion_rate = len([d for d in results['documents'] if d.get('compliance', {}).get('is_compliant', False)]) / len(results['documents']) * 100
            st.metric("Compliance Rate", f"{completion_rate:.1f}%")
        
        # Document-specific results - SINGLE LEVEL EXPANDERS ONLY
        st.markdown("---")
        st.markdown("### 📄 Document Analysis")
        
        for i, doc in enumerate(results['documents']):
            # Single expander per document - NO NESTING
            with st.expander(f"📄 {doc['filename']} - {doc.get('document_type', 'Unknown')}", expanded=True):
                
                # Basic info
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Document Type:** {doc.get('document_type', 'Unknown')}")
                    st.write(f"**Word Count:** {doc.get('word_count', 0):,}")
                
                # Compliance status
                if 'compliance' in doc:
                    compliance = doc['compliance']
                    with col2:
                        if compliance['is_compliant']:
                            st.success("✅ ADGM Compliant")
                        else:
                            st.error("❌ Non-Compliant")
                            st.write(f"Issues: {len(compliance['issues'])}")
                    
                    # Issues section
                    if compliance['issues']:
                        st.markdown("**🚨 Issues Found:**")
                        for issue in compliance['issues']:
                            severity_icon = {'High': '🔴', 'Medium': '🟡', 'Low': '🟢'}
                            
                            st.markdown(f"""
                            **{severity_icon.get(issue['severity'], '🔵')} {issue['severity']} Priority**
                            - **Issue:** {issue['issue']}
                            - **Location:** {issue['location']}
                            - **Suggestion:** {issue['suggestion']}
                            """)
                            st.markdown("---")
                
                # AI Analysis section (NO NESTED EXPANDER)
                if 'rag_analysis' in doc:
                    st.markdown("**🤖 AI Analysis:**")
                    st.info(doc['rag_analysis'])
        
        # Download section
        self.render_download_section(results)


    def render_document_analysis(self, doc_data):
        """Render individual document analysis"""
        # Document type and basic info
        st.write(f"**Document Type:** {doc_data.get('document_type', 'Unknown')}")
        st.write(f"**Word Count:** {doc_data.get('word_count', 0):,}")
        
        # Compliance status
        if 'compliance' in doc_data:
            compliance = doc_data['compliance']
            
            if compliance['is_compliant']:
                st.markdown('<div class="status-box success-box">✅ <strong>Document is ADGM compliant</strong></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="status-box error-box">❌ <strong>Document has compliance issues</strong></div>', unsafe_allow_html=True)
            
            # Issues found
            if compliance['issues']:
                st.markdown("**Issues Found:**")
                for issue in compliance['issues']:
                    severity_color = {
                        'High': '🔴',
                        'Medium': '🟡', 
                        'Low': '🟢'
                    }
                    
                    st.markdown(f"""
                    {severity_color.get(issue['severity'], '🔵')} **{issue['severity']}** - {issue['issue']}
                    - **Location:** {issue['location']}
                    - **Suggestion:** {issue['suggestion']}
                    """)
        
        # RAG Analysis
        if 'rag_analysis' in doc_data:
            with st.expander("🤖 AI Analysis", expanded=False):
                st.write(doc_data['rag_analysis'])

    def render_download_section(self, results):
        """Render download section for processed documents"""
        st.markdown('<h2 class="section-header">⬇️ Download Results</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Download JSON report
            json_report = json.dumps(results, indent=2, default=str)
            st.download_button(
                label="📋 Download Analysis Report (JSON)",
                data=json_report,
                file_name=f"adgm_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        with col2:
            # Download commented documents
            commented_docs = [doc for doc in results['documents'] if 'commented_document_path' in doc]
            if commented_docs:
                st.info(f"📝 {len(commented_docs)} document(s) available with comments")
                
                for doc in commented_docs:
                    if os.path.exists(doc['commented_document_path']):
                        with open(doc['commented_document_path'], 'rb') as file:
                            st.download_button(
                                label=f"📄 Download {doc['filename']} (with comments)",
                                data=file.read(),
                                file_name=f"commented_{doc['filename']}",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )

    def run(self):
        """Main application runner"""
        self.initialize_session_state()
        self.render_header()
        
        # Sidebar options
        options = self.render_sidebar()
        
        # File upload
        uploaded_files = self.render_file_upload()
        
        # Process button
        if uploaded_files and st.button("🚀 Start Analysis", type="primary"):
            with st.spinner("Processing documents..."):
                results = self.process_documents(uploaded_files, options)
                st.session_state.analysis_results = results
        
        # Display results
        if 'analysis_results' in st.session_state and st.session_state.analysis_results:
            self.render_results(st.session_state.analysis_results)

def main():
    """Main function"""
    try:
        agent = ADGMCorporateAgent()
        agent.run()
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.error("Please check your environment variables and API keys.")

if __name__ == "__main__":
    main()
