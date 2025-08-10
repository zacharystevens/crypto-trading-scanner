#!/usr/bin/env python3
"""
Bitunix API Integration Demo
Demonstrates the new multi-exchange architecture with Bitunix support
"""

import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from config.settings import settings
from services.exchange_factory import ExchangeFactory, create_bitunix_exchange, create_binance_exchange
from services.exchange_interface import ExchangeConfig, ExchangeType
from services.market_data_service import MarketDataService

class BitunixDemo:
    """Demo class for Bitunix API integration"""
    
    def __init__(self):
        self.exchange = None
        self.market_service = None
        
    async def initialize(self):
        """Initialize the trading system with Bitunix"""
        print("🚀 BITUNIX TRADING SYSTEM DEMO")
        print("=" * 60)
        
        # Show current configuration
        print(f"📊 Exchange Type: {settings.exchange_type}")
        print(f"🌍 Environment: {settings.environment}")
        print(f"🔧 API Timeout: {settings.api_timeout}ms")
        print(f"⚡ Rate Limiting: {settings.enable_rate_limit}")
        print()
        
        try:
            # Create exchange using factory
            exchange_config = settings.get_exchange_config()
            print(f"🔗 Creating {exchange_config['exchange_type']} exchange connection...")
            
            self.exchange = ExchangeFactory.create_from_settings(exchange_config)
            
            # Connect to exchange
            print("📡 Connecting to exchange...")
            connected = await self.exchange.connect()
            
            if connected:
                print(f"✅ Successfully connected to {self.exchange.exchange_type.value} exchange")
            else:
                print("❌ Failed to connect to exchange")
                return False
            
            # Initialize market data service
            print("📈 Initializing market data service...")
            self.market_service = MarketDataService(config=settings)
            
            print("🎯 Demo system ready!")
            print()
            return True
            
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def demo_basic_data(self):
        """Demonstrate basic data fetching"""
        print("📊 BASIC DATA DEMO")
        print("-" * 40)
        
        try:
            # Get ticker data
            print("🎯 Fetching BTC and ETH tickers...")
            tickers = await self.exchange.get_tickers(['BTC/USDT', 'ETH/USDT'])
            
            for ticker in tickers:
                print(f"  {ticker.symbol}: ${ticker.price:,.2f} ({ticker.change_24h:+.2f}%)")
            
            print()
            
            # Get OHLCV data
            print("📈 Fetching BTC 1h OHLCV data...")
            ohlcv_data = await self.exchange.get_ohlcv('BTC/USDT', '1h', 5)
            
            print("  Latest 5 candles:")
            for i, candle in enumerate(ohlcv_data[-5:]):
                timestamp = datetime.fromtimestamp(candle.timestamp / 1000)
                print(f"    {i+1}. {timestamp.strftime('%H:%M')}: O=${candle.open:,.0f} H=${candle.high:,.0f} L=${candle.low:,.0f} C=${candle.close:,.0f}")
            
            print()
            
        except Exception as e:
            print(f"❌ Basic data demo failed: {e}")
    
    async def demo_market_overview(self):
        """Demonstrate market overview features"""
        print("🌐 MARKET OVERVIEW DEMO")
        print("-" * 40)
        
        try:
            # Get market movers
            print("🚀 Top 5 Gainers:")
            gainers = await self.market_service.fetch_market_movers('gainers', 5)
            for i, gainer in enumerate(gainers, 1):
                print(f"  {i}. {gainer['symbol']}: ${gainer['price']:.4f} ({gainer['change_24h']:+.2f}%)")
            
            print()
            
            print("📉 Top 5 Losers:")
            losers = await self.market_service.fetch_market_movers('losers', 5)
            for i, loser in enumerate(losers, 1):
                print(f"  {i}. {loser['symbol']}: ${loser['price']:.4f} ({loser['change_24h']:+.2f}%)")
            
            print()
            
            print("💎 Top 5 by Market Cap:")
            market_cap = await self.market_service.fetch_top_market_cap(5)
            for i, coin in enumerate(market_cap, 1):
                print(f"  {i}. {coin['symbol']}: ${coin['price']:.4f} ({coin['change_24h']:+.2f}%)")
            
            print()
            
        except Exception as e:
            print(f"❌ Market overview demo failed: {e}")
    
    async def demo_technical_analysis(self):
        """Demonstrate technical analysis capabilities"""
        print("📊 TECHNICAL ANALYSIS DEMO")
        print("-" * 40)
        
        try:
            # Get BTC data for analysis
            print("🔍 Analyzing BTC/USDT...")
            df = await self.market_service.fetch_ohlcv_data('BTC/USDT', '1h', 50)
            
            if df is not None:
                # Calculate basic indicators
                df['sma_20'] = df['close'].rolling(window=20).mean()
                df['ema_20'] = df['close'].ewm(span=20).mean()
                
                latest = df.iloc[-1]
                print(f"  Current Price: ${latest['close']:,.2f}")
                print(f"  20-period SMA: ${latest['sma_20']:,.2f}")
                print(f"  20-period EMA: ${latest['ema_20']:,.2f}")
                
                # Trend analysis
                if latest['close'] > latest['sma_20']:
                    trend = "🟢 BULLISH (Above SMA)"
                else:
                    trend = "🔴 BEARISH (Below SMA)"
                print(f"  Trend: {trend}")
                
                print()
            else:
                print("❌ Unable to fetch OHLCV data for analysis")
                
        except Exception as e:
            print(f"❌ Technical analysis demo failed: {e}")
    
    async def demo_multi_exchange_support(self):
        """Demonstrate multi-exchange architecture"""
        print("🔄 MULTI-EXCHANGE DEMO")
        print("-" * 40)
        
        try:
            # Show current exchange
            print(f"📊 Current exchange: {self.exchange.exchange_type.value}")
            
            # Show available exchanges
            supported = ExchangeFactory.get_supported_exchanges()
            print(f"🔧 Supported exchanges: {[ex.value for ex in supported]}")
            
            # Demonstrate switching capability (if API keys available)
            print("💡 To switch exchanges, update TRADING_EXCHANGE_TYPE in .env file")
            print("   Available options: 'bitunix' or 'binance'")
            
            print()
            
        except Exception as e:
            print(f"❌ Multi-exchange demo failed: {e}")
    
    async def demo_configuration(self):
        """Demonstrate configuration capabilities"""
        print("⚙️  CONFIGURATION DEMO")
        print("-" * 40)
        
        # Show key configuration settings
        print("📋 Current Settings:")
        print(f"  Exchange: {settings.exchange_type}")
        print(f"  Environment: {settings.environment}")
        print(f"  API Timeout: {settings.api_timeout}ms")
        print(f"  Rate Limiting: {settings.enable_rate_limit}")
        print(f"  Demo Mode: {settings.demo_mode}")
        print()
        
        print("📊 Market Filters:")
        filters = settings.get_market_filters()
        print(f"  Min Volume: ${filters['min_volume_usdt']:,}")
        print(f"  Price Range: ${filters['min_price']} - ${filters['max_price']:,}")
        print(f"  Excluded: {', '.join(filters['excluded_symbols'][:3])}...")
        print()
        
        print("🎯 Analysis Config:")
        analysis = settings.get_analysis_config()
        print(f"  FVG Threshold: {analysis['fvg_threshold']*100:.1f}%")
        print(f"  Confluence Threshold: {analysis['confluence_threshold']*100:.0f}%")
        print(f"  Timeframes: {', '.join(analysis['timeframes'])}")
        print()
    
    async def run_full_demo(self):
        """Run the complete demo"""
        print("🎯 BITUNIX TRADING SYSTEM - FULL DEMO")
        print("=" * 60)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Initialize system
        if not await self.initialize():
            return
        
        # Run all demo sections
        await self.demo_configuration()
        await self.demo_basic_data()
        await self.demo_market_overview()
        await self.demo_technical_analysis()
        await self.demo_multi_exchange_support()
        
        print("✅ DEMO COMPLETED SUCCESSFULLY")
        print("=" * 60)
        print()
        print("🚀 Next Steps:")
        print("  1. Configure your API keys in .env file")
        print("  2. Set TRADING_EXCHANGE_TYPE=bitunix")
        print("  3. Run: python flask_dashboard.py")
        print("  4. Open: http://localhost:5001")
        print()
        
        # Cleanup
        if self.exchange:
            await self.exchange.disconnect()

async def main():
    """Main demo function"""
    demo = BitunixDemo()
    await demo.run_full_demo()

if __name__ == "__main__":
    asyncio.run(main()) 