from agents.vision_agent import VisionAgent
from agents.heuristic_agent import HeuristicAgent
from agents.feedback_agent import FeedbackAgent
from agents.wireframe_agent import WireframeAgent
import json
from pathlib import Path
import webbrowser


def test_complete_pipeline(image_path: str):
    """
    Complete 4-agent pipeline test:
    Vision → Heuristic → Feedback → Wireframe
    """
    
    print("=" * 70)
    print("🚀 TESTING COMPLETE UX FEEDBACK SYSTEM")
    print("=" * 70)
    
    # Step 1: Vision Analysis
    print("\n📸 STEP 1: Analyzing UI with Vision Agent...")
    vision_agent = VisionAgent()
    vision_result = vision_agent.analyze_screenshot(image_path)
    
    # Step 2: Heuristic Evaluation
    print("\n🔍 STEP 2: Evaluating against heuristics...")
    heuristic_agent = HeuristicAgent()
    evaluation_result = heuristic_agent.evaluate(vision_result)
    
    # Step 3: Generate Feedback
    print("\n💡 STEP 3: Generating developer feedback...")
    feedback_agent = FeedbackAgent()
    feedback_result = feedback_agent.generate_feedback(
        vision_result,
        evaluation_result
    )
    
    # Step 4: Generate Wireframe
    print("\n🎨 STEP 4: Generating improved wireframe...")
    wireframe_agent = WireframeAgent()
    wireframe_result = wireframe_agent.generate_wireframe(
        vision_result,
        feedback_result
    )
    
    # Save all outputs
    output_dir = Path("data/outputs")
    output_dir.mkdir(exist_ok=True, parents=True)
    
    with open(output_dir / "1_vision_analysis.json", 'w') as f:
        json.dump(vision_result, f, indent=2)
    
    with open(output_dir / "2_heuristic_evaluation.json", 'w') as f:
        json.dump(evaluation_result, f, indent=2)
    
    with open(output_dir / "3_feedback.json", 'w') as f:
        json.dump(feedback_result, f, indent=2)
    
    with open(output_dir / "4_wireframe_metadata.json", 'w') as f:
        json.dump({
            "output_path": wireframe_result.get("output_path"),
            "timestamp": wireframe_result.get("timestamp")
        }, f, indent=2)
    
    # Generate developer report
    print("\n📄 STEP 5: Generating reports...")
    report = feedback_agent.generate_developer_report(feedback_result)
    
    with open(output_dir / "DEVELOPER_FEEDBACK.md", 'w') as f:
        f.write(report)
    
    print("\n" + "=" * 70)
    print("✅ COMPLETE PIPELINE FINISHED!")
    print("=" * 70)
    print("\n📁 All outputs saved to data/outputs/:")
    print("   ├── 1_vision_analysis.json")
    print("   ├── 2_heuristic_evaluation.json")
    print("   ├── 3_feedback.json")
    print("   ├── 4_wireframe_metadata.json")
    print("   ├── DEVELOPER_FEEDBACK.md")
    print(f"   └── {Path(wireframe_result.get('output_path', '')).name}")
    
    # Open wireframe in browser
    wireframe_path = wireframe_result.get('output_path')
    if wireframe_path:
        print(f"\n🌐 Opening wireframe in browser...")
        webbrowser.open(f'file://{Path(wireframe_path).absolute()}')
    
    return {
        "vision": vision_result,
        "evaluation": evaluation_result,
        "feedback": feedback_result,
        "wireframe": wireframe_result
    }


if __name__ == "__main__":
    # Test with your quiz app screenshot
    image_path = "data/test_screenshots/test_image.png"
    test_complete_pipeline(image_path)