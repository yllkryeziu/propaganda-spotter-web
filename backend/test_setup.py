#!/usr/bin/env python3
"""
Test script to verify backend setup and model loading
"""

import sys
import asyncio
from PIL import Image
import numpy as np

def test_imports():
    """Test that all required packages can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__}")
        
        import transformers
        print(f"✅ Transformers {transformers.__version__}")
        
        import cv2
        print(f"✅ OpenCV {cv2.__version__}")
        
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__}")
        
        from PIL import Image
        print("✅ PIL/Pillow")
        
        import numpy as np
        print(f"✅ NumPy {np.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_model_loading():
    """Test that AI models can be loaded"""
    print("\n🤖 Testing model loading...")
    
    try:
        from models.propaganda_detector import PropagandaDetector
        
        print("Loading propaganda detection model...")
        detector = PropagandaDetector()
        print("✅ Propaganda detector loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading error: {e}")
        return False

async def test_analysis():
    """Test image analysis with a simple test image"""
    print("\n🖼️  Testing image analysis...")
    
    try:
        from models.propaganda_detector import PropagandaDetector
        
        # Create a simple test image
        test_image = Image.new('RGB', (256, 256), color='red')
        
        detector = PropagandaDetector()
        result = await detector.analyze_image(test_image)
        
        print(f"✅ Analysis completed in {result['processing_time']:.2f}s")
        print(f"✅ Found {len(result['detections'])} detections")
        print(f"✅ Overall confidence: {result['overall_confidence']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return False

def test_api_setup():
    """Test that FastAPI app can be imported"""
    print("\n🌐 Testing API setup...")
    
    try:
        from main import app
        print("✅ FastAPI app imported successfully")
        
        # Test that endpoints exist
        routes = [route.path for route in app.routes]
        expected_routes = ["/", "/health", "/analyze"]
        
        for route in expected_routes:
            if route in routes:
                print(f"✅ Route {route} exists")
            else:
                print(f"❌ Route {route} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ API setup error: {e}")
        return False

async def main():
    """Run all tests"""
    print("🚀 Starting Propaganda Spotter Backend Tests\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Model Loading Test", test_model_loading),
        ("API Setup Test", test_api_setup),
        ("Analysis Test", test_analysis),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"Running: {test_name}")
        print(f"{'='*50}")
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Backend is ready to use.")
        return 0
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
