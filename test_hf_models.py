#!/usr/bin/env python3
"""
HuggingFace Model Testing Script
Test all HuggingFace models to verify they return unique, non-boilerplate responses
"""

import asyncio
import httpx
import json
from datetime import datetime

# Railway API Configuration
RAILWAY_API = "https://ai-journal-backend-production.up.railway.app"

# Test journal entries with different emotional tones
TEST_ENTRIES = [
    {
        "name": "Positive Entry",
        "text": "Today was incredible! I finally got the promotion I've been working toward for months. The interview went perfectly, and my manager said my presentation was exactly what they were looking for. I feel so proud of myself and excited about the new challenges ahead. This success makes me realize how much I've grown professionally this year."
    },
    {
        "name": "Negative Entry", 
        "text": "I'm feeling really overwhelmed and anxious today. Work has been incredibly stressful with all these deadlines, and I had an argument with my best friend over something silly. I keep replaying the conversation in my head and wondering if I said the wrong thing. Sometimes I feel like I'm not handling adult responsibilities very well."
    },
    {
        "name": "Neutral/Mixed Entry",
        "text": "Had a regular day at the office today. Attended three meetings, worked on the quarterly report, and grabbed lunch with Sarah from accounting. The weather was nice so I took a walk during my break. Nothing particularly exciting happened, but I'm grateful for the steady routine. Planning to read a book tonight and maybe call my parents this weekend."
    }
]

# HuggingFace models to test
HF_MODELS = [
    "hf-mistral-7b",
    "hf-phi3-medium", 
    "hf-gemma-7b",
    "hf-zephyr-7b"
]

# Analysis types to test
ANALYSIS_TYPES = ["sentiment", "insights", "summarize"]

async def test_single_analysis(entry_name: str, text: str, model: str, analysis_type: str):
    """Test a single model/analysis combination"""
    print(f"\n🧪 Testing {model} - {analysis_type} - {entry_name}")
    print("-" * 60)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{RAILWAY_API}/api/ai/{analysis_type}",
                json={
                    "text": text,
                    "task_type": analysis_type,
                    "model": model
                },
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Print results
                print(f"✅ Status: SUCCESS")
                print(f"🤖 Model: {result.get('metadata', {}).get('model', model)}")
                print(f"🎯 Confidence: {result.get('confidence', 'N/A')}")
                print(f"📝 Response Length: {len(result.get('result', ''))}")
                print(f"💬 Response:")
                print(f"   {result.get('result', 'No result')[:200]}...")
                
                # Check for boilerplate indicators
                boilerplate_indicators = [
                    "I don't have access",
                    "I cannot analyze", 
                    "Based on the general",
                    "This appears to be",
                    "I'm not able to",
                    "As an AI, I cannot"
                ]
                
                response_text = result.get('result', '').lower()
                is_boilerplate = any(indicator.lower() in response_text for indicator in boilerplate_indicators)
                
                if is_boilerplate:
                    print("⚠️  WARNING: Response appears to be boilerplate/fallback")
                else:
                    print("✨ Response appears to be genuine AI analysis")
                
                return {
                    "success": True,
                    "model": model,
                    "analysis_type": analysis_type,
                    "entry_name": entry_name,
                    "response_length": len(result.get('result', '')),
                    "is_boilerplate": is_boilerplate,
                    "response": result.get('result', '')[:500]  # First 500 chars
                }
                
            else:
                print(f"❌ HTTP ERROR: {response.status_code}")
                print(f"📄 Response: {response.text}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "model": model,
                    "analysis_type": analysis_type,
                    "entry_name": entry_name
                }
                
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "model": model,
            "analysis_type": analysis_type,
            "entry_name": entry_name
        }

async def test_all_models():
    """Test all HuggingFace models with different journal entries"""
    print("🚀 Starting HuggingFace Model Testing")
    print("=" * 80)
    
    results = []
    
    # Test each model with each analysis type and entry
    for entry in TEST_ENTRIES:
        for model in HF_MODELS:
            for analysis_type in ANALYSIS_TYPES:
                result = await test_single_analysis(
                    entry["name"], 
                    entry["text"], 
                    model, 
                    analysis_type
                )
                results.append(result)
                
                # Small delay to avoid rate limiting
                await asyncio.sleep(2)
    
    # Generate summary report
    print("\n" + "=" * 80)
    print("📊 SUMMARY REPORT")
    print("=" * 80)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    boilerplate_responses = [r for r in successful_tests if r.get("is_boilerplate", False)]
    genuine_responses = [r for r in successful_tests if not r.get("is_boilerplate", False)]
    
    print(f"Total Tests: {len(results)}")
    print(f"✅ Successful: {len(successful_tests)}")
    print(f"❌ Failed: {len(failed_tests)}")
    print(f"⚠️  Boilerplate Responses: {len(boilerplate_responses)}")
    print(f"✨ Genuine AI Responses: {len(genuine_responses)}")
    
    # Model performance breakdown
    print(f"\n🤖 MODEL PERFORMANCE:")
    for model in HF_MODELS:
        model_results = [r for r in results if r["model"] == model]
        model_success = [r for r in model_results if r["success"]]
        model_genuine = [r for r in model_success if not r.get("is_boilerplate", False)]
        
        success_rate = len(model_success) / len(model_results) * 100 if model_results else 0
        genuine_rate = len(model_genuine) / len(model_success) * 100 if model_success else 0
        
        print(f"  {model}: {success_rate:.1f}% success, {genuine_rate:.1f}% genuine")
    
    # Analysis type performance
    print(f"\n📊 ANALYSIS TYPE PERFORMANCE:")
    for analysis_type in ANALYSIS_TYPES:
        type_results = [r for r in results if r["analysis_type"] == analysis_type]
        type_success = [r for r in type_results if r["success"]]
        type_genuine = [r for r in type_success if not r.get("is_boilerplate", False)]
        
        success_rate = len(type_success) / len(type_results) * 100 if type_results else 0
        genuine_rate = len(type_genuine) / len(type_success) * 100 if type_success else 0
        
        print(f"  {analysis_type}: {success_rate:.1f}% success, {genuine_rate:.1f}% genuine")
    
    # Save detailed results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"hf_model_test_results_{timestamp}.json"
    
    with open(results_file, 'w') as f:
        json.dump({
            "timestamp": timestamp,
            "summary": {
                "total_tests": len(results),
                "successful": len(successful_tests),
                "failed": len(failed_tests),
                "boilerplate": len(boilerplate_responses),
                "genuine": len(genuine_responses)
            },
            "detailed_results": results
        }, f, indent=2)
    
    print(f"\n💾 Detailed results saved to: {results_file}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if len(failed_tests) > 0:
        print("❗ Some API calls failed - check API keys and network connectivity")
    
    if len(boilerplate_responses) > len(genuine_responses):
        print("⚠️  Many responses appear to be boilerplate - check HuggingFace API integration")
    
    if len(genuine_responses) > 0:
        print("✅ HuggingFace models are working and providing genuine responses!")
        best_model = max(HF_MODELS, key=lambda m: len([r for r in genuine_responses if r["model"] == m]))
        print(f"🏆 Best performing model: {best_model}")

async def test_api_health():
    """Test basic API connectivity"""
    print("🏥 Testing API Health...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{RAILWAY_API}/health")
            if response.status_code == 200:
                print("✅ API is healthy and responding")
                return True
            else:
                print(f"❌ API health check failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 HuggingFace Model Validation Test Suite")
    print("This script will test all HF models with different journal entries")
    print("to verify they're providing genuine AI responses, not boilerplate.\n")
    
    async_result = asyncio.run(test_api_health())
    if async_result:
        asyncio.run(test_all_models())
    else:
        print("❌ Cannot proceed - API is not accessible")
