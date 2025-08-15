# 🔧 Environment Variable Configuration Guide

Complete guide for setting up API credentials to avoid repetitive configuration and enable seamless dashboard startup.

## 📋 **Overview**

Setting up environment variables allows the dashboard to start automatically with your preferred exchange without going through the configuration wizard every time.

## 🎯 **Quick Setup (Recommended)**

### **Option 1: .env File (Persistent Configuration)**

Create a `.env` file in the project root directory:

```bash
# =============================================================================
# CRYPTO TRADING SCANNER ENVIRONMENT CONFIGURATION
# =============================================================================

# -----------------------------------------------------------------------------
# EXCHANGE SELECTION (Choose one)
# -----------------------------------------------------------------------------
# Primary exchange to use (bitunix recommended)
TRADING_EXCHANGE_TYPE=bitunix

# -----------------------------------------------------------------------------
# BITUNIX API CREDENTIALS
# -----------------------------------------------------------------------------
# Get these from: https://bitunix.com → Account → API Management
TRADING_BITUNIX_API_KEY=your_bitunix_api_key_here
TRADING_BITUNIX_SECRET_KEY=your_bitunix_secret_key_here

# -----------------------------------------------------------------------------
# BINANCE API CREDENTIALS (Alternative)
# -----------------------------------------------------------------------------
# Get these from: https://binance.com → Account → API Management
# TRADING_BINANCE_API_KEY=your_binance_api_key_here
# TRADING_BINANCE_SECRET_KEY=your_binance_secret_key_here

# -----------------------------------------------------------------------------
# TRADING PARAMETERS
# -----------------------------------------------------------------------------
TRADING_MIN_VOLUME_USDT=1000000        # Minimum 24h volume ($1M)
TRADING_MIN_PRICE=0.0001               # Minimum price filter
TRADING_MAX_PRICE=150000               # Maximum price filter

# -----------------------------------------------------------------------------
# DASHBOARD CONFIGURATION
# -----------------------------------------------------------------------------
TRADING_FLASK_HOST=localhost           # Dashboard host
TRADING_FLASK_PORT=5001                # Dashboard port
TRADING_FLASK_DEBUG=true               # Debug mode

# -----------------------------------------------------------------------------
# DEMO MODE (Alternative to live data)
# -----------------------------------------------------------------------------
# Uncomment to force demo mode (overrides API keys)
# TRADING_DEMO_MODE=true
```

### **Option 2: Shell Environment Variables (Session-based)**

For temporary setup or CI/CD environments:

```bash
# Bitunix setup
export TRADING_EXCHANGE_TYPE=bitunix
export TRADING_BITUNIX_API_KEY=your_api_key_here
export TRADING_BITUNIX_SECRET_KEY=your_secret_key_here

# OR Binance setup
export TRADING_EXCHANGE_TYPE=binance
export TRADING_BINANCE_API_KEY=your_api_key_here  
export TRADING_BINANCE_SECRET_KEY=your_secret_key_here

# Then start dashboard
python flask_dashboard.py
```

## 🚀 **Seamless Startup Methods**

### **Method 1: Automatic Detection**
```bash
# Dashboard automatically detects and uses .env file
python flask_dashboard.py
```

### **Method 2: Force Specific Exchange**
```bash
# Force Bitunix (requires TRADING_BITUNIX_* env vars)
python flask_dashboard.py --api-bitunix

# Force Binance (requires TRADING_BINANCE_* env vars)
python flask_dashboard.py --api-binance
```

### **Method 3: Demo Mode Override**
```bash
# Force demo mode (ignores API credentials)
python flask_dashboard.py --demo
```

## 🔑 **Getting API Credentials**

### **Bitunix Setup (Recommended)**

1. **Create Account**: Go to [bitunix.com](https://bitunix.com)
2. **Navigate**: Account → API Management → Create API Key
3. **Permissions**: Enable "Trading" and "Read" permissions
4. **Security**: Enable IP restrictions (optional but recommended)
5. **Save**: Copy API Key and Secret Key to `.env` file

### **Binance Setup (Alternative)**

1. **Create Account**: Go to [binance.com](https://binance.com)
2. **Navigate**: Account → API Management → Create API Key
3. **Permissions**: Enable "Spot & Margin Trading" and "Read Info"
4. **Security**: Enable IP restrictions (optional but recommended)  
5. **Save**: Copy API Key and Secret Key to `.env` file

## 🛡️ **Security Best Practices**

### **API Key Security**
- ✅ **Never share** your API keys
- ✅ **Enable IP restrictions** when possible
- ✅ **Use trading-only permissions** (no withdrawals)
- ✅ **Store in .env file** (automatically gitignored)
- ❌ **Don't commit** .env files to version control

### **Environment Variable Validation**
```bash
# Check if credentials are loaded
echo $TRADING_BITUNIX_API_KEY    # Should show your API key
echo $TRADING_BITUNIX_SECRET_KEY # Should show "SET" or similar

# Verify .env file exists and is readable
ls -la .env
cat .env | head -10
```

## 🔄 **Configuration Priorities**

The dashboard uses this priority order for configuration:

1. **Command line flags** (highest priority)
   - `--demo`, `--api-bitunix`, `--api-binance`
2. **Environment variables**
   - From `.env` file or shell exports
3. **Saved user configuration**
   - From `user_config.json` (created by wizard)
4. **Configuration wizard** (lowest priority)
   - Interactive setup for first-time users

## 🧪 **Testing Your Setup**

### **Verify Environment Variables**
```bash
# Check all trading-related environment variables
env | grep TRADING_

# Test specific exchange detection
python -c "
import os
from config.setup_wizard import ConfigurationWizard
wizard = ConfigurationWizard()
config = wizard.detect_existing_api_config()
print('Detected configuration:', config)
"
```

### **Test Dashboard Startup**
```bash
# Test automatic startup (should use your .env configuration)
python flask_dashboard.py

# Test forced exchange startup
TRADING_BITUNIX_API_KEY=test python flask_dashboard.py --api-bitunix
```

## 🐛 **Troubleshooting**

### **Common Issues**

**❌ "Missing required environment variables"**
```bash
# Check if .env file exists
ls -la .env

# Verify variable names are correct (case-sensitive)
grep TRADING_ .env

# Ensure no extra spaces around = sign
# WRONG: TRADING_BITUNIX_API_KEY = value
# RIGHT: TRADING_BITUNIX_API_KEY=value
```

**❌ "Configuration wizard keeps running"**
```bash
# Clear saved configuration to force environment detection
rm -f user_config.json

# Check if environment variables are properly set
echo $TRADING_BITUNIX_API_KEY
```

**❌ "Dashboard starts in demo mode despite API keys"**
```bash
# Check if demo mode is explicitly enabled
grep TRADING_DEMO_MODE .env

# Demo mode takes priority over API keys
# Comment out or remove: # TRADING_DEMO_MODE=true
```

### **Validation Commands**
```bash
# Test environment loading
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('Exchange type:', os.getenv('TRADING_EXCHANGE_TYPE'))
print('Bitunix API key set:', bool(os.getenv('TRADING_BITUNIX_API_KEY')))
print('Binance API key set:', bool(os.getenv('TRADING_BINANCE_API_KEY')))
"
```

## 📝 **Example Configurations**

### **Production Setup (.env)**
```bash
# Production configuration for Bitunix
TRADING_EXCHANGE_TYPE=bitunix
TRADING_BITUNIX_API_KEY=bx_live_api_key_12345
TRADING_BITUNIX_SECRET_KEY=bx_live_secret_67890
TRADING_MIN_VOLUME_USDT=5000000
TRADING_FLASK_DEBUG=false
```

### **Development Setup (.env)**
```bash
# Development configuration with debug enabled
TRADING_EXCHANGE_TYPE=bitunix
TRADING_BITUNIX_API_KEY=bx_test_api_key_12345
TRADING_BITUNIX_SECRET_KEY=bx_test_secret_67890
TRADING_MIN_VOLUME_USDT=1000000
TRADING_FLASK_DEBUG=true
```

### **Demo Setup (.env)**
```bash
# Demo mode for testing/learning
TRADING_DEMO_MODE=true
TRADING_FLASK_DEBUG=true
```

## 🎯 **Quick Commands Reference**

```bash
# Normal startup (uses .env or wizard)
python flask_dashboard.py

# Force demo mode
python flask_dashboard.py --demo

# Force specific exchange
python flask_dashboard.py --api-bitunix
python flask_dashboard.py --api-binance

# Reconfigure interactively
python flask_dashboard.py --config

# Check configuration status
python -c "from config.setup_wizard import ConfigurationWizard; print(ConfigurationWizard().detect_existing_api_config())"
```

---

## 📚 **Related Documentation**

- [Quick Start Guide](QUICK_START.md) - Basic setup instructions
- [README.md](README.md) - Main project documentation  
- [Configuration Wizard](config/setup_wizard.py) - Interactive setup tool
- [Settings](config/settings.py) - Full configuration options

This guide ensures you can set up the trading scanner once and have it start seamlessly every time without repetitive configuration steps.
