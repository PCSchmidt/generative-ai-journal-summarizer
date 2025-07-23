#!/usr/bin/env python3
"""
Quick HuggingFace API Test
Simple test to verify HuggingFace models are working
"""

import json
import asyncio
import sys

# Try to import httpx
try:
    import httpx
except ImportError:
    print("❌ httpx not installed. Please run: pip install httpx")
    sys.exit(1)

RAILWAY_API = "https://ai-journal-backend-production.up.railway.app"

async def quick_test():
    """Quick test of HuggingFace models"""
    
    # Test data
    test_text = "Today was incredible! I finally got the promotion I've been working toward for months. I feel so proud and excited about the new challenges ahead."
    
    models_to_test = [
        "hf-mistral-7b",
        "hf-phi3-medium", 
        "hf-gemma-7b",
        "hf-zephyr-7b"
    ]
    
    print("🧪 Quick HuggingFace Model Test")
    print("=" * 50)
    
    # Test API health first
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            health_response = await client.get(f"{RAILWAY_API}/health")
            if health_response.status_code == 200:
                print("✅ API is healthy and responding")
                print(f"   Response: {health_response.json()}")
            else:
                print(f"❌ API health check failed: {health_response.status_code}")
                return
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return
    
    print(f"\n📝 Testing with entry: \"{test_text[:50]}...\"")
    print("-" * 50)
    
    # Test each HuggingFace model for sentiment analysis
    for model in models_to_test:
        print(f"\n🤖 Testing {model}...")
        
        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                response = await client.post(
                    f"{RAILWAY_API}/api/ai/sentiment",
                    json={
                        "text": test_text,
                        "task_type": "sentiment",
                        "model": model
                    },
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    print(f"   ✅ SUCCESS")
                    print(f"   📊 Confidence: {result.get('confidence', 'N/A')}")
                    print(f"   📝 Response Length: {len(result.get('result', ''))}")
                    
                    # Check for boilerplate
                    response_text = result.get('result', '').lower()
                    boilerplate_indicators = [
                        "i don't have access",
                        "i cannot analyze", 
                        "based on the general",
                        "this appears to be",
                        "i'm not able to",
                        "as an ai, i cannot",
                        "fallback response"
                    ]
                    
                    is_boilerplate = any(indicator in response_text for indicator in boilerplate_indicators)
                    
                    if is_boilerplate:
                        print(f"   ⚠️  WARNING: Appears to be boilerplate/fallback response")
                    else:
                        print(f"   ✨ SUCCESS: Genuine AI response detected")
                    
                    print(f"   💬 Response: {result.get('result', 'No response')[:150]}...")
                    
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    print(f"   📄 Response: {response.text[:200]}...")
                    
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    print(f"\n{'='*50}")
    print("✅ Test completed!")
    print("\n💡 To test more thoroughly:")
    print("   1. Open test_hf_models.html in your browser")
    print("   2. Or run the full Python test suite")
    print("\n🔍 If you see boilerplate responses:")
    print("   • Check HUGGINGFACE_API_KEY in Railway environment")
    print("   • Verify HuggingFace API quota/limits")
    print("   • Check Railway logs for API errors")

if __name__ == "__main__":
    asyncio.run(quick_test())
