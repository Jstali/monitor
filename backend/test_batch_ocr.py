"""
Test script for Batch OCR service
Tests the parallel processing capabilities
"""

import os
import sys
import time
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from ocr_service import create_ocr_service
from config import Config
import json

def test_batch_ocr():
    """Test Batch OCR service"""
    
    print("=" * 60)
    print("Testing Batch OCR Processing")
    print("=" * 60)
    
    # Get API key from config
    api_key = Config.MISTRAL_API_KEY
    api_url = Config.MISTRAL_API_URL
    
    if not api_key or api_key == 'your-api-key-here':
        print("\n❌ ERROR: MISTRAL_API_KEY not configured")
        return False
    
    # Create OCR service
    print("\n📝 Creating OCR service...")
    ocr_service = create_ocr_service(api_key, api_url)
    
    # Find screenshot files
    screenshot_folder = Config.SCREENSHOT_FOLDER
    screenshot_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        screenshot_files.extend(list(Path(screenshot_folder).glob(ext)))
    
    if len(screenshot_files) < 2:
        print("⚠️  Need at least 2 screenshots to test batch processing")
        return True
    
    # Take up to 3 screenshots for testing
    test_files = [str(f) for f in screenshot_files[:3]]
    print(f"\n✅ Found {len(screenshot_files)} screenshots, testing with {len(test_files)}")
    
    # Test Sequential (for baseline)
    print("\n1️⃣  Testing Sequential Processing (Baseline)...")
    start_time = time.time()
    # We'll simulate sequential by calling extract_text_from_image in a loop
    for path in test_files:
        ocr_service.extract_text_from_image(path)
    sequential_time = time.time() - start_time
    print(f"   Time taken: {sequential_time:.2f} seconds")
    print(f"   Rate: {len(test_files) / sequential_time * 60:.2f} images/min")
    
    # Test Parallel
    print("\n2️⃣  Testing Parallel Processing (Batch)...")
    start_time = time.time()
    results = ocr_service.extract_batch_parallel(test_files, max_workers=5)
    parallel_time = time.time() - start_time
    print(f"   Time taken: {parallel_time:.2f} seconds")
    print(f"   Rate: {len(test_files) / parallel_time * 60:.2f} images/min")
    
    # Calculate Speedup
    speedup = sequential_time / parallel_time
    print(f"\n🚀 Speedup: {speedup:.2f}x")
    
    # Verify results
    success_count = sum(1 for _, (text, _) in results.items() if text)
    print(f"\n📊 Success Rate: {success_count}/{len(test_files)}")
    
    if success_count == len(test_files):
        print("\n✅ Batch OCR test completed successfully!")
        return True
    else:
        print("\n⚠️  Some images failed to process")
        return False

if __name__ == '__main__':
    test_batch_ocr()
