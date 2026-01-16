import json
import os
from typing import Dict, Any, List
from pathlib import Path
from google import genai


class FeedbackAgent:
    """
    Feedback Generator Agent: Converts heuristic violations into 
    developer-friendly, actionable feedback with code examples
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
        # Configure Gemini
        self.client = genai.Client(api_key=self.api_key)
        self.model = "gemini-3-flash-preview"
        
        print("✅ Feedback Agent initialized")
    
    def generate_feedback(
        self, 
        vision_analysis: Dict[str, Any],
        heuristic_evaluation: Dict[str, Any],
        platform: str = "android"  # or "ios", "react-native"
    ) -> Dict[str, Any]:
        """
        Generate developer-friendly feedback from evaluation results
        
        Args:
            vision_analysis: Output from Vision Agent
            heuristic_evaluation: Output from Heuristic Agent
            platform: Target platform for code examples
            
        Returns:
            Dictionary with actionable feedback and wireframe instructions
        """
        try:
            print(f"\n💡 Generating developer feedback for {platform}...")
            
            # Create feedback generation prompt
            prompt = self._create_feedback_prompt(
                vision_analysis,
                heuristic_evaluation,
                platform
            )
            
            # Get AI-generated feedback
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            # Parse response
            result = self._parse_feedback_response(response.text)
            
            # Add metadata
            result['platform'] = platform
            result['total_feedback_items'] = len(result.get('feedback_items', []))
            
            print(f"✅ Generated {result['total_feedback_items']} feedback items")
            
            return result
            
        except Exception as e:
            print(f"❌ Error generating feedback: {str(e)}")
            return {"error": str(e)}
    
    def _create_feedback_prompt(
        self,
        vision_analysis: Dict,
        heuristic_evaluation: Dict,
        platform: str
    ) -> str:
        """Create detailed prompt for feedback generation"""
        
        violations = heuristic_evaluation.get('violations', [])
        mobile_issues = heuristic_evaluation.get('mobile_specific_issues', [])
        screen_type = vision_analysis.get('screen_type', 'unknown')
        components = vision_analysis.get('components', [])
        
        prompt = f"""
You are a senior UX developer and mentor. Your job is to help a developer improve their mobile UI by providing clear, actionable, and encouraging feedback.

## CONTEXT

**Platform:** {platform}
**Screen Type:** {screen_type}
**Components:** {len(components)} UI elements detected

## VIOLATIONS IDENTIFIED

{json.dumps(violations, indent=2)}

## MOBILE-SPECIFIC ISSUES

{json.dumps(mobile_issues, indent=2)}

## YOUR TASK

Transform these technical violations into helpful, actionable feedback that a developer can immediately implement. For EACH violation or issue:

1. **Title**: Short, action-oriented (e.g., "Add Loading Indicators", "Improve Color Contrast")
2. **Why it matters**: Explain the user impact in 1-2 sentences
3. **What to do**: Step-by-step actions (3-5 bullet points)
4. **Priority**: critical/high/medium/low based on severity and user impact
5. **Wireframe change**: Describe visual changes needed (for wireframe generator)

## OUTPUT FORMAT

Return ONLY valid JSON with this structure:

{{
  "feedback_items": [
    {{
      "id": 1,
      "title": "Add Loading State Indicators",
      "category": "Visibility of system status",
      "priority": "high",
      "why_it_matters": "Users need visual feedback when actions are processing. Without loading indicators, users may think the app is frozen or broken, leading to frustration and multiple taps.",
      "what_to_do": [
        "Add a progress indicator when quiz categories are tapped",
        "Show a spinner overlay during data fetching",
        "Disable buttons during loading to prevent double-taps",
        "Add success/error feedback after actions complete"
      ],
      "code_example": {{
        "language": "kotlin",
        "description": "Add loading state with ProgressBar",
        "code": "// In your Activity or Fragment\\nval progressBar = findViewById<ProgressBar>(R.id.progressBar)\\nval quizButton = findViewById<Button>(R.id.quizButton)\\n\\nquizButton.setOnClickListener {{\\n    // Show loading\\n    progressBar.visibility = View.VISIBLE\\n    quizButton.isEnabled = false\\n    \\n    // Fetch quiz data\\n    viewModel.loadQuiz().observe(this) {{ result ->\\n        progressBar.visibility = View.GONE\\n        quizButton.isEnabled = true\\n        // Handle result\\n    }}\\n}}"
      }},
      "wireframe_changes": "Add a circular progress spinner in the center of each quiz category card when tapped. Show semi-transparent overlay during loading.",
      "affected_components": ["quiz category cards"],
      "estimated_effort": "30 minutes"
    }}
  ],
  "wireframe_instructions": {{
    "overall_changes": "Summary of all visual changes needed",
    "priority_fixes": [
      "Most important visual change #1",
      "Most important visual change #2",
      "Most important visual change #3"
    ],
    "layout_modifications": [
      "Specific layout adjustments needed"
    ],
    "color_adjustments": [
      "Color/contrast changes needed"
    ],
    "typography_changes": [
      "Font size/weight adjustments needed"
    ]
  }},
  "quick_wins": [
    {{
      "change": "Increase 'Beginner' text size to 16sp",
      "impact": "Improves readability significantly",
      "effort": "5 minutes"
    }}
  ],
  "summary": {{
    "total_issues": 6,
    "critical": 0,
    "high": 2,
    "medium": 3,
    "low": 1,
    "estimated_total_time": "3-4 hours"
  }}
}}

Be specific, practical, and encouraging. Focus on actionable improvements that will have the biggest impact on user experience.
"""
        return prompt
    
    def _parse_feedback_response(self, response_text: str) -> Dict:
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
            print(f"⚠️  Failed to parse feedback JSON")
            return {
                "raw_response": response_text,
                "parse_error": str(e),
                "feedback_items": []
            }
    
    def generate_developer_report(self, feedback_result: Dict) -> str:
        """Generate markdown report for developers"""
        
        feedback_items = feedback_result.get('feedback_items', [])
        quick_wins = feedback_result.get('quick_wins', [])
        summary = feedback_result.get('summary', {})
        wireframe_instructions = feedback_result.get('wireframe_instructions', {})
        
        report = []
        report.append("# 🎯 UX Feedback Report for Developers\n")
        
        # Summary section
        report.append("## 📊 Summary\n")
        report.append(f"- **Total Issues Found:** {summary.get('total_issues', 0)}")
        report.append(f"- **Critical:** {summary.get('critical', 0)}")
        report.append(f"- **High Priority:** {summary.get('high', 0)}")
        report.append(f"- **Medium Priority:** {summary.get('medium', 0)}")
        report.append(f"- **Low Priority:** {summary.get('low', 0)}")
        report.append(f"- **Estimated Time to Fix:** {summary.get('estimated_total_time', 'Unknown')}\n")
        
        # Quick wins
        if quick_wins:
            report.append("## ⚡ Quick Wins (Do These First!)\n")
            report.append("These changes take minimal time but provide maximum impact:\n")
            for i, win in enumerate(quick_wins, 1):
                report.append(f"{i}. **{win.get('change', 'N/A')}**")
                report.append(f"   - Impact: {win.get('impact', 'N/A')}")
                report.append(f"   - Effort: {win.get('effort', 'N/A')}\n")
        
        # Priority-sorted feedback
        report.append("## 🔧 Detailed Feedback\n")
        
        # Group by priority
        for priority in ['critical', 'high', 'medium', 'low']:
            priority_items = [
                item for item in feedback_items 
                if item.get('priority') == priority
            ]
            
            if priority_items:
                report.append(f"### {priority.upper()} Priority ({len(priority_items)} items)\n")
                
                for item in priority_items:
                    report.append(f"#### {item.get('id', '?')}. {item.get('title', 'Unknown')}\n")
                    report.append(f"**Category:** {item.get('category', 'N/A')}  ")
                    report.append(f"**Estimated Effort:** {item.get('estimated_effort', 'Unknown')}\n")
                    
                    report.append(f"**Why it matters:**  ")
                    report.append(f"{item.get('why_it_matters', 'N/A')}\n")
                    
                    report.append("**What to do:**")
                    for step in item.get('what_to_do', []):
                        report.append(f"- {step}")
                    report.append("")
                    
                    # Code example
                    code_example = item.get('code_example', {})
                    if code_example:
                        report.append(f"**Code Example ({code_example.get('language', 'code')}):**")
                        report.append(f"```{code_example.get('language', 'kotlin')}")
                        report.append(code_example.get('code', ''))
                        report.append("```\n")
                    
                    report.append(f"**Visual changes needed:**  ")
                    report.append(f"{item.get('wireframe_changes', 'N/A')}\n")
                    
                    report.append("---\n")
        
        # Wireframe instructions
        if wireframe_instructions:
            report.append("## 🎨 Visual Design Changes\n")
            
            overall = wireframe_instructions.get('overall_changes', '')
            if overall:
                report.append(f"**Overall:** {overall}\n")
            
            priority_fixes = wireframe_instructions.get('priority_fixes', [])
            if priority_fixes:
                report.append("**Priority Visual Fixes:**")
                for fix in priority_fixes:
                    report.append(f"- {fix}")
                report.append("")
            
            color_adj = wireframe_instructions.get('color_adjustments', [])
            if color_adj:
                report.append("**Color Adjustments:**")
                for adj in color_adj:
                    report.append(f"- {adj}")
                report.append("")
            
            typo_changes = wireframe_instructions.get('typography_changes', [])
            if typo_changes:
                report.append("**Typography Changes:**")
                for change in typo_changes:
                    report.append(f"- {change}")
                report.append("")
        
        return "\n".join(report)