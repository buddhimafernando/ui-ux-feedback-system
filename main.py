import os
from dotenv import load_dotenv
from agents.vision_agent import VisionAgent, test_single_image
import json
from pathlib import Path

# Load environment variables
load_dotenv()

def main():
    """
    Main testing script for Day 1
    """
    print("=" * 60)
    print("UX FEEDBACK SYSTEM - DAY 1: VISION AGENT TEST")
    print("=" * 60)
    
    # Initialize Vision Agent
    try:
        agent = VisionAgent()
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("\n📝 Please set GEMINI_API_KEY in your .env file")
        print("   Get free API key from: https://makersuite.google.com/app/apikey")
        return
    
    # Test with single image
    test_image_path = "data/test_screenshots/test_image.png"
    
    if not os.path.exists(test_image_path):
        print(f"\n⚠️  Test image not found: {test_image_path}")
        print("   Please add a mobile UI screenshot to data/test_screenshots/")
        print("   You can use any mobile app screenshot for testing")
        return
    
    # Analyze the image
    print(f"\n📸 Analyzing: {test_image_path}")
    result = agent.analyze_screenshot(test_image_path)
    
    # Save result to JSON
    output_dir = Path("data/outputs")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "vision_analysis_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    
    print(f"\n💾 Result saved to: {output_file}")
    
    # Display summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
    elif "parse_error" in result:
        print(f"⚠️  Parse error: {result['parse_error']}")
        print("\nRaw response:")
        print(result.get('raw_response', 'N/A')[:500])
    else:
        print(f"Screen Type: {result.get('screen_type', 'N/A')}")
        print(f"Components Found: {len(result.get('components', []))}")
        print(f"Layout: {result.get('layout_structure', 'N/A')}")
        print(f"\nColor Scheme:")
        colors = result.get('color_scheme', {})
        print(f"  Primary: {colors.get('primary_colors', 'N/A')}")
        print(f"  Background: {colors.get('background', 'N/A')}")
        
        # Show first 3 components
        components = result.get('components', [])
        if components:
            print(f"\nFirst 3 Components:")
            for i, comp in enumerate(components[:3], 1):
                print(f"  {i}. {comp.get('type', 'unknown')} - {comp.get('text', 'no text')}")
    
    print("\n✅ Day 1 Test Complete!")
    print("\n💡 Next Steps:")
    print("   1. Review the JSON output in data/outputs/")
    print("   2. Test with more screenshots from RICO dataset")
    print("   3. Fine-tune the analysis prompt if needed")

if __name__ == "__main__":
    main()