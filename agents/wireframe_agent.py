import json
import os
from typing import Dict, Any
from pathlib import Path
from google import genai
from datetime import datetime


class WireframeAgent:
    """
    Wireframe Generator Agent: Creates improved UI wireframes based on feedback
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")
        
           # Initialize modern Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Supported vision capable model
        self.model = "gemini-3-flash-preview"
        
        print("✅ Wireframe Agent initialized")
    
    def generate_wireframe(
        self,
        vision_analysis: Dict[str, Any],
        feedback_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate improved wireframe HTML based on feedback
        
        Args:
            vision_analysis: Output from Vision Agent
            feedback_result: Output from Feedback Agent
            
        Returns:
            Dictionary with HTML code and metadata
        """
        try:
            print("\n🎨 Generating improved wireframe...")
            
            # Create wireframe generation prompt
            prompt = self._create_wireframe_prompt(vision_analysis, feedback_result)
            
            # Get AI-generated HTML
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
           
            # Parse and clean HTML
            html_code = self._extract_html(response.text)
            
            # Create complete HTML with viewer
            complete_html = self._create_complete_html(html_code, vision_analysis, feedback_result)
            
            # Save HTML file
            output_path = self._save_html(complete_html)
            
            print(f"✅ Wireframe generated: {output_path}")
            
            return {
                "wireframe_html": html_code,
                "complete_html": complete_html,
                "output_path": str(output_path),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error generating wireframe: {str(e)}")
            return {"error": str(e)}
    
    def _create_wireframe_prompt(
        self,
        vision_analysis: Dict,
        feedback_result: Dict
    ) -> str:
        """Create detailed prompt for wireframe generation"""
        
        screen_type = vision_analysis.get('screen_type', 'mobile app')
        components = vision_analysis.get('components', [])
        color_scheme = vision_analysis.get('color_scheme', {})
        
        feedback_items = feedback_result.get('feedback_items', [])
        wireframe_instructions = feedback_result.get('wireframe_instructions', {})
        
        prompt = f"""
You are an expert UI/UX designer. Create an IMPROVED mobile UI wireframe in HTML/CSS based on the original design analysis and feedback.

## ORIGINAL DESIGN ANALYSIS

**Screen Type:** {screen_type}

**Components:**
{json.dumps(components[:10], indent=2)}

**Color Scheme:**
{json.dumps(color_scheme, indent=2)}

## FEEDBACK TO IMPLEMENT

**Feedback Items:**
{json.dumps(feedback_items, indent=2)}

**Wireframe Instructions:**
{json.dumps(wireframe_instructions, indent=2)}

## YOUR TASK

Create a COMPLETE, IMPROVED mobile UI wireframe as a single HTML file with embedded CSS.

**Requirements:**

1. **Mobile-first design** (max-width: 375px, scale up for display)
2. **Implement ALL feedback suggestions:**
   - Fix color contrast issues
   - Adjust typography sizes
   - Improve spacing and layout
   - Add missing UI elements (loading indicators, labels, etc.)
   - Fix inconsistencies

3. **Use modern CSS:**
   - Flexbox/Grid for layout
   - Proper spacing (padding, margins)
   - Mobile-friendly touch targets (min 44px)
   - Smooth transitions and hover states

4. **Include annotations:**
   - Add small labels showing what was improved
   - Use a subtle annotation style (small text, muted color)

5. **Make it realistic but clean:**
   - Use actual UI components (buttons, cards, inputs)
   - Include icons (use emoji or Unicode symbols)
   - Proper visual hierarchy

## OUTPUT FORMAT

Return ONLY the HTML code inside a single code block, like this:
```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Improved Mobile UI Wireframe</title>
    <style>
        /* Your CSS here */
    </style>
</head>
<body>
    <!-- Your improved UI here -->
</body>
</html>
```

Create a complete, functional wireframe that clearly shows the improvements.
Make it look professional and polished.
"""
        return prompt
    
    def _extract_html(self, response_text: str) -> str:
        """Extract HTML code from AI response"""
        
        # Remove markdown code blocks
        cleaned = response_text.strip()
        
        if "```html" in cleaned:
            # Extract content between ```html and ```
            start = cleaned.find("```html") + 7
            end = cleaned.find("```", start)
            cleaned = cleaned[start:end].strip()
        elif "```" in cleaned:
            # Extract content between ``` and ```
            start = cleaned.find("```") + 3
            end = cleaned.find("```", start)
            cleaned = cleaned[start:end].strip()
        
        # Ensure it starts with <!DOCTYPE or <html
        if not (cleaned.startswith("<!DOCTYPE") or cleaned.startswith("<html")):
            # Wrap in basic HTML structure
            cleaned = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wireframe</title>
</head>
<body>
{cleaned}
</body>
</html>"""
        
        return cleaned
    
    def _create_complete_html(
        self,
        wireframe_html: str,
        vision_analysis: Dict,
        feedback_result: Dict
    ) -> str:
        """Create complete HTML with wireframe viewer and export functionality"""
        
        summary = feedback_result.get('summary', {})
        
        complete_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UX Feedback - Improved Wireframe</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .stats {{
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            color: white;
        }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        
        .stat-item {{
            text-align: center;
            padding: 15px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        
        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        .wireframe-section {{
            background: white;
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }}
        
        .controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }}
        
        .btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .btn-secondary {{
            background: #48bb78;
            color: white;
        }}
        
        .btn-secondary:hover {{
            background: #38a169;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(72, 187, 120, 0.4);
        }}
        
        .wireframe-viewer {{
            background: #f7fafc;
            border-radius: 15px;
            padding: 20px;
            min-height: 600px;
            border: 2px solid #e2e8f0;
        }}
        
        .wireframe-iframe {{
            width: 100%;
            min-height: 800px;
            border: none;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .info {{
            margin-top: 20px;
            padding: 15px;
            background: #ebf8ff;
            border-left: 4px solid #3182ce;
            border-radius: 5px;
        }}
        
        .info h3 {{
            color: #2c5282;
            margin-bottom: 10px;
        }}
        
        .info ul {{
            margin-left: 20px;
            color: #2d3748;
        }}
        
        .info li {{
            margin: 5px 0;
        }}
        
        @media (max-width: 768px) {{
            .header h1 {{
                font-size: 1.8em;
            }}
            
            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .controls {{
                flex-direction: column;
            }}
            
            .btn {{
                width: 100%;
                justify-content: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 Improved UI Wireframe</h1>
            <p>Based on UX Heuristic Evaluation & Feedback</p>
        </div>
        
        <div class="stats">
            <h2>📊 Evaluation Summary</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <span class="stat-value">{summary.get('total_issues', 0)}</span>
                    <span class="stat-label">Total Issues</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" style="color: #f56565;">{summary.get('high', 0)}</span>
                    <span class="stat-label">High Priority</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" style="color: #ed8936;">{summary.get('medium', 0)}</span>
                    <span class="stat-label">Medium Priority</span>
                </div>
                <div class="stat-item">
                    <span class="stat-value" style="color: #48bb78;">{summary.get('low', 0)}</span>
                    <span class="stat-label">Low Priority</span>
                </div>
            </div>
        </div>
        
        <div class="wireframe-section">
            <div class="controls">
                <button class="btn btn-primary" onclick="exportAsPNG()">
                    📥 Export as PNG
                </button>
                <button class="btn btn-secondary" onclick="exportAsJPG()">
                    📥 Export as JPG
                </button>
                <button class="btn btn-primary" onclick="downloadHTML()">
                    💾 Download HTML
                </button>
            </div>
            
            <div class="wireframe-viewer">
                <iframe 
                    id="wireframe-iframe" 
                    class="wireframe-iframe"
                    srcdoc='{wireframe_html.replace("'", "&#39;")}'
                ></iframe>
            </div>
            
            <div class="info">
                <h3>ℹ️ How to Export</h3>
                <ul>
                    <li><strong>Export as PNG/JPG:</strong> Click the export button to download the wireframe as an image</li>
                    <li><strong>Download HTML:</strong> Get the complete HTML code to edit further</li>
                    <li><strong>View in Browser:</strong> This page is already saved and can be opened in any browser</li>
                </ul>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script>
        async function exportAsPNG() {{
            const iframe = document.getElementById('wireframe-iframe');
            const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
            
            try {{
                const canvas = await html2canvas(iframeDocument.body, {{
                    scale: 2,
                    backgroundColor: '#ffffff',
                    logging: false
                }});
                
                canvas.toBlob(function(blob) {{
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'improved-wireframe-' + Date.now() + '.png';
                    a.click();
                    URL.revokeObjectURL(url);
                }});
                
                showNotification('PNG export started!');
            }} catch (error) {{
                console.error('Export error:', error);
                alert('Export failed. Try downloading the HTML instead.');
            }}
        }}
        
        async function exportAsJPG() {{
            const iframe = document.getElementById('wireframe-iframe');
            const iframeDocument = iframe.contentDocument || iframe.contentWindow.document;
            
            try {{
                const canvas = await html2canvas(iframeDocument.body, {{
                    scale: 2,
                    backgroundColor: '#ffffff',
                    logging: false
                }});
                
                canvas.toBlob(function(blob) {{
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'improved-wireframe-' + Date.now() + '.jpg';
                    a.click();
                    URL.revokeObjectURL(url);
                }}, 'image/jpeg', 0.95);
                
                showNotification('JPG export started!');
            }} catch (error) {{
                console.error('Export error:', error);
                alert('Export failed. Try downloading the HTML instead.');
            }}
        }}
        
        function downloadHTML() {{
            const iframe = document.getElementById('wireframe-iframe');
            const html = iframe.srcdoc;
            
            const blob = new Blob([html], {{ type: 'text/html' }});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'improved-wireframe-' + Date.now() + '.html';
            a.click();
            URL.revokeObjectURL(url);
            
            showNotification('HTML downloaded!');
        }}
        
        function showNotification(message) {{
            const notification = document.createElement('div');
            notification.textContent = message;
            notification.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #48bb78;
                color: white;
                padding: 15px 25px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                z-index: 10000;
                animation: slideIn 0.3s ease;
            `;
            document.body.appendChild(notification);
            
            setTimeout(() => {{
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }}, 3000);
        }}
    </script>
    
    <style>
        @keyframes slideIn {{
            from {{ transform: translateX(400px); opacity: 0; }}
            to {{ transform: translateX(0); opacity: 1; }}
        }}
        
        @keyframes slideOut {{
            from {{ transform: translateX(0); opacity: 1; }}
            to {{ transform: translateX(400px); opacity: 0; }}
        }}
    </style>
</body>
</html>"""
        
        return complete_html
    
    def _save_html(self, html_content: str) -> Path:
        """Save HTML to file"""
        output_dir = Path("data/outputs")
        output_dir.mkdir(exist_ok=True, parents=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"wireframe_{timestamp}.html"
        output_path = output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path