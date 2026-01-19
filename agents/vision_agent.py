from google import genai
from google.genai import types
import os
from PIL import Image
import json
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

class VisionAgent:
    """
    Vision Agent: Analyzes mobile UI screenshots and extracts UI components
    """

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found")

        # Initialize modern Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Supported vision capable model
        self.model_name = "gemini-3-flash-preview"

        print("✅ Vision Agent initialized with Gemini (google.genai)")

    def analyze_screenshot(self, image_path: str) -> Dict[str, Any]:
        try:
            print(f" Analyzing screenshot: {image_path}")

            with open(image_path, "rb") as f:
                image_bytes = f.read()

            prompt = self._get_analysis_prompt()

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type="image/png",
                    ),
                    prompt,
                ],
            )

            result = self._parse_response(response.text)

            print("✅ Analysis complete!")
            return result

        except Exception as e:
            print(f"❌ Error analyzing screenshot: {e}")
            return {"error": str(e)}
    
    def _get_analysis_prompt(self):
        """Detailed prompt for UI component extraction"""
        return """
You are a UI/UX analysis expert. Analyze this mobile app screenshot and extract detailed information.

Provide your response ONLY as valid JSON with this exact structure:

{
  "screen_type": "login/home/profile/list/etc",
  "components": [
    {
      "type": "button/text_input/image/label/icon/etc",
      "text": "visible text if any",
      "position": "top/middle/bottom/top-left/etc",
      "color": "describe color",
      "size": "small/medium/large",
      "style": "primary/secondary/text/outlined/etc"
    }
  ],
  "layout_structure": "describe overall layout",
  "color_scheme": {
    "primary_colors": ["list of main colors"],
    "background": "background color",
    "text_colors": ["list of text colors"]
  },
  "typography": {
    "heading_sizes": "describe heading sizes",
    "body_text_size": "describe body text size",
    "font_weights": "describe font weights used"
  },
  "spacing_and_density": {
    "overall_density": "tight/comfortable/spacious",
    "padding": "describe padding",
    "element_spacing": "describe spacing between elements"
  },
  "interactive_elements": [
    {
      "element": "describe element",
      "action": "what it likely does",
      "visibility": "how easy to find/use"
    }
  ],
  "visual_hierarchy": "describe how eye flows through the screen",
  "accessibility_observations": ["list any obvious accessibility issues"],
  "notable_patterns": ["list UI patterns used"]
}

Be specific and detailed. Return ONLY the JSON, no additional text.
"""
    
    def _parse_response(self, response_text):
        """Parse the model's response into structured JSON"""
        try:
            cleaned = response_text.strip()
            
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            result = json.loads(cleaned)
            return result
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Failed to parse JSON, returning raw text")
            return {
                "raw_response": response_text,
                "parse_error": str(e)
            }