import json
import os
from typing import Dict, Any, List
from pathlib import Path
from google import genai


class HeuristicAgent:
    """
    Heuristic Evaluation Agent: Evaluates UI against Nielsen's heuristics
    and mobile-specific UX guidelines
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        # Configure Gemini
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"

        
        # Load Nielsen's heuristics
        self.heuristics = self._load_heuristics()
        
        print("✅ Heuristic Agent initialized")
    
    def _load_heuristics(self) -> Dict:
        """Load Nielsen's heuristics from JSON file"""
        heuristics_path = Path("config/nielsen_heuristics.json")
        
        if not heuristics_path.exists():
            raise FileNotFoundError(
                f"Heuristics file not found: {heuristics_path}\n"
                "Please create config/nielsen_heuristics.json"
            )
        
        with open(heuristics_path, 'r') as f:
            return json.load(f)
    
    def evaluate(self, vision_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate UI against heuristics
        
        Args:
            vision_analysis: Output from Vision Agent
            
        Returns:
            Dictionary with violations and scores
        """
        try:
            print(f"\n🔍 Evaluating UI against Nielsen's heuristics...")
            
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(vision_analysis)
            
            # Get AI evaluation
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            # Parse response
            result = self._parse_evaluation_response(response.text)
            
            # Calculate overall score
            result['overall_score'] = self._calculate_score(result.get('violations', []))
            
            print(f"✅ Evaluation complete! Score: {result['overall_score']}/10")
            
            return result
            
        except Exception as e:
            print(f"❌ Error during evaluation: {str(e)}")
            return {"error": str(e)}
    
    def _create_evaluation_prompt(self, vision_analysis: Dict) -> str:
        """Create detailed prompt for heuristic evaluation"""
        
        # Extract key info from vision analysis
        screen_type = vision_analysis.get('screen_type', 'unknown')
        components = vision_analysis.get('components', [])
        color_scheme = vision_analysis.get('color_scheme', {})
        accessibility_obs = vision_analysis.get('accessibility_observations', [])
        spacing = vision_analysis.get('spacing_and_density', {})
        
        prompt = f"""
You are a UX evaluation expert. Evaluate this mobile UI design against Nielsen's 10 Usability Heuristics and mobile UX best practices.

## UI ANALYSIS DATA:

**Screen Type:** {screen_type}

**Components Detected:** {len(components)}
{json.dumps(components, indent=2)}

**Color Scheme:**
{json.dumps(color_scheme, indent=2)}

**Spacing & Density:**
{json.dumps(spacing, indent=2)}

**Accessibility Observations:**
{json.dumps(accessibility_obs, indent=2)}

## NIELSEN'S 10 HEURISTICS TO EVALUATE:

{self._format_heuristics_for_prompt()}

## MOBILE-SPECIFIC GUIDELINES:

{self._format_mobile_guidelines()}

## YOUR TASK:

Evaluate this UI against EACH heuristic and identify violations. For each violation found:

1. Specify which heuristic is violated
2. Assign severity: critical/high/medium/low
3. Describe the specific issue
4. List affected components
5. Suggest improvements

**IMPORTANT:** Return ONLY valid JSON with this structure:

{{
  "violations": [
    {{
      "heuristic_id": 1,
      "heuristic_name": "Visibility of system status",
      "severity": "high",
      "issue": "Detailed description of the problem",
      "affected_components": ["component type or name"],
      "evidence": "What you observed in the UI data",
      "improvement_suggestion": "Specific actionable advice"
    }}
  ],
  "strengths": [
    {{
      "heuristic_id": 4,
      "heuristic_name": "Consistency and standards",
      "observation": "What the UI does well"
    }}
  ],
  "mobile_specific_issues": [
    {{
      "category": "Touch Targets / Typography / Color / etc",
      "severity": "high/medium/low",
      "issue": "Description",
      "recommendation": "How to fix"
    }}
  ]
}}

Be thorough but fair. Only report actual violations you can identify from the data.
Return ONLY the JSON, no additional text.
"""
        return prompt
    
    def _format_heuristics_for_prompt(self) -> str:
        """Format heuristics as readable text for prompt"""
        output = []
        for h in self.heuristics['heuristics']:
            output.append(f"{h['id']}. {h['name']}")
            output.append(f"   Description: {h['description']}")
            output.append(f"   Mobile considerations: {', '.join(h['mobile_considerations'][:3])}")
            output.append("")
        return "\n".join(output)
    
    def _format_mobile_guidelines(self) -> str:
        """Format mobile guidelines for prompt"""
        output = []
        for guideline in self.heuristics['mobile_specific_guidelines']:
            output.append(f"**{guideline['category']}:**")
            for g in guideline['guidelines']:
                output.append(f"  - {g}")
            output.append("")
        return "\n".join(output)
    
    def _parse_evaluation_response(self, response_text: str) -> Dict:
        """Parse AI response into structured JSON"""
        try:
            # Clean response
            cleaned = response_text.strip()
            
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse evaluation JSON")
            return {
                "raw_response": response_text,
                "parse_error": str(e),
                "violations": []
            }
    
    def _calculate_score(self, violations: List[Dict]) -> float:
        """
        Calculate overall UX score (0-10 scale)
        10 = perfect, 0 = critical issues
        """
        if not violations:
            return 10.0
        
        # Severity weights
        severity_impact = {
            'critical': 10,
            'high': 3,
            'medium': 1,
            'low': 0.3
        }
        
        # Calculate total deduction
        total_deduction = 0
        for violation in violations:
            severity = violation.get('severity', 'low')
            total_deduction += severity_impact.get(severity, 0)
        
        # Cap deduction at 10 (minimum score is 0)
        total_deduction = min(total_deduction, 10)
        
        score = 10.0 - total_deduction
        return max(0, round(score, 1))
    
    def generate_report(self, evaluation_result: Dict) -> str:
        """Generate human-readable report from evaluation"""
        
        violations = evaluation_result.get('violations', [])
        strengths = evaluation_result.get('strengths', [])
        mobile_issues = evaluation_result.get('mobile_specific_issues', [])
        score = evaluation_result.get('overall_score', 0)
        
        report = []
        report.append("=" * 70)
        report.append("UX HEURISTIC EVALUATION REPORT")
        report.append("=" * 70)
        report.append(f"\n**Overall UX Score: {score}/10**\n")
        
        # Violations section
        if violations:
            report.append(f"\n{'='*70}")
            report.append(f"VIOLATIONS FOUND ({len(violations)})")
            report.append(f"{'='*70}\n")
            
            # Group by severity
            for severity in ['critical', 'high', 'medium', 'low']:
                severity_violations = [v for v in violations if v.get('severity') == severity]
                
                if severity_violations:
                    report.append(f"\n{severity.upper()} Severity ({len(severity_violations)}):")
                    report.append("-" * 70)
                    
                    for i, v in enumerate(severity_violations, 1):
                        report.append(f"\n{i}. {v.get('heuristic_name', 'Unknown')}")
                        report.append(f"   Issue: {v.get('issue', 'N/A')}")
                        report.append(f"   Affected: {', '.join(v.get('affected_components', []))}")
                        report.append(f"   Suggestion: {v.get('improvement_suggestion', 'N/A')}")
        
        # Strengths section
        if strengths:
            report.append(f"\n\n{'='*70}")
            report.append(f"STRENGTHS ({len(strengths)})")
            report.append(f"{'='*70}\n")
            
            for i, s in enumerate(strengths, 1):
                report.append(f"{i}. {s.get('heuristic_name', 'Unknown')}")
                report.append(f"   {s.get('observation', 'N/A')}\n")
        
        # Mobile-specific issues
        if mobile_issues:
            report.append(f"\n{'='*70}")
            report.append(f"MOBILE-SPECIFIC ISSUES ({len(mobile_issues)})")
            report.append(f"{'='*70}\n")
            
            for i, issue in enumerate(mobile_issues, 1):
                report.append(f"{i}. {issue.get('category', 'Unknown')} [{issue.get('severity', 'unknown')}]")
                report.append(f"   Issue: {issue.get('issue', 'N/A')}")
                report.append(f"   Fix: {issue.get('recommendation', 'N/A')}\n")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)