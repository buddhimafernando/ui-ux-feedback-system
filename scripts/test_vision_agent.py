from agents.vision_agent import VisionAgent

# Initialize agent (make sure GEMINI_API_KEY is set in your environment)
agent = VisionAgent()

# Path to your mobile UI screenshot
image_path = "data/test_screenshots/test_image.png"

# Analyze screenshot
result = agent.analyze_screenshot(image_path)

# Pretty-print the result
import json
print(json.dumps(result, indent=2))
