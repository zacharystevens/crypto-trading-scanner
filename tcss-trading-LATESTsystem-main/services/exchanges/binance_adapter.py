#!/usr/bin/env python3
"""
Binance Exchange Adapter (via CCXT)
Implements ExchangeInterface for backward compatibility
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
import ccxt
import pandas as pd

from ..exchange_interface import ExchangeInterface, ExchangeConfig, ExchangeType, Ticker, OHLCV

logger = logging.getLogger(__name__)

class BinanceAdapter(ExchangeInterface):
    """Binance exchange adapter implementing ExchangeInterface via CCXT"""
    
    def __init__(self, config: ExchangeConfig):
        super().__init__(config)
        self._exchange_type = ExchangeType.BINANCE
        self.exchange = None
        
    async def connect(self) -> bool:
        """Establish connection to Binance exchange"""
        try:
            # Initialize CCXT Binance exchange
            exchange_config = {
                'apiKey': self.config.api_key,
                'secret': self.config.secret_key,
                'sandbox': self.config.sandbox,
                'enableRateLimit': self.config.enable_rate_limit,
                'timeout': self.config.timeout,
            }
            
            # Add extra parameters if provided
            if self.config.extra_params:
                exchange_config.update(self.config.extra_params)
            
            self.exchange = ccxt.binance(exchange_config)
            
            # Test connection by loading markets
            await asyncio.get_event_loop().run_in_executor(None, self.exchange.load_markets)
            
            self._connected = True
            logger.info("Successfully connected to Binance exchange via CCXT")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Binance: {e}")
            self._connected = False
            return False
    
    async def disconnect(self) -> None:
        """Close connection to Binance exchange"""
        if self.exchange:
            await asyncio.get_event_loop().run_in_executor(None, self.exchange.close)
        self.exchange = None
        self._connected = False
        logger.info("Disconnected from Binance exchange")
    
    async def get_tickers(self, symbols: Optional[List[str]] = None) -> List[Ticker]:
        """Get ticker data for symbols"""
        if not self._connected or not self.exchange:
            raise ConnectionError("Not connected to Binance exchange")
        
        try:
            # Fetch tickers from Binance via CCXT
            if symbols:
                tickers_data = {}
                for symbol in symbols:
                    ticker = await asyncio.get_event_loop().run_in_executor(
                        None, self.exchange.fetch_ticker, symbol
                    )
                    tickers_data[symbol] = ticker
            else:
                tickers_data = await asyncio.get_event_loop().run_in_executor(
                    None, self.exchange.fetch_tickers
                )
            
            # Convert to our standardized format
            tickers = []
            for symbol, ticker_data in tickers_data.items():
                tickers.append(Ticker(
                    symbol=symbol,
                    price=float(ticker_data.get('last', 0)),
                    change_24h=float(ticker_data.get('percentage', 0)),
                    volume_24h=float(ticker_data.get('quoteVolume', 0)),
                    high_24h=float(ticker_data.get('high', 0)),
                    low_24h=float(ticker_data.get('low', 0)),
                    timestamp=int(ticker_data.get('timestamp', time.time() * 1000))
                ))
            
            return tickers
            
        except Exception as e:
            logger.error(f"Error fetching tickers from Binance: {e}")
            raise
    
    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List[OHLCV]:
        """Get OHLCV data for symbol"""
        if not self._connected or not self.exchange:
            raise ConnectionError("Not connected to Binance exchange")
        
        try:
            # Fetch OHLCV data from Binance via CCXT
            ohlcv_data = await asyncio.get_event_loop().run_in_executor(
                None, self.exchange.fetch_ohlcv, symbol, timeframe, limit
            )
            
            # Convert to our standardized format
            ohlcv_list = []
            for candle in ohlcv_data:
                ohlcv_list.append(OHLCV(
                    timestamp=int(candle[0]),  # timestamp
                    open=float(candle[1]),     # open
                    high=float(candle[2]),     # high
                    low=float(candle[3]),      # low
                    close=float(candle[4]),    # close
                    volume=float(candle[5])    # volume
                ))
            
            return ohlcv_list
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol} from Binance: {e}")
            raise
    
    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get available markets/trading pairs"""
        if not self._connected or not self.exchange:
            raise ConnectionError("Not connected to Binance exchange")
        
        try:
            # Fetch markets from Binance via CCXT
            markets_data = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self.exchange.markets
            )
            
            # Convert to standardized format
            markets = []
            for symbol, market_data in markets_data.items():
                markets.append({
                    'symbol': symbol,
                    'base': market_data.get('base', ''),
                    'quote': market_data.get('quote', ''),
                    'active': market_data.get('active', False),
                    'spot': market_data.get('spot', False),
                    'futures': market_data.get('future', False),
                    'min_amount': float(market_data.get('limits', {}).get('amount', {}).get('min', 0)),
                    'max_amount': float(market_data.get('limits', {}).get('amount', {}).get('max', 999999999)),
                    'price_precision': int(market_data.get('precision', {}).get('price', 8)),
                    'amount_precision': int(market_data.get('precision', {}).get('amount', 8))
                })
            
            return markets
            
        except Exception as e:
            logger.error(f"Error fetching markets from Binance: {e}")
            raise
    
    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a symbol"""
        if not self._connected or not self.exchange:
            raise ConnectionError("Not connected to Binance exchange")
        
        try:
            if symbol not in self.exchange.markets:
                raise ValueError(f"Symbol {symbol} not found")
            
            market_data = self.exchange.markets[symbol]
            return {
                'symbol': symbol,
                'base': market_data.get('base', ''),
                'quote': market_data.get('quote', ''),
                'active': market_data.get('active', False),
                'spot': market_data.get('spot', False),
                'futures': market_data.get('future', False),
                'min_amount': float(market_data.get('limits', {}).get('amount', {}).get('min', 0)),
                'max_amount': float(market_data.get('limits', {}).get('amount', {}).get('max', 999999999)),
                'price_precision': int(market_data.get('precision', {}).get('price', 8)),
                'amount_precision': int(market_data.get('precision', {}).get('amount', 8)),
                'fees': market_data.get('fees', {}),
                'limits': market_data.get('limits', {})
            }
            
        except Exception as e:
            logger.error(f"Error fetching symbol info for {symbol} from Binance: {e}")
            raise 