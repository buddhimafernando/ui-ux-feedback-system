"""
Simple BLIP-2 Test for M4 Mac
No CrewAI - just testing if BLIP-2 works
"""

import torch
from transformers import Blip2Processor, Blip2ForConditionalGeneration
from PIL import Image
import os
import time

def test_blip2_basic():
    """Test BLIP-2 without CrewAI"""
    
    print("🧪 Testing BLIP-2 on M4 Mac")
    print("="*60)
    
    # Step 1: Check MPS
    print("\n1️⃣ Checking Apple Silicon GPU...")
    if torch.backends.mps.is_available():
        device = "mps"
        print("   ✅ MPS (Apple GPU) Available!")
        print("   🚀 Will use M4 Neural Engine + GPU")
    else:
        device = "cpu"
        print("   ⚠️  MPS not available, using CPU")
    
    # Step 2: Load model
    print("\n2️⃣ Loading BLIP-2 model...")
    print("   (First time: ~2GB download, please wait...)")
    
    try:
        # processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
        # model = Blip2ForConditionalGeneration.from_pretrained(
        #     "Salesforce/blip2-opt-2.7b",
        #     torch_dtype=torch.float32,  # MPS requires float32
        # )
        processor = Blip2Processor.from_pretrained("Salesforce/blip2-flan-t5-xl")
        model = Blip2ForConditionalGeneration.from_pretrained(
            "Salesforce/blip2-flan-t5-xl",
            torch_dtype=torch.float32,
        )

        
        # Move to device
        model = model.to(device)
        model.eval()  # Set to inference mode
        
        print("   ✅ Model loaded successfully!")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("\n💡 Try:")
        print("   pip install --upgrade transformers torch")
        return False
    
    # Step 3: Test with image
    print("\n3️⃣ Testing image analysis...")
    
    # Check for test image
    test_image_path = "data/test_screenshots/test_image.png"
    
    if not os.path.exists(test_image_path):
        print(f"   ⚠️  No test image found")
        print(f"   📁 Creating test directory...")
        os.makedirs("data/test_screenshots", exist_ok=True)
        
        # Create a simple colored image for testing
        test_img = Image.new('RGB', (400, 600), color=(52, 152, 219))
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.ImageDraw(test_img)
        draw.rectangle([50, 200, 350, 260], fill=(255, 255, 255))
        draw.rectangle([50, 300, 350, 360], fill=(46, 204, 113))
        
        test_img.save(test_image_path)
        print(f"   ✅ Created test image at {test_image_path}")
    
    # Load image
    image = Image.open(test_image_path).convert("RGB")
    print(f"   📸 Image loaded: {image.size}")
    
    # Test 1: Simple caption
    print("\n   Test 1: Image Captioning")
    start = time.time()
    
    inputs = processor(image, return_tensors="pt").to(device)
    
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=50)
    
    caption = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    elapsed = time.time() - start
    
    print(f"   Caption: {caption}")
    print(f"   ⏱️  Time: {elapsed:.2f} seconds")
    
    # Test 2: Visual Question Answering
    print("\n   Test 2: Visual Question Answering")
    question = "What colors do you see in this image?"
    
    start = time.time()
    inputs = processor(image, question, return_tensors="pt").to(device)
    
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=50)
    
    answer = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    elapsed = time.time() - start
    
    print(f"   Question: {question}")
    print(f"   Answer: {answer}")
    print(f"   ⏱️  Time: {elapsed:.2f} seconds")
    
    # Test 3: UI Analysis Question
    print("\n   Test 3: UI-Specific Question")
    ui_question = "What user interface elements do you see?"
    
    start = time.time()
    inputs = processor(image, ui_question, return_tensors="pt").to(device)
    
    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=80)
    
    ui_answer = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
    elapsed = time.time() - start
    
    print(f"   Question: {ui_question}")
    print(f"   Answer: {ui_answer}")
    print(f"   ⏱️  Time: {elapsed:.2f} seconds")
    
    # Summary
    print("\n" + "="*60)
    print("✅ BLIP-2 is working on your M4 Mac!")
    print("="*60)
    print(f"\n📊 Performance Summary:")
    print(f"   Device: {device.upper()}")
    print(f"   Model: BLIP-2 OPT 2.7B")
    print(f"   Expected speed: 3-8 seconds per question")
    
    if device == "mps":
        print(f"\n🚀 Your M4 is running BLIP-2 with GPU acceleration!")
    else:
        print(f"\n⚠️  Running on CPU - slower but works")
    
    print("\n💡 Next steps:")
    print("   1. Add your own mobile UI screenshot to data/test_screenshots/")
    print("   2. Run this test again to analyze real UI")
    print("   3. Integrate with CrewAI for full system")
    
    return True


if __name__ == "__main__":
    success = test_blip2_basic()
    
    if success:
        print("\n🎉 Ready to build your UI/UX feedback system!")
    else:
        print("\n❌ Setup incomplete. Check errors above.")