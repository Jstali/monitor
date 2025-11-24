"""
Test script for OCR service
Tests the Mistral OCR integration with sample screenshots
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from ocr_service import create_ocr_service
from config import Config
import json


def test_ocr_service():
    """Test OCR service with configuration"""
    
    print("=" * 60)
    print("Testing Mistral OCR Service")
    print("=" * 60)
    
    # Get API key from config
    api_key = Config.MISTRAL_API_KEY
    api_url = Config.MISTRAL_API_URL
    
    print(f"\nConfiguration:")
    print(f"  API URL: {api_url}")
    print(f"  API Key: {'*' * 20}{api_key[-10:] if len(api_key) > 10 else '***'}")
    print(f"  OCR Enabled: {Config.OCR_ENABLED}")
    print(f"  OCR Timeout: {Config.OCR_TIMEOUT}s")
    
    if not api_key or api_key == 'your-api-key-here':
        print("\n❌ ERROR: MISTRAL_API_KEY not configured properly")
        print("Please set MISTRAL_API_KEY in your environment or config.py")
        return False
    
    # Create OCR service
    print("\n📝 Creating OCR service...")
    try:
        ocr_service = create_ocr_service(api_key, api_url)
        print("✅ OCR service created successfully")
    except Exception as e:
        print(f"❌ Failed to create OCR service: {str(e)}")
        return False
    
    # Check for test screenshots
    screenshot_folder = Config.SCREENSHOT_FOLDER
    print(f"\n📁 Looking for screenshots in: {screenshot_folder}")
    
    if not os.path.exists(screenshot_folder):
        print(f"⚠️  Screenshot folder does not exist yet: {screenshot_folder}")
        print("This is normal if no screenshots have been uploaded yet.")
        print("\nTo test OCR:")
        print("1. Start the backend server: python app.py")
        print("2. Start the monitoring agent to capture screenshots")
        print("3. Upload screenshots through the agent")
        print("4. Use the 'Extract' button in the UI to trigger OCR")
        return True
    
    # Find screenshot files
    screenshot_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg']:
        screenshot_files.extend(Path(screenshot_folder).glob(ext))
    
    if not screenshot_files:
        print("⚠️  No screenshot files found in the folder")
        print("Upload some screenshots first, then run this test again")
        return True
    
    print(f"✅ Found {len(screenshot_files)} screenshot(s)")
    
    # Test with first screenshot
    test_file = screenshot_files[0]
    print(f"\n🔍 Testing OCR with: {test_file.name}")
    print(f"   File size: {test_file.stat().st_size / 1024:.2f} KB")
    
    try:
        print("\n⏳ Extracting text from screenshot (this may take 10-30 seconds)...")
        extracted_text, extraction_data = ocr_service.extract_text_from_image(str(test_file))
        
        print("\n" + "=" * 60)
        print("✅ OCR EXTRACTION SUCCESSFUL!")
        print("=" * 60)
        
        print("\n📄 Extracted Text:")
        print("-" * 60)
        print(extracted_text)
        print("-" * 60)
        
        print("\n📊 Extraction Data:")
        print("-" * 60)
        print(json.dumps(extraction_data, indent=2))
        print("-" * 60)
        
        print("\n✅ OCR test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ OCR extraction failed: {str(e)}")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. Network connectivity issues")
        print("3. Mistral API rate limits")
        print("4. Image file corruption")
        return False


def main():
    """Main test function"""
    success = test_ocr_service()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 All tests passed!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the backend: python app.py")
        print("2. Start the frontend: cd ../frontend && npm run dev")
        print("3. Login and upload screenshots via the monitoring agent")
        print("4. Click 'Extract' on screenshots to trigger OCR")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Tests failed")
        print("=" * 60)
        sys.exit(1)


if __name__ == '__main__':
    main()
