#!/usr/bin/env python3
"""
Configuration Setup Wizard
Interactive setup for first-time users to configure API access or demo mode.

Design goals:
- SOLID: Single responsibility for configuration setup
- KISS: Simple, clear user interaction
- DRY: Reusable configuration validation
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import getpass
import re
from dotenv import load_dotenv


class ConfigurationWizard:
    """Interactive configuration wizard for first-time setup."""
    
    def __init__(self):
        self.config_file = Path('.env')
        self.user_config_file = Path('user_config.json')
        
        # Load existing environment variables
        if self.config_file.exists():
            load_dotenv(self.config_file)
        
        self.exchanges = {
            'bitunix': {
                'name': 'Bitunix',
                'description': 'Professional exchange with 450+ USDT pairs',
                'url': 'https://bitunix.com',
                'api_guide': 'Account → API Management → Create API Key'
            },
            'binance': {
                'name': 'Binance',
                'description': 'Global exchange with extensive pair coverage',
                'url': 'https://binance.com',
                'api_guide': 'Account → API Management → Create API Key'
            }
        }
    
    def has_existing_config(self) -> bool:
        """Check if configuration already exists."""
        return self.user_config_file.exists() or self.config_file.exists()
    
    def load_existing_config(self) -> Optional[Dict[str, Any]]:
        """Load existing user configuration."""
        if self.user_config_file.exists():
            try:
                with open(self.user_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return None
    
    def detect_existing_api_config(self) -> Optional[Dict[str, Any]]:
        """Detect existing API configuration from environment variables."""
        detected_configs = {}
        
        # Check for demo mode
        if os.getenv('TRADING_DEMO_MODE', '').lower() == 'true':
            return {'mode': 'demo', 'source': 'environment'}
        
        # Check for Bitunix configuration
        bitunix_api = os.getenv('TRADING_BITUNIX_API_KEY')
        bitunix_secret = os.getenv('TRADING_BITUNIX_SECRET_KEY')
        if bitunix_api and bitunix_secret:
            detected_configs['bitunix'] = {
                'exchange': 'bitunix',
                'api_key': bitunix_api,
                'secret_key': bitunix_secret,
                'source': 'environment'
            }
        
        # Check for Binance configuration  
        binance_api = os.getenv('TRADING_BINANCE_API_KEY')
        binance_secret = os.getenv('TRADING_BINANCE_SECRET_KEY')
        if binance_api and binance_secret:
            detected_configs['binance'] = {
                'exchange': 'binance',
                'api_key': binance_api,
                'secret_key': binance_secret,
                'source': 'environment'
            }
        
        # Check for explicit exchange type setting
        exchange_type = os.getenv('TRADING_EXCHANGE_TYPE', '').lower()
        if exchange_type in detected_configs:
            return detected_configs[exchange_type]
        
        # Return first available configuration
        if detected_configs:
            return list(detected_configs.values())[0]
        
        return None
    
    def ask_use_existing_config(self, existing_config: Dict[str, Any]) -> bool:
        """Ask user if they want to use existing API configuration."""
        print("🔍 EXISTING CONFIGURATION DETECTED!")
        print("=" * 50)
        
        if existing_config.get('mode') == 'demo':
            print("Found: 🎭 Demo Mode configuration")
            print("Source: Environment variable (TRADING_DEMO_MODE=true)")
        else:
            exchange_name = self.exchanges[existing_config['exchange']]['name']
            api_key = existing_config['api_key']
            print(f"Found: 📈 Live Data configuration")
            print(f"Exchange: {exchange_name}")
            print(f"API Key: {api_key[:8]}...{api_key[-4:]}")
            print("Secret Key: ***configured***")
            print("Source: Environment variables")
        
        print("=" * 50)
        print()
        
        while True:
            choice = input(
                "Would you like to use this existing configuration? (y/n): "
            ).strip().lower()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no")
    
    def save_user_config(self, config: Dict[str, Any]) -> None:
        """Save user configuration preferences."""
        try:
            with open(self.user_config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"⚠️  Warning: Could not save user config: {e}")
    
    def print_header(self) -> None:
        """Print welcome header."""
        print("\n" + "=" * 70)
        print("🚀 CRYPTO TRADING SCANNER - CONFIGURATION WIZARD")
        print("=" * 70)
        print("Welcome! Let's set up your trading scanner.")
        print("You can choose demo mode (no setup) or configure live data.\n")
    
    def ask_mode_preference(self) -> str:
        """Ask user to choose between demo mode or live data."""
        print("📊 CHOOSE YOUR MODE:")
        print("1. 🎭 Demo Mode (Recommended for beginners)")
        print("   • No API keys required")
        print("   • Simulated realistic data")
        print("   • Full functionality for learning")
        print("   • Start immediately")
        print()
        print("2. 📈 Live Data Mode (For experienced traders)")
        print("   • Real market data")
        print("   • Requires exchange API keys")
        print("   • Professional trading")
        print("   • Live opportunities")
        print()
        
        while True:
            choice = input("Enter your choice (1 for Demo, 2 for Live): ").strip()
            if choice == '1':
                return 'demo'
            elif choice == '2':
                return 'live'
            else:
                print("❌ Please enter 1 or 2")
    
    def ask_exchange_choice(self) -> str:
        """Ask user to choose exchange for live data."""
        print("\n📡 CHOOSE YOUR EXCHANGE:")
        
        for i, (_, exchange) in enumerate(self.exchanges.items(), 1):
            print(f"{i}. {exchange['name']}")
            print(f"   • {exchange['description']}")
            print(f"   • Sign up: {exchange['url']}")
            print()
        
        while True:
            try:
                choice = int(input(f"Enter your choice (1-{len(self.exchanges)}): ").strip())
                if 1 <= choice <= len(self.exchanges):
                    return list(self.exchanges.keys())[choice - 1]
                else:
                    print(f"❌ Please enter a number between 1 and {len(self.exchanges)}")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def collect_api_credentials(self, exchange: str) -> Tuple[str, str]:
        """Collect API credentials for chosen exchange."""
        exchange_info = self.exchanges[exchange]
        
        print(f"\n🔐 {exchange_info['name'].upper()} API SETUP:")
        print(f"To get your API keys:")
        print(f"1. Go to {exchange_info['url']}")
        print(f"2. {exchange_info['api_guide']}")
        print(f"3. Enable trading permissions")
        print(f"4. Copy your API Key and Secret Key")
        print()
        print("⚠️  SECURITY NOTES:")
        print("• Never share your API keys")
        print("• Enable IP restrictions if possible")
        print("• Use trading-only permissions")
        print("• Keys are stored locally in .env file")
        print()
        
        # API Key
        while True:
            api_key = input(f"Enter your {exchange_info['name']} API Key: ").strip()
            if api_key:
                break
            print("❌ API Key cannot be empty")
        
        # Secret Key (hidden input)
        while True:
            secret_key = getpass.getpass(f"Enter your {exchange_info['name']} Secret Key (hidden): ").strip()
            if secret_key:
                break
            print("❌ Secret Key cannot be empty")
        
        return api_key, secret_key
    
    def validate_api_credentials(self, exchange: str, api_key: str, 
                               secret_key: str) -> bool:
        """Basic validation of API credentials format."""
        # Basic length and format checks
        if len(api_key) < 10 or len(secret_key) < 10:
            print("❌ API credentials seem too short")
            return False
        
        # Check for common mistakes
        if api_key == secret_key:
            print("❌ API Key and Secret Key should be different")
            return False
        
        pattern = r'^[A-Za-z0-9]+$'
        if not re.match(pattern, api_key.replace('-', '').replace('_', '')):
            print("❌ API Key contains invalid characters")
            return False
        
        return True
    
    def create_env_file(self, config: Dict[str, Any]) -> None:
        """Create .env file with configuration."""
        # If using existing environment configuration, don't overwrite
        if config.get('source') in ['environment', 'forced_exchange']:
            print(
                f"✅ Using existing environment configuration in {self.config_file}"
            )
            return
        
        env_content = []
        
        if config['mode'] == 'demo':
            env_content.extend([
                "# Crypto Trading Scanner Configuration",
                "# Running in DEMO MODE - no API keys required",
                "",
                "# Demo mode settings",
                "TRADING_DEMO_MODE=true",
                ""
            ])
        else:
            exchange = config['exchange']
            api_key = config['api_key']
            secret_key = config['secret_key']
            
            env_content.extend([
                "# Crypto Trading Scanner Configuration",
                f"# Live data mode with {exchange.title()} exchange",
                "",
                "# Exchange configuration",
                f"TRADING_EXCHANGE_TYPE={exchange}",
                f"TRADING_{exchange.upper()}_API_KEY={api_key}",
                f"TRADING_{exchange.upper()}_SECRET_KEY={secret_key}",
                "",
                "# Trading parameters",
                "TRADING_MIN_VOLUME_USDT=1000000",
                "TRADING_MIN_PRICE=0.0001",
                "TRADING_MAX_PRICE=150000",
                "",
                "# Dashboard settings",
                "TRADING_FLASK_HOST=localhost",
                "TRADING_FLASK_PORT=5001",
                "TRADING_FLASK_DEBUG=true",
                ""
            ])
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(env_content))
            print(f"✅ Configuration saved to {self.config_file}")
        except IOError as e:
            print(f"❌ Error saving configuration: {e}")
            sys.exit(1)
    
    def confirm_configuration(self, config: Dict[str, Any]) -> bool:
        """Show configuration summary and ask for confirmation."""
        print("\n📋 CONFIGURATION SUMMARY:")
        print("-" * 40)
        
        if config['mode'] == 'demo':
            print("Mode: 🎭 Demo Mode")
            print("Data: Simulated market data")
            print("Setup: Complete - ready to start!")
        else:
            print("Mode: 📈 Live Data Mode")
            print(f"Exchange: {self.exchanges[config['exchange']]['name']}")
            print(f"API Key: {config['api_key'][:8]}...{config['api_key'][-4:]}")
            print("Secret Key: ***hidden***")
        
        print("-" * 40)
        print()
        
        while True:
            confirm = input("Is this configuration correct? (y/n): ").strip().lower()
            if confirm in ['y', 'yes']:
                return True
            elif confirm in ['n', 'no']:
                return False
            else:
                print("❌ Please enter 'y' for yes or 'n' for no")
    
    def run_wizard(self) -> Dict[str, Any]:
        """Run the complete configuration wizard."""
        self.print_header()
        
        # Check for existing user configuration first
        existing_user_config = self.load_existing_config()
        if existing_user_config:
            print("🔧 Existing user configuration found.")
            mode_name = "Demo Mode" if existing_user_config.get('mode') == 'demo' else "Live Data Mode"
            print(f"Current mode: {mode_name}")
            
            reconfigure = input(
                "\nWould you like to reconfigure? (y/n): "
            ).strip().lower()
            if reconfigure not in ['y', 'yes']:
                print("✅ Using existing user configuration")
                return existing_user_config
            print()
        
        # Check for existing API configuration in environment
        existing_api_config = self.detect_existing_api_config()
        if existing_api_config and not existing_user_config:
            if self.ask_use_existing_config(existing_api_config):
                print("✅ Using existing API configuration")
                # Save as user config for future use
                self.save_user_config(existing_api_config)
                return existing_api_config
            else:
                print(
                    "🔄 Proceeding with new configuration setup...\n"
                )
        
        while True:
            # Choose mode
            mode = self.ask_mode_preference()
            
            config = {'mode': mode}
            
            if mode == 'live':
                # Choose exchange
                exchange = self.ask_exchange_choice()
                config['exchange'] = exchange
                
                # Get API credentials
                api_key, secret_key = self.collect_api_credentials(exchange)
                
                # Validate credentials
                if not self.validate_api_credentials(exchange, api_key, secret_key):
                    retry = input("\nWould you like to try again? (y/n): ").strip().lower()
                    if retry not in ['y', 'yes']:
                        print("⚠️  Switching to demo mode")
                        config = {'mode': 'demo'}
                        break
                    continue
                
                config['api_key'] = api_key
                config['secret_key'] = secret_key
            
            # Confirm configuration
            if self.confirm_configuration(config):
                break
            else:
                print("\n🔄 Let's try again...\n")
        
        # Save configuration
        self.create_env_file(config)
        self.save_user_config(config)
        
        return config
    
    def print_next_steps(self, config: Dict[str, Any]) -> None:
        """Print next steps after configuration."""
        print("\n🎉 SETUP COMPLETE!")
        print("=" * 50)
        
        if config.get('mode') == 'demo':
            print("✅ Demo mode configured")
            print("🎭 You'll see simulated market data")
            print("📚 Perfect for learning and testing")
        else:
            exchange_name = self.exchanges[config['exchange']]['name']
            print(f"✅ Live data mode configured with {exchange_name}")
            print("📈 You'll see real market data")
            
            if config.get('source') == 'environment':
                print("🔗 Using existing environment configuration")
            else:
                print("🔐 API keys securely stored in .env file")
        
        print("\n🚀 NEXT STEPS:")
        print("1. The dashboard will start automatically")
        print("2. Open browser to: http://localhost:5001")
        print("3. Explore the features and documentation")
        
        if config.get('mode') != 'demo':
            print("\n⚠️  REMEMBER:")
            print("• Your API keys are for data access only")
            print("• Never share your API credentials")
            print(
                "• You can switch to demo mode anytime with: "
                "python flask_dashboard.py --demo"
            )
        else:
            print("\n💡 TIP:")
            print(
                "• You can enable live data later by running: "
                "python flask_dashboard.py"
            )
            print(
                "• Or force demo mode anytime with: "
                "python flask_dashboard.py --demo"
            )
        
        print("\n📚 DOCUMENTATION:")
        print("• Quick Start: QUICK_START.md")
        print("• Dashboard Guide: WEB_DASHBOARD_GUIDE.md")
        print("• Demo Scripts: DEMO_SCRIPTS_GUIDE.md")
        print("=" * 50)


def run_configuration_wizard() -> Dict[str, Any]:
    """Main entry point for configuration wizard."""
    wizard = ConfigurationWizard()
    config = wizard.run_wizard()
    wizard.print_next_steps(config)
    return config


if __name__ == "__main__":
    run_configuration_wizard()
