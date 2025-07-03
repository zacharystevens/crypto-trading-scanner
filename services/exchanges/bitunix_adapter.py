#!/usr/bin/env python3
"""
Bitunix Exchange Adapter
Implements ExchangeInterface for Bitunix API integration
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
import requests
import pandas as pd

from ..exchange_interface import ExchangeInterface, ExchangeConfig, ExchangeType, Ticker, OHLCV
# Import Bitunix API modules from local copy
from .bitunix_api.open_api_http_future_public import OpenApiHttpFuturePublic
from .bitunix_api.open_api_http_future_private import OpenApiHttpFuturePrivate
from .bitunix_api.config import Config as BitunixConfig

logger = logging.getLogger(__name__)

class BitunixAdapter(ExchangeInterface):
    """Bitunix exchange adapter implementing ExchangeInterface"""
    
    def __init__(self, config: ExchangeConfig):
        super().__init__(config)
        self._exchange_type = ExchangeType.BITUNIX
        self.public_client = None
        self.private_client = None
        self._markets_cache = None
        self._markets_cache_timestamp = None
        self._cache_duration = 300  # 5 minutes
        
    async def connect(self) -> bool:
        """Establish connection to Bitunix exchange"""
        try:
            # Create Bitunix config from our config
            bitunix_config = self._create_bitunix_config()
            
            # Initialize clients
            self.public_client = OpenApiHttpFuturePublic(bitunix_config)
            if self.config.api_key and self.config.secret_key:
                self.private_client = OpenApiHttpFuturePrivate(bitunix_config)
            
            # Test connection by fetching a ticker
            await self._test_connection()
            
            self._connected = True
            logger.info("Successfully connected to Bitunix exchange")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Bitunix: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Close connection to Bitunix exchange"""
        self.public_client = None
        self.private_client = None
        self._connected = False
        logger.info("Disconnected from Bitunix exchange")
    
    async def get_tickers(self, symbols: Optional[List[str]] = None) -> List[Ticker]:
        """Get ticker data for symbols"""
        if not self._connected or not self.public_client:
            raise ConnectionError("Not connected to Bitunix exchange")
        
        try:
            # Convert symbols format if needed (BTC/USDT -> BTCUSDT)
            bitunix_symbols = None
            if symbols:
                bitunix_symbols = ','.join([s.replace('/', '') for s in symbols])
            
            # Fetch tickers from Bitunix
            response = self.public_client.get_tickers(bitunix_symbols)
            
            # Convert to our standardized format
            tickers = []
            ticker_data = response if isinstance(response, list) else [response]
            
            for ticker in ticker_data:
                # Parse Bitunix ticker format
                open_price = float(ticker.get('open', 0))
                last_price = float(ticker.get('lastPrice', ticker.get('last', 0)))
                
                # Calculate 24h change percentage
                change_24h = 0.0
                if open_price > 0:
                    change_24h = ((last_price - open_price) / open_price) * 100
                
                tickers.append(Ticker(
                    symbol=self._format_symbol_to_standard(ticker.get('symbol', '')),
                    price=last_price,
                    change_24h=change_24h,
                    volume_24h=float(ticker.get('baseVol', ticker.get('quoteVol', 0))),
                    high_24h=float(ticker.get('high', 0)),
                    low_24h=float(ticker.get('low', 0)),
                    timestamp=int(time.time() * 1000)  # Use current time as Bitunix doesn't provide timestamp
                ))
            
            return tickers
            
        except Exception as e:
            logger.error(f"Error fetching tickers from Bitunix: {e}")
            raise
    
    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List[OHLCV]:
        """Get OHLCV data for symbol"""
        if not self._connected or not self.public_client:
            raise ConnectionError("Not connected to Bitunix exchange")
        
        try:
            # Convert symbol format (BTC/USDT -> BTCUSDT)
            bitunix_symbol = symbol.replace('/', '')
            
            # Fetch kline data from Bitunix
            response = self.public_client.get_kline(
                symbol=bitunix_symbol,
                interval=timeframe,
                limit=limit,
                type="LAST_PRICE"
            )
            
            # Convert to our standardized format
            ohlcv_data = []
            kline_data = response.get('data', []) if isinstance(response, dict) else response
            
            for kline in kline_data:
                # Handle Bitunix kline format (dict format, not array)
                if isinstance(kline, dict):
                    ohlcv_data.append(OHLCV(
                        timestamp=int(kline.get('time', 0)),
                        open=float(kline.get('open', 0)),
                        high=float(kline.get('high', 0)),
                        low=float(kline.get('low', 0)),
                        close=float(kline.get('close', 0)),
                        volume=float(kline.get('baseVol', kline.get('quoteVol', 0)))
                    ))
                else:
                    # Fallback to array format
                    ohlcv_data.append(OHLCV(
                        timestamp=int(kline[0]),  # timestamp
                        open=float(kline[1]),     # open
                        high=float(kline[2]),     # high
                        low=float(kline[3]),      # low
                        close=float(kline[4]),    # close
                        volume=float(kline[5])    # volume
                    ))
            
            return ohlcv_data
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol} from Bitunix: {e}")
            raise
    
    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get available markets/trading pairs"""
        if not self._connected or not self.public_client:
            raise ConnectionError("Not connected to Bitunix exchange")
        
        # Check cache first
        current_time = time.time()
        if (self._markets_cache and self._markets_cache_timestamp and 
            current_time - self._markets_cache_timestamp < self._cache_duration):
            return self._markets_cache
        
        try:
            # Fetch trading pairs from Bitunix
            response = self.public_client.get_trading_pairs()
            
            # Convert to standardized format
            markets = []
            pairs_data = response if isinstance(response, list) else [response]
            
            for pair in pairs_data:
                markets.append({
                    'symbol': self._format_symbol_to_standard(pair.get('symbol', '')),
                    'base': pair.get('baseCoin', ''),
                    'quote': pair.get('quoteCoin', ''),
                    'active': pair.get('status', '').upper() == 'TRADING',
                    'spot': True,  # Bitunix futures
                    'futures': True,
                    'min_amount': float(pair.get('minOrderQty', 0)),
                    'max_amount': float(pair.get('maxOrderQty', 999999999)),
                    'price_precision': int(pair.get('pricePrecision', 8)),
                    'amount_precision': int(pair.get('quantityPrecision', 8))
                })
            
            # Cache the results
            self._markets_cache = markets
            self._markets_cache_timestamp = current_time
            
            return markets
            
        except Exception as e:
            logger.error(f"Error fetching markets from Bitunix: {e}")
            raise
    
    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a symbol"""
        markets = await self.get_markets()
        
        for market in markets:
            if market['symbol'] == symbol:
                return market
        
        raise ValueError(f"Symbol {symbol} not found")
    
    def _create_bitunix_config(self) -> BitunixConfig:
        """Create Bitunix config from our ExchangeConfig"""
        # Create BitunixConfig object directly without file loading
        config = BitunixConfig.__new__(BitunixConfig)
        config.config_path = None  # No file needed
        config.config_data = {
            'credentials': {
                'api_key': self.config.api_key,
                'secret_key': self.config.secret_key
            },
            'websocket': {
                'public_uri': 'wss://fapi.bitunix.com/public/',
                'private_uri': 'wss://fapi.bitunix.com/private/',
                'reconnect_interval': 5
            },
            'http': {
                'uri_prefix': 'https://fapi.bitunix.com' if not self.config.sandbox else 'https://testnet.bitunix.com'
            }
        }
        
        return config
    
    async def _test_connection(self) -> None:
        """Test connection to exchange"""
        if not self.public_client:
            raise ConnectionError("Public client not initialized")
        
        # Test with a simple ticker request
        self.public_client.get_tickers("BTCUSDT")
    
    def _format_symbol_to_standard(self, bitunix_symbol: str) -> str:
        """Convert Bitunix symbol format to standard format (BTCUSDT -> BTC/USDT)"""
        if not bitunix_symbol:
            return bitunix_symbol
        
        # Common quote currencies
        quote_currencies = ['USDT', 'USDC', 'BTC', 'ETH', 'BNB']
        
        for quote in quote_currencies:
            if bitunix_symbol.endswith(quote):
                base = bitunix_symbol[:-len(quote)]
                return f"{base}/{quote}"
        
        # Fallback - return as is
        return bitunix_symbol
    
    def _format_symbol_to_bitunix(self, standard_symbol: str) -> str:
        """Convert standard symbol format to Bitunix format (BTC/USDT -> BTCUSDT)"""
        return standard_symbol.replace('/', '') if '/' in standard_symbol else standard_symbol 