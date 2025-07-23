# Debug Script for HuggingFace API Issues
# Run this to diagnose why HF models are returning boilerplate responses

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def diagnose_hf_setup():
    """Diagnose HuggingFace API setup issues"""
    
    print("🔍 DIAGNOSING HUGGINGFACE API SETUP")
    print("=" * 50)
    
    # Check environment variables
    groq_key = os.getenv("GROQ_API_KEY")
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    
    print(f"📊 Environment Variables:")
    print(f"   GROQ_API_KEY: {'✅ Set' if groq_key else '❌ Missing'}")
    print(f"   HUGGINGFACE_API_KEY: {'✅ Set' if hf_key else '❌ Missing'}")
    
    if hf_key:
        print(f"   HF Key preview: {hf_key[:10]}...{hf_key[-4:]}")
    
    # Check if keys are valid format
    if hf_key:
        if hf_key.startswith('hf_'):
            print("   ✅ HuggingFace key format looks correct")
        else:
            print("   ⚠️  HuggingFace key should start with 'hf_'")
    
    print(f"\n🎯 ISSUE DIAGNOSIS:")
    
    if not hf_key:
        print("❌ CRITICAL: HUGGINGFACE_API_KEY environment variable is missing!")
        print("   🔧 SOLUTION: Add HUGGINGFACE_API_KEY to Railway environment")
        print("   📋 Steps:")
        print("      1. Go to Railway dashboard")
        print("      2. Select your project")
        print("      3. Go to Variables tab")
        print("      4. Add HUGGINGFACE_API_KEY with your HF token")
        print("      5. Redeploy the service")
        return False
    
    print("✅ Environment variables look good")
    print("   🔧 Next step: Test actual API calls")
    
    return True

def generate_fix_suggestions():
    """Generate specific fix suggestions based on diagnosis"""
    
    print(f"\n💡 FIXING BOILERPLATE RESPONSES:")
    print("=" * 50)
    
    print("🎯 Most likely causes:")
    print("   1. Missing HUGGINGFACE_API_KEY in Railway environment")
    print("   2. Invalid or expired HuggingFace API token")
    print("   3. HuggingFace API rate limits exceeded")
    print("   4. HuggingFace Inference API model loading issues")
    
    print(f"\n🔧 IMMEDIATE FIXES:")
    print("   1. Check Railway environment variables")
    print("   2. Verify HuggingFace token is valid")
    print("   3. Test with different HF models")
    print("   4. Add error logging to see API failures")
    
    print(f"\n📋 RAILWAY ENVIRONMENT SETUP:")
    print("   1. Go to railway.app dashboard")
    print("   2. Select 'ai-journal-backend-production' project")
    print("   3. Click 'Variables' tab")
    print("   4. Ensure these variables exist:")
    print("      - GROQ_API_KEY=gsk_...")
    print("      - HUGGINGFACE_API_KEY=hf_...")
    print("   5. Click 'Deploy' to restart with new environment")

def check_hf_token_validity():
    """Check if HuggingFace token is valid"""
    import asyncio
    import httpx
    
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if not hf_key:
        print("❌ No HuggingFace API key found")
        return False
    
    async def test_hf_api():
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://huggingface.co/api/whoami",
                    headers={"Authorization": f"Bearer {hf_key}"}
                )
                
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"✅ HuggingFace token is valid")
                    print(f"   User: {user_info.get('name', 'Unknown')}")
                    return True
                else:
                    print(f"❌ HuggingFace token validation failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ HuggingFace token test failed: {e}")
            return False
    
    return asyncio.run(test_hf_api())

if __name__ == "__main__":
    print("🧪 HuggingFace API Diagnostics")
    print("Running comprehensive diagnosis...\n")
    
    # Step 1: Check environment setup
    env_ok = diagnose_hf_setup()
    
    # Step 2: Check token validity (if available)
    if env_ok:
        print(f"\n🔑 Testing HuggingFace Token Validity...")
        token_ok = check_hf_token_validity()
        
        if not token_ok:
            print("\n❌ Token validation failed - this explains the boilerplate responses!")
    
    # Step 3: Generate fix suggestions
    generate_fix_suggestions()
    
    print(f"\n🎯 NEXT STEPS:")
    print("   1. Fix the environment variables in Railway")
    print("   2. Verify HuggingFace token is valid")
    print("   3. Test again with the browser tester")
    print("   4. Check Railway deployment logs for errors")
