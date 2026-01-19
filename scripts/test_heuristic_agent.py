from agents.vision_agent import VisionAgent
from agents.heuristic_agent import HeuristicAgent
import json
from pathlib import Path


def test_heuristic_evaluation(image_path: str):
    """
    End-to-end test: Vision Analysis → Heuristic Evaluation
    """
    
    print("=" * 70)
    print("TESTING HEURISTIC EVALUATION PIPELINE")
    print("=" * 70)
    
    # Step 1: Vision Analysis
    print("\n STEP 1: Analyzing UI with Vision Agent...")
    vision_agent = VisionAgent()
    vision_result = vision_agent.analyze_screenshot(image_path)
    
    # Save vision result
    Path("data/outputs").mkdir(exist_ok=True, parents=True)
    with open("data/outputs/h_vision_result.json", 'w') as f:
        json.dump(vision_result, f, indent=2)
    
    print("✅ Vision analysis complete")
    
    # Step 2: Heuristic Evaluation
    print("\n🔍 STEP 2: Evaluating against heuristics...")
    heuristic_agent = HeuristicAgent()
    evaluation_result = heuristic_agent.evaluate(vision_result)
    
    # Save evaluation result
    with open("data/outputs/h_heuristic_evaluation.json", 'w') as f:
        json.dump(evaluation_result, f, indent=2)
    
    print("✅ Heuristic evaluation complete")
    
    # Step 3: Generate Report
    print("\n📄 STEP 3: Generating report...")
    report = heuristic_agent.generate_report(evaluation_result)
    
    # Save report
    with open("data/outputs/h_evaluation_report.txt", 'w') as f:
        f.write(report)
    
    # Display report
    print("\n" + report)
    
    print("\n✅ All outputs saved to data/outputs/")
    print("   - vision_result.json")
    print("   - heuristic_evaluation.json")
    print("   - evaluation_report.txt")
    
    return evaluation_result


if __name__ == "__main__":
    # Test with your quiz app screenshot
    image_path = "data/test_screenshots/test_image.PNG"
    test_heuristic_evaluation(image_path)