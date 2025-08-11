import google.generativeai as genai
import os
from typing import Optional, Dict
import time
import json

class GeminiClient:
    def __init__(self):
        # Configure Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        
        # Initialize model
        self.model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-exp',
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for consistent legal analysis
                top_p=0.95,
                top_k=40,
                max_output_tokens=4096,
            ),
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH", 
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
    
    def generate_response(self, prompt: str, max_retries: int = 3) -> str:
        """Generate response using Gemini"""
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(prompt)
                
                if response.text:
                    return response.text
                else:
                    raise Exception("Empty response from Gemini")
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    raise Exception(f"Failed to generate response after {max_retries} attempts: {str(e)}")
    
    def analyze_legal_document(self, document_content: str, document_type: str, context: str = "") -> Dict:
        """Analyze legal document with structured output"""
        prompt = f"""
        You are an expert ADGM legal analyst. Analyze the following legal document for compliance with ADGM regulations.

        Document Type: {document_type}
        
        {f"Additional Context: {context}" if context else ""}
        
        Document Content:
        {document_content[:3000]}...
        
        Please provide a structured analysis in the following JSON format:
        {{
            "compliance_assessment": {{
                "overall_compliant": true/false,
                "compliance_score": 0-100,
                "summary": "Brief overall assessment"
            }},
            "issues_identified": [
                {{
                    "category": "jurisdiction/formatting/content/other",
                    "severity": "High/Medium/Low",
                    "description": "Issue description",
                    "location": "Where in document",
                    "adgm_reference": "Relevant ADGM regulation if applicable",
                    "recommendation": "How to fix"
                }}
            ],
            "positive_aspects": [
                "List of compliant elements found"
            ],
            "recommendations": [
                "Specific actionable recommendations"
            ],
            "next_steps": "What the user should do next"
        }}
        
        Focus on ADGM-specific requirements and provide practical, actionable advice.
        """
        
        try:
            response = self.generate_response(prompt)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response if it's wrapped in text
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = response[json_start:json_end]
                    return json.loads(json_str)
                else:
                    # If no JSON found, return structured text response
                    return {
                        "compliance_assessment": {
                            "overall_compliant": False,
                            "compliance_score": 50,
                            "summary": "Analysis completed - see full response"
                        },
                        "full_response": response
                    }
            except json.JSONDecodeError:
                return {
                    "compliance_assessment": {
                        "overall_compliant": False,
                        "compliance_score": 50,
                        "summary": "Analysis completed - see full response"
                    },
                    "full_response": response
                }
                
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "compliance_assessment": {
                    "overall_compliant": False,
                    "compliance_score": 0,
                    "summary": "Analysis could not be completed"
                }
            }
    
    def generate_document_suggestions(self, document_type: str, issues: list) -> str:
        """Generate improvement suggestions for document"""
        prompt = f"""
        As an ADGM legal expert, provide specific improvement suggestions for a {document_type} that has the following issues:
        
        Issues Found:
        {json.dumps(issues, indent=2)}
        
        Please provide:
        1. Priority order for fixing issues
        2. Specific wording suggestions where applicable
        3. ADGM regulatory references
        4. Template examples if helpful
        5. Common mistakes to avoid
        
        Make your suggestions practical and implementable.
        """
        
        return self.generate_response(prompt)
    
    def explain_adgm_requirement(self, requirement: str, context: str = "") -> str:
        """Explain specific ADGM requirements"""
        prompt = f"""
        Explain the following ADGM requirement in clear, practical terms:
        
        Requirement: {requirement}
        {f"Context: {context}" if context else ""}
        
        Please explain:
        1. What this requirement means
        2. Why it's important
        3. How to comply with it
        4. Common mistakes
        5. Practical examples
        
        Keep the explanation clear and actionable for legal practitioners.
        """
        
        return self.generate_response(prompt)
    
    def compare_with_template(self, document_content: str, template_content: str, document_type: str) -> str:
        """Compare document with ADGM template"""
        prompt = f"""
        Compare the following document with the ADGM template and identify differences:
        
        Document Type: {document_type}
        
        ADGM Template:
        {template_content[:1500]}...
        
        User Document:
        {document_content[:1500]}...
        
        Please identify:
        1. Missing sections from template
        2. Additional sections not in template
        3. Content differences
        4. Formatting differences
        5. Recommendations for alignment
        
        Focus on compliance-critical differences.
        """
        
        return self.generate_response(prompt)
