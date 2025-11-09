"""
Test script to verify Gamma API configuration
"""

import os
from main import Config

def test_gamma_config():
    """Test that gamma_api_key can be loaded from config.yaml"""
    
    print("🔍 Testing Gamma API Configuration...")
    print()
    
    # Test 1: Load from config.yaml
    print("📄 Test 1: Loading from config.yaml")
    try:
        config = Config.from_yaml('config.yaml')
        gamma_key = config.gamma_api_key
        
        if gamma_key:
            if gamma_key.startswith('sk-gamma-'):
                print(f"✅ Gamma API key found in config.yaml: {gamma_key[:15]}...")
            else:
                print(f"⚠️  Gamma API key found but format incorrect: {gamma_key[:15]}...")
                print("    Expected format: sk-gamma-xxxx")
        else:
            print("ℹ️  Gamma API key not configured in config.yaml (optional)")
    except FileNotFoundError:
        print("⚠️  config.yaml not found, using defaults")
        config = Config()
    
    print()
    
    # Test 2: Check environment variable
    print("🌍 Test 2: Checking environment variable")
    env_key = os.getenv('GAMMA_API_KEY')
    if env_key:
        if env_key.startswith('sk-gamma-'):
            print(f"✅ GAMMA_API_KEY environment variable set: {env_key[:15]}...")
        else:
            print(f"⚠️  GAMMA_API_KEY found but format incorrect")
    else:
        print("ℹ️  GAMMA_API_KEY environment variable not set (optional)")
    
    print()
    
    # Test 3: Show final priority
    print("🎯 Test 3: Final configuration priority")
    final_key = env_key or config.gamma_api_key
    
    if final_key:
        source = "environment variable" if env_key else "config.yaml"
        print(f"✅ Gamma API key will be used from: {source}")
        print(f"   Key: {final_key[:15]}...")
    else:
        print("ℹ️  Gamma API key not configured")
        print("   This is optional - system will work without presentations")
        print()
        print("📝 To enable Gamma presentations:")
        print("   Option 1: Add to config.yaml:")
        print('   gamma_api_key: "sk-gamma-xxxxxxxx"')
        print()
        print("   Option 2: Set environment variable:")
        print('   export GAMMA_API_KEY="sk-gamma-xxxxxxxx"')
        print()
        print("   Get API key: https://gamma.app/settings/api")
    
    print()
    print("=" * 60)
    print("✅ Configuration test complete!")
    
    # Summary
    print()
    print("📊 Summary:")
    print(f"  OpenAI API Key: {'✅ Configured' if config.api_key else '❌ Missing'}")
    print(f"  Tavily API Key: {'✅ Configured' if config.tavily_api_key else 'ℹ️  Optional'}")
    print(f"  Gamma API Key:  {'✅ Configured' if final_key else 'ℹ️  Optional'}")
    print(f"  Model Powerful: {config.model_powerful}")
    print(f"  Model Standard: {config.model_standard}")
    print(f"  Model Basic:    {config.model_basic}")

if __name__ == "__main__":
    test_gamma_config()

