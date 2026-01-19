from agents.vision_agent import VisionAgent
from agents.heuristic_agent import HeuristicAgent
from agents.feedback_agent import FeedbackAgent
import json
from pathlib import Path


def test_full_pipeline(image_path: str, platform: str = "android"):
    """
    Complete 3-agent pipeline test:
    Vision → Heuristic → Feedback
    """
    
    print("=" * 70)
    print("TESTING COMPLETE FEEDBACK GENERATION PIPELINE")
    print("=" * 70)
    
    # Step 1: Vision Analysis
    print("\n STEP 1: Analyzing UI with Vision Agent...")
    vision_agent = VisionAgent()
    vision_result = vision_agent.analyze_screenshot(image_path)

    # Save vision result
    Path("data/outputs").mkdir(exist_ok=True, parents=True)
    with open("data/outputs/vision_result.json", 'w') as f:
        json.dump(vision_result, f, indent=2)
    
    # Step 2: Heuristic Evaluation
    print("\n STEP 2: Evaluating against heuristics...")
    heuristic_agent = HeuristicAgent()
    evaluation_result = heuristic_agent.evaluate(vision_result)

    # Save evaluation result
    with open("data/outputs/heuristic_evaluation.json", 'w') as f:
        json.dump(evaluation_result, f, indent=2)

    # Step 3: Generate Report
    print("\n STEP 3: Generating report...")
    report = heuristic_agent.generate_report(evaluation_result)
    
    # Save report
    with open("data/outputs/evaluation_report.txt", 'w') as f:
        f.write(report)

    # Step 4: Generate Feedback
    print(f"\n STEP 4: Generating developer feedback for {platform}...")
    feedback_agent = FeedbackAgent()
    feedback_result = feedback_agent.generate_feedback(
        vision_result,
        evaluation_result,
        platform=platform
    )
    
    # Save all outputs
    Path("data/outputs").mkdir(exist_ok=True, parents=True)
    
    # with open("data/outputs/1_vision_analysis.json", 'w') as f:
    #     json.dump(vision_result, f, indent=2)
    
    # with open("data/outputs/2_heuristic_evaluation.json", 'w') as f:
    #     json.dump(evaluation_result, f, indent=2)
    
    with open("data/outputs/feedback_file.json", 'w') as f:
        json.dump(feedback_result, f, indent=2)
    
    # Generate developer report
    print("\n STEP 5: Generating developer report...")
    report = feedback_agent.generate_developer_report(feedback_result)
    
    with open("data/outputs/DEVELOPER_FEEDBACK.md", 'w') as f:
        f.write(report)
    
    # Display report
    # print("\n" + report)
    
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE!")
    print("=" * 70)
    print("\n📁 Outputs saved:")
    print("   - data/outputs/1_vision_analysis.json")
    print("   - data/outputs/2_heuristic_evaluation.json")
    print("   - data/outputs/3_feedback.json")
    print("   - data/outputs/DEVELOPER_FEEDBACK.md")
    
    return feedback_result


if __name__ == "__main__":
    # Test with your quiz app screenshot
    image_path = "data/test_screenshots/test_image.PNG"
    
    # You can change platform to "ios" or "react-native"
    test_full_pipeline(image_path, platform="android")