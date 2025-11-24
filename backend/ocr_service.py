"""
OCR Service using Mistral API
Handles text extraction and analysis from screenshots
"""

import os
import base64
import json
import logging
from typing import Dict, Optional, Tuple
import requests
from PIL import Image
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MistralOCRService:
    """OCR service using Mistral Vision API"""
    
    def __init__(self, api_key: str, api_url: str = "https://api.mistral.ai/v1/chat/completions"):
        """
        Initialize Mistral OCR service
        
        Args:
            api_key: Mistral API key
            api_url: Mistral API endpoint URL
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model = "pixtral-12b-2409"  # Mistral's vision model
        self.timeout = 30
        
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        Encode image file to base64 string
        
        Args:
            image_path: Path to image file
            
        Returns:
            Base64 encoded string
        """
        try:
            # Open and potentially compress image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (max 2048px on longest side)
                max_size = 2048
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                img_bytes = buffer.getvalue()
                
            return base64.b64encode(img_bytes).decode('utf-8')
            
        except Exception as e:
            logger.error(f"Error encoding image: {str(e)}")
            raise
    
    def extract_text_from_image(self, image_path: str) -> Tuple[str, Dict]:
        """
        Extract text and structured data from screenshot using Mistral Vision API
        
        Args:
            image_path: Path to screenshot file
            
        Returns:
            Tuple of (extracted_text, extraction_data)
        """
        try:
            # Encode image
            base64_image = self.encode_image_to_base64(image_path)
            
            # Prepare the prompt for structured extraction
            prompt = """Analyze this screenshot and extract the following information:
1. Application name or website being used
2. Main action or activity visible in the screenshot
3. Context or additional details about what the user is doing
4. Any visible text content (OCR)

Please respond in valid JSON format. Ensure all newlines within string values are escaped as \\n.
{
    "app": "application or website name",
    "action": "main action or activity",
    "context": "brief context or details",
    "text_content": "visible text extracted from screenshot (escape newlines)",
    "confidence": 0.0-1.0
}"""
            
            # Prepare API request
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": f"data:image/png;base64,{base64_image}"
                            }
                        ]
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 1000
            }
            
            # Make API request
            logger.info(f"Sending OCR request to Mistral API for image: {image_path}")
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            if 'choices' not in result or len(result['choices']) == 0:
                raise ValueError("No response from Mistral API")
            
            content = result['choices'][0]['message']['content']
            
            # Try to parse JSON from response
            try:
                # Extract JSON from markdown code blocks if present
                if '```json' in content:
                    json_start = content.find('```json') + 7
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                elif '```' in content:
                    json_start = content.find('```') + 3
                    json_end = content.find('```', json_start)
                    content = content[json_start:json_end].strip()
                
                # Clean up potential invalid control characters
                # content = content.replace('\n', '\\n').replace('\r', '').replace('\t', '\\t')
                
                extraction_data = json.loads(content)
                
                # Validate required fields
                if 'app' not in extraction_data:
                    extraction_data['app'] = 'Unknown Application'
                if 'action' not in extraction_data:
                    extraction_data['action'] = 'Activity'
                if 'context' not in extraction_data:
                    extraction_data['context'] = ''
                if 'confidence' not in extraction_data:
                    extraction_data['confidence'] = 0.8
                
                # Build extracted text summary
                extracted_text = f"App: {extraction_data['app']}\n"
                extracted_text += f"Action: {extraction_data['action']}\n"
                extracted_text += f"Context: {extraction_data['context']}\n"
                if 'text_content' in extraction_data and extraction_data['text_content']:
                    extracted_text += f"\nVisible Text:\n{extraction_data['text_content']}"
                
                # Add metadata
                extraction_data['source'] = 'mistral_ocr'
                extraction_data['model'] = self.model
                
                logger.info(f"Successfully extracted data from screenshot: {extraction_data['app']}")
                return extracted_text, extraction_data
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from Mistral response, using raw text: {str(e)}")
                # Fallback: use raw response
                extraction_data = {
                    'app': 'Unknown Application',
                    'action': 'Activity Detected',
                    'context': content[:200],
                    'text_content': content,
                    'confidence': 0.6,
                    'source': 'mistral_ocr_raw',
                    'model': self.model
                }
                extracted_text = content
                return extracted_text, extraction_data
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Mistral API request failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            raise
    
    def extract_batch(self, image_paths: list) -> list:
        """
        Extract text from multiple images sequentially (deprecated, use extract_batch_parallel)
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of tuples (extracted_text, extraction_data)
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.extract_text_from_image(image_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {image_path}: {str(e)}")
                results.append((None, None))
        
        return results

    def extract_batch_parallel(self, image_paths: list, max_workers: int = 5) -> Dict[str, Tuple[str, Dict]]:
        """
        Extract text from multiple images in parallel
        
        Args:
            image_paths: List of image file paths
            max_workers: Maximum number of concurrent requests
            
        Returns:
            Dictionary mapping image_path -> (extracted_text, extraction_data)
        """
        import concurrent.futures
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Create a future for each image
            future_to_path = {
                executor.submit(self.extract_text_from_image, path): path 
                for path in image_paths
            }
            
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    extracted_text, extraction_data = future.result()
                    results[path] = (extracted_text, extraction_data)
                except Exception as e:
                    logger.error(f"Failed to process batch item {path}: {str(e)}")
                    results[path] = (None, {'error': str(e)})
                    
        return results


def create_ocr_service(api_key: str, api_url: Optional[str] = None) -> MistralOCRService:
    """
    Factory function to create OCR service instance
    
    Args:
        api_key: Mistral API key
        api_url: Optional custom API URL
        
    Returns:
        MistralOCRService instance
    """
    if api_url:
        return MistralOCRService(api_key, api_url)
    return MistralOCRService(api_key)


# Example usage
if __name__ == '__main__':
    # Test with environment variable
    api_key = os.getenv('MISTRAL_API_KEY', '')
    
    if not api_key:
        print("Please set MISTRAL_API_KEY environment variable")
        exit(1)
    
    service = create_ocr_service(api_key)
    
    # Test with a sample image
    test_image = 'test_screenshot.png'
    if os.path.exists(test_image):
        text, data = service.extract_text_from_image(test_image)
        print("Extracted Text:")
        print(text)
        print("\nExtraction Data:")
        print(json.dumps(data, indent=2))
    else:
        print(f"Test image not found: {test_image}")
