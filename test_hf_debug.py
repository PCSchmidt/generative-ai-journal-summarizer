#!/usr/bin/env python3
"""
Test HuggingFace API with detailed debugging
This will call the Railway API and show us exactly what's happening
"""

import asyncio
import httpx
import json

RAILWAY_API = "https://ai-journal-backend-production.up.railway.app"

async def test_hf_debug():
    """Test HuggingFace API with comprehensive debugging"""
    
    # Test entry that should definitely trigger specific sentiment analysis
    test_text = """Today was an amazing day! I finally completed the project I've been working on for weeks. The client was thrilled with the results, and my team celebrated with coffee. I feel so accomplished and proud of what we achieved together. This success makes me excited about future challenges. What is the meaning of that which came before before and how angry do I need to be? I am so angry I cannot even breathe."""
    
    print("🧪 Testing HuggingFace API with Enhanced Debugging")
    print("=" * 60)
    print(f"📝 Test Text: {test_text[:100]}...")
    print(f"📏 Text Length: {len(test_text)} characters")
    print()
    
    # Test one HuggingFace model
    model = "hf-mistral-7b"
    
    try:
        print(f"🚀 Testing {model}...")
        print(f"🔗 URL: {RAILWAY_API}/api/ai/sentiment")
        
        request_data = {
            "text": test_text,
            "task_type": "sentiment", 
            "model": model
        }
        
        print(f"📤 Request Data: {json.dumps(request_data, indent=2)}")
        print()
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{RAILWAY_API}/api/ai/sentiment",
                json=request_data,
                headers={"Content-Type": "application/json"}
            )
            
            print(f"📊 Response Status: {response.status_code}")
            print(f"🏷️ Response Headers: {dict(response.headers)}")
            print()
            
            if response.status_code == 200:
                result = response.json()
                print(f"📥 Full Response:")
                print(json.dumps(result, indent=2))
                print()
                
                # Analyze the response
                ai_response = result.get('result', '')
                confidence = result.get('confidence', 0)
                metadata = result.get('metadata', {})
                
                print(f"🔍 RESPONSE ANALYSIS:")
                print(f"   Response Length: {len(ai_response)} characters")
                print(f"   Confidence: {confidence}")
                print(f"   Metadata: {metadata}")
                print()
                
                # Check for boilerplate indicators
                boilerplate_phrases = [
                    "positive emotional tone",
                    "reflects a positive",
                    "reflects a negative", 
                    "I don't have access",
                    "I cannot analyze",
                    "Based on the general",
                    "fallback-analysis"
                ]
                
                is_boilerplate = any(phrase.lower() in ai_response.lower() for phrase in boilerplate_phrases)
                
                if is_boilerplate:
                    print(f"⚠️  BOILERPLATE DETECTED!")
                    print(f"   This is NOT a genuine HuggingFace API response")
                    print(f"   The backend is using fallback responses")
                else:
                    print(f"✅ GENUINE AI RESPONSE!")
                    print(f"   This appears to be a real HuggingFace API response")
                
                print(f"\n💬 AI Response Preview:")
                print(f"   {ai_response[:200]}...")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                error_text = response.text
                print(f"📄 Error Response: {error_text}")
                
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Check Railway logs for detailed debugging output")
    print(f"   2. Look for the 🔍 debug messages in the logs")
    print(f"   3. Verify if HuggingFace API is being called or falling back")

if __name__ == "__main__":
    asyncio.run(test_hf_debug())
