#!/usr/bin/env python3
"""
MarketDataService - Handles all market data fetching and caching operations
"""

import ccxt
import pandas as pd
import time
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MarketDataService:
    """Service responsible for fetching and caching market data from exchanges"""
    
    def __init__(self, exchange_config: Optional[Dict] = None):
        # Market filtering settings
        self.MIN_VOLUME_USDT = 1000000
        self.MIN_PRICE = 0.0001
        self.MAX_PRICE = 150000
        self.EXCLUDED_SYMBOLS = ['USDT', 'BUSD', 'USDC', 'DAI', 'TUSD']
        
        # Ticker data caching
        self.ticker_cache = {
            'data': None,
            'timestamp': None,
            'cache_duration': 60
        }
        
        # Initialize exchange
        self.exchange = None
        self._initialize_exchange(exchange_config)
    
    def _initialize_exchange(self, config: Optional[Dict] = None):
        """Initialize exchange connection"""
        try:
            exchange_config = config or {
                'sandbox': False,
                'enableRateLimit': True,
                'timeout': 10000,
            }
            
            self.exchange = ccxt.binance(exchange_config)
            self.exchange.load_markets()
            logger.info("Successfully connected to Binance exchange")
        except Exception as e:
            logger.error(f"Failed to connect to exchange: {e}")
            raise ConnectionError(f"Exchange connection failed: {e}")
    
    def _get_cached_tickers(self):
        """Get cached ticker data or fetch fresh data if cache expired"""
        current_time = time.time()
        
        # Check if cache is valid
        if (self.ticker_cache['data'] is not None and 
            self.ticker_cache['timestamp'] is not None and
            current_time - self.ticker_cache['timestamp'] < self.ticker_cache['cache_duration']):
            return self.ticker_cache['data']
        
        # Cache expired or empty, fetch fresh data
        try:
            tickers = self.exchange.fetch_tickers()
            self.ticker_cache['data'] = tickers
            self.ticker_cache['timestamp'] = current_time
            logger.debug(f"Refreshed ticker cache with {len(tickers)} symbols")
            return tickers
        except Exception as e:
            logger.error(f"Error fetching tickers: {e}")
            # Return cached data if available, even if stale
            if self.ticker_cache['data'] is not None:
                logger.warning("Using stale ticker cache due to API error")
                return self.ticker_cache['data']
            raise e

    def fetch_ohlcv_data(self, symbol: str, timeframe: str, limit: int = 100) -> Optional[pd.DataFrame]:
        """Fetch OHLCV data with error handling"""
        if not self.exchange:
            logger.error(f"No exchange connection available for {symbol}")
            return None
        
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv or len(ohlcv) < 10:
                logger.warning(f"Insufficient data returned for {symbol} {timeframe}")
                return None
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Data validation
            if df.isnull().any().any():
                logger.warning(f"NaN values detected in {symbol} data")
                df = df.fillna(method='ffill').fillna(method='bfill')
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {symbol} {timeframe}: {e}")
            return None
    
    def fetch_market_movers(self, move_type: str = 'gainers', limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch top market gainers or losers dynamically"""
        try:
            logger.info(f"Fetching top {limit} {move_type} from the market...")
            
            # Fetch all tickers (cached for efficiency)
            tickers = self._get_cached_tickers()
            
            # Filter USDT pairs with sufficient volume
            usdt_pairs = []
            for symbol, ticker in tickers.items():
                if (symbol.endswith('/USDT') and 
                    ticker.get('quoteVolume', 0) >= self.MIN_VOLUME_USDT and
                    ticker.get('last', 0) >= self.MIN_PRICE and 
                    ticker.get('last', 0) <= self.MAX_PRICE and
                    ticker.get('percentage') is not None):
                    
                    # Exclude stablecoins and problematic pairs
                    base_symbol = symbol.split('/')[0]
                    if not any(excluded in base_symbol for excluded in self.EXCLUDED_SYMBOLS):
                        usdt_pairs.append({
                            'symbol': symbol,
                            'price': ticker['last'],
                            'change_24h': ticker['percentage'],
                            'volume_24h': ticker['quoteVolume'],
                            'high_24h': ticker['high'],
                            'low_24h': ticker['low']
                        })
            
            # Sort by 24h percentage change
            if move_type == 'gainers':
                sorted_pairs = sorted(usdt_pairs, key=lambda x: x['change_24h'], reverse=True)
                logger.info(f"Found {len(sorted_pairs)} qualifying pairs. Top gainer: {sorted_pairs[0]['symbol'] if sorted_pairs else 'None'}")
            else:  # losers
                sorted_pairs = sorted(usdt_pairs, key=lambda x: x['change_24h'])
                logger.info(f"Found {len(sorted_pairs)} qualifying pairs. Top loser: {sorted_pairs[0]['symbol'] if sorted_pairs else 'None'}")
            
            # Get top performers
            top_movers = sorted_pairs[:limit]
            
            logger.debug(f"Fetched {len(top_movers)} {move_type} successfully")
            
            # Return formatted data for frontend
            return [{
                'symbol': mover['symbol'],
                'price': mover['price'],
                'change_24h': mover['change_24h'],
                'volume': mover['volume_24h'],
                'high_24h': mover['high_24h'],
                'low_24h': mover['low_24h']
            } for mover in top_movers]
            
        except Exception as e:
            logger.error(f"Error fetching market movers: {e}")
            # Return static coins as fallback
            return [{
                'symbol': symbol,
                'price': 0.0,
                'change_24h': 0.0,
                'volume': 0,
                'high_24h': 0.0,
                'low_24h': 0.0
            } for symbol in ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'][:limit]]
    
    def fetch_top_market_cap(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch top coins by actual market capitalization ranking"""
        try:
            logger.info(f"Fetching top {limit} coins by market cap...")
            
            # Actual top cryptocurrencies by market cap (as of 2024/2025)
            TOP_MARKET_CAP_SYMBOLS = [
                'BTC/USDT',   # #1 - Bitcoin
                'ETH/USDT',   # #2 - Ethereum  
                'XRP/USDT',   # #3 - XRP
                'BNB/USDT',   # #4 - Binance Coin
                'SOL/USDT',   # #5 - Solana
                'ADA/USDT',   # #6 - Cardano
                'AVAX/USDT',  # #7 - Avalanche
                'DOT/USDT',   # #8 - Polkadot
                'TRX/USDT',   # #9 - TRON
                'LINK/USDT',  # #10 - Chainlink
                'MATIC/USDT', # #11 - Polygon
                'LTC/USDT',   # #12 - Litecoin
                'UNI/USDT',   # #13 - Uniswap
                'ATOM/USDT',  # #14 - Cosmos
                'FIL/USDT'    # #15 - Filecoin
            ]
            
            # Fetch all tickers (cached for efficiency)
            tickers = self._get_cached_tickers()
            
            # Get market data for top market cap coins (in correct order)
            top_market_cap = []
            for symbol in TOP_MARKET_CAP_SYMBOLS[:limit]:
                if symbol in tickers:
                    ticker = tickers[symbol]
                    price = ticker.get('last', 0)
                    percentage = ticker.get('percentage')
                    
                    # Remove volume filter for major market cap coins
                    if (price >= self.MIN_PRICE and 
                        price <= self.MAX_PRICE and
                        percentage is not None):
                        
                        top_market_cap.append({
                            'symbol': symbol,
                            'price': ticker['last'],
                            'change_24h': ticker.get('percentage', 0),
                            'volume': ticker.get('quoteVolume', 0),
                            'high_24h': ticker.get('high', ticker['last']),
                            'low_24h': ticker.get('low', ticker['last'])
                        })
                    else:
                        logger.debug(f"Filtered out {symbol}: price validation failed")
                else:
                    logger.warning(f"Symbol {symbol} not found in tickers")
            
            logger.info(f"Successfully fetched {len(top_market_cap)} market cap coins")
            return top_market_cap
            
        except Exception as e:
            logger.error(f"Error fetching top market cap coins: {e}")
            # Return major coins as fallback - IN CORRECT MARKET CAP ORDER
            major_coins = ['BTC/USDT', 'ETH/USDT', 'XRP/USDT', 'BNB/USDT', 'SOL/USDT', 
                          'ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT']
            return [{
                'symbol': symbol,
                'price': 0.0,
                'change_24h': 0.0,
                'volume': 0,
                'high_24h': 0.0,
                'low_24h': 0.0
            } for symbol in major_coins[:limit]]
    
    def get_all_usdt_symbols(self) -> List[str]:
        """Get all available USDT trading pairs from exchange"""
        try:
            markets = self.exchange.fetch_markets()
            usdt_symbols = []
            
            for market in markets:
                if (market['quote'] == 'USDT' and 
                    market['active'] and 
                    market['spot'] and
                    market['base'] not in self.EXCLUDED_SYMBOLS):
                    usdt_symbols.append(market['symbol'])
            
            usdt_symbols.sort()
            logger.info(f"Found {len(usdt_symbols)} USDT trading pairs")
            return usdt_symbols
            
        except Exception as e:
            logger.error(f"Error fetching all symbols: {e}")
            # Fallback to major pairs if API fails
            return ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
    
    def get_curated_30_coins(self) -> Dict[str, Any]:
        """Get curated list of 30 coins: 10 gainers + 10 losers + 10 by market cap"""
        try:
            logger.info("Fetching curated 30 coin selection...")
            
            # Fetch all three categories
            gainers = self.fetch_market_movers('gainers', 10)
            losers = self.fetch_market_movers('losers', 10)
            market_cap = self.fetch_top_market_cap(10)
            
            # Extract symbols for deduplication
            gainer_symbols = {coin['symbol'] for coin in gainers}
            loser_symbols = {coin['symbol'] for coin in losers}
            market_cap_symbols = {coin['symbol'] for coin in market_cap}
            
            # If there's overlap, fill with additional coins to maintain 30 total
            all_symbols = gainer_symbols | loser_symbols | market_cap_symbols
            
            if len(all_symbols) < 30:
                # Get additional coins to reach 30
                additional_needed = 30 - len(all_symbols)
                try:
                    all_available = self.get_all_usdt_symbols()
                    remaining = [s for s in all_available if s not in all_symbols]
                    import random
                    random.shuffle(remaining)
                    additional_coins = remaining[:additional_needed]
                    
                    # Add additional coins as market data objects
                    for symbol in additional_coins:
                        market_cap.append({
                            'symbol': symbol,
                            'price': 0.0,
                            'change_24h': 0.0,
                            'volume': 0,
                            'high_24h': 0.0,
                            'low_24h': 0.0
                        })
                except:
                    pass
            
            # Combine all coins into a single list for analysis
            curated_coins = []
            for coin_list in [gainers, losers, market_cap]:
                for coin in coin_list:
                    if coin['symbol'] not in [c['symbol'] for c in curated_coins]:
                        curated_coins.append(coin)
            
            logger.info(f"Curated selection complete: {len(curated_coins)} unique coins")
            return {
                'gainers': gainers,
                'losers': losers,
                'market_cap': market_cap,
                'all_symbols': [coin['symbol'] for coin in curated_coins]
            }
            
        except Exception as e:
            logger.error(f"Error creating curated coin selection: {e}")
            # Fallback to static list
            static_coins = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 
                           'SOL/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT']
            return {
                'gainers': static_coins[:10],
                'losers': [],
                'market_cap': [],
                'all_symbols': static_coins
            }
    
    def fetch_multi_timeframe_data(self, symbol: str, timeframes: List[str]) -> Dict[str, pd.DataFrame]:
        """Fetch OHLCV data for multiple timeframes"""
        timeframe_data = {}
        
        for timeframe in timeframes:
            df = self.fetch_ohlcv_data(symbol, timeframe)
            if df is not None:
                timeframe_data[timeframe] = df
            else:
                logger.warning(f"Failed to fetch {timeframe} data for {symbol}")
        
        return timeframe_data 