#!/usr/bin/env python3
"""
CONFIRMATION CANDLE SYSTEM
Adds 5-minute candle confirmation to reduce false signals
Uses 1-2 confirmation candles to validate trend direction
"""

import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
import time
import logging

logger = logging.getLogger(__name__)

class ConfirmationCandleSystem:
    def __init__(self, exchange=None):
        self.exchange = exchange
        self.confirmation_timeframe = '5m'
        self.confirmation_candles = 1  # Number of candles to wait for confirmation
        self.min_body_ratio = 0.6  # Minimum body to wick ratio for confirmation
        self.min_volume_increase = 1.2  # Minimum volume increase for confirmation
        self.confirmation_cache = {}  # Cache confirmation data
        
        # SECOND CONFIRMATION BLOCK - More strict requirements
        self.second_confirmation_candles = 1  # Additional 1 candle for second confirmation
        self.second_min_body_ratio = 0.7  # Higher body ratio requirement
        self.second_min_volume_increase = 1.5  # Higher volume requirement
        self.second_confirmation_delay = 5  # Minutes to wait for second confirmation
        
        # THIRD CONFIRMATION BLOCK - Ultra strict requirements
        self.third_confirmation_candles = 1  # Additional 1 candle for third confirmation
        self.third_min_body_ratio = 0.8  # Very high body ratio requirement
        self.third_min_volume_increase = 2.0  # Very high volume requirement
        self.third_confirmation_delay = 10  # Minutes to wait for third confirmation
        
        # FOURTH CONFIRMATION BLOCK - Maximum strict requirements
        self.fourth_confirmation_candles = 1  # Additional 1 candle for fourth confirmation
        self.fourth_min_body_ratio = 0.9  # Maximum body ratio requirement
        self.fourth_min_volume_increase = 3.0  # Maximum volume requirement
        self.fourth_confirmation_delay = 15  # Minutes to wait for fourth confirmation
        
        # SYMBOL COOLDOWN - Prevent conflicting signals on same coin
        self.symbol_cooldown_minutes = 30  # Minimum time between signals for same symbol
        self.symbol_signal_history = {}  # Track last signal time per symbol
        
    def get_confirmation_data(self, symbol):
        """Fetch 5-minute candle data for confirmation using the async exchange API"""
        try:
            if not self.exchange:
                return None
            
            # Use the standardized async interface get_ohlcv() and run it synchronously here
            async def _fetch():
                try:
                    return await self.exchange.get_ohlcv(symbol, self.confirmation_timeframe, limit=100)
                except Exception as e:
                    raise e
            
            ohlcv_data = asyncio.run(_fetch())
            if not ohlcv_data:
                return None
            
            # Convert standardized OHLCV objects to DataFrame
            df_rows = []
            for o in ohlcv_data:
                # Support both dataclass objects and raw mappings if any adapter returns dicts
                if hasattr(o, 'timestamp'):
                    df_rows.append({
                        'timestamp': pd.to_datetime(getattr(o, 'timestamp'), unit='ms'),
                        'open': float(getattr(o, 'open')),
                        'high': float(getattr(o, 'high')),
                        'low': float(getattr(o, 'low')),
                        'close': float(getattr(o, 'close')),
                        'volume': float(getattr(o, 'volume')),
                    })
                elif isinstance(o, dict):
                    df_rows.append({
                        'timestamp': pd.to_datetime(int(o.get('timestamp', o.get('time', 0))), unit='ms'),
                        'open': float(o.get('open', 0)),
                        'high': float(o.get('high', 0)),
                        'low': float(o.get('low', 0)),
                        'close': float(o.get('close', 0)),
                        'volume': float(o.get('volume', o.get('baseVol', o.get('quoteVol', 0)))),
                    })
                elif isinstance(o, (list, tuple)) and len(o) >= 6:
                    df_rows.append({
                        'timestamp': pd.to_datetime(int(o[0]), unit='ms'),
                        'open': float(o[1]),
                        'high': float(o[2]),
                        'low': float(o[3]),
                        'close': float(o[4]),
                        'volume': float(o[5]),
                    })
            
            if not df_rows:
                return None
            
            df = pd.DataFrame(df_rows)
            
            # Calculate additional metrics
            df['body_size'] = abs(df['close'] - df['open'])
            df['upper_wick'] = df['high'] - df[['open', 'close']].max(axis=1)
            df['lower_wick'] = df[['open', 'close']].min(axis=1) - df['low']
            df['total_range'] = df['high'] - df['low']
            df['body_ratio'] = df['body_size'] / df['total_range']
            df['is_bullish'] = df['close'] > df['open']
            df['is_bearish'] = df['close'] < df['open']
            
            # Volume analysis
            df['volume_sma'] = df['volume'].rolling(window=10).mean()
            df['volume_ratio'] = df['volume'] / df['volume_sma']
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching confirmation data for {symbol}: {e}")
            return None
    
    def check_long_confirmation(self, symbol, signal_price, signal_time):
        """
        Check for bullish confirmation candles after a long signal
        Returns: (confirmed, confidence, details)
        """
        try:
            df = self.get_confirmation_data(symbol)
            if df is None or len(df) < 5:
                return False, 0, "Insufficient data"
            
            # Get the most recent candles after the signal
            signal_timestamp = pd.to_datetime(signal_time)
            recent_candles = df[df['timestamp'] > signal_timestamp].tail(self.confirmation_candles)
            
            if len(recent_candles) < self.confirmation_candles:
                return False, 0, "Waiting for confirmation candles"
            
            confirmation_score = 0
            total_score = 0
            details = []
            
            for idx, candle in recent_candles.iterrows():
                candle_score = 0
                max_score = 4  # Maximum score per candle
                
                # 1. Bullish candle (close > open)
                if candle['is_bullish']:
                    candle_score += 1
                    details.append(f"Candle {idx}: Bullish ✓")
                else:
                    details.append(f"Candle {idx}: Bearish ✗")
                
                # 2. Strong body (body ratio > threshold)
                if candle['body_ratio'] > self.min_body_ratio:
                    candle_score += 1
                    details.append(f"  Strong body ({candle['body_ratio']:.2f}) ✓")
                else:
                    details.append(f"  Weak body ({candle['body_ratio']:.2f}) ✗")
                
                # 3. Higher volume than average
                if candle['volume_ratio'] > self.min_volume_increase:
                    candle_score += 1
                    details.append(f"  High volume ({candle['volume_ratio']:.2f}x) ✓")
                else:
                    details.append(f"  Low volume ({candle['volume_ratio']:.2f}x) ✗")
                
                # 4. Price above signal price
                if candle['close'] > signal_price:
                    candle_score += 1
                    details.append(f"  Above signal price ✓")
                else:
                    details.append(f"  Below signal price ✗")
                
                confirmation_score += candle_score
                total_score += max_score
            
            # Calculate overall confidence
            confidence = (confirmation_score / total_score) * 100 if total_score > 0 else 0
            confirmed = confidence >= 60  # 60% threshold for confirmation
            
            return confirmed, confidence, "\n".join(details)
            
        except Exception as e:
            logger.error(f"Error checking long confirmation for {symbol}: {e}")
            return False, 0, f"Error: {str(e)}"
    
    def check_short_confirmation(self, symbol, signal_price, signal_time):
        """
        Check for bearish confirmation candles after a short signal
        Returns: (confirmed, confidence, details)
        """
        try:
            df = self.get_confirmation_data(symbol)
            if df is None or len(df) < 5:
                return False, 0, "Insufficient data"
            
            # Get the most recent candles after the signal
            signal_timestamp = pd.to_datetime(signal_time)
            recent_candles = df[df['timestamp'] > signal_timestamp].tail(self.confirmation_candles)
            
            if len(recent_candles) < self.confirmation_candles:
                return False, 0, "Waiting for confirmation candles"
            
            confirmation_score = 0
            total_score = 0
            details = []
            
            for idx, candle in recent_candles.iterrows():
                candle_score = 0
                max_score = 4  # Maximum score per candle
                
                # 1. Bearish candle (close < open)
                if candle['is_bearish']:
                    candle_score += 1
                    details.append(f"Candle {idx}: Bearish ✓")
                else:
                    details.append(f"Candle {idx}: Bullish ✗")
                
                # 2. Strong body (body ratio > threshold)
                if candle['body_ratio'] > self.min_body_ratio:
                    candle_score += 1
                    details.append(f"  Strong body ({candle['body_ratio']:.2f}) ✓")
                else:
                    details.append(f"  Weak body ({candle['body_ratio']:.2f}) ✗")
                
                # 3. Higher volume than average
                if candle['volume_ratio'] > self.min_volume_increase:
                    candle_score += 1
                    details.append(f"  High volume ({candle['volume_ratio']:.2f}x) ✓")
                else:
                    details.append(f"  Low volume ({candle['volume_ratio']:.2f}x) ✗")
                
                # 4. Price below signal price
                if candle['close'] < signal_price:
                    candle_score += 1
                    details.append(f"  Below signal price ✓")
                else:
                    details.append(f"  Above signal price ✗")
                
                confirmation_score += candle_score
                total_score += max_score
            
            # Calculate overall confidence
            confidence = (confirmation_score / total_score) * 100 if total_score > 0 else 0
            confirmed = confidence >= 60  # 60% threshold for confirmation
            
            return confirmed, confidence, "\n".join(details)
            
        except Exception as e:
            logger.error(f"Error checking short confirmation for {symbol}: {e}")
            return False, 0, f"Error: {str(e)}"
    
    def check_confirmation(self, symbol, direction, signal_price, signal_time):
        """
        Main confirmation check method
        Returns: (confirmed, confidence, details)
        """
        if direction.upper() == 'LONG':
            return self.check_long_confirmation(symbol, signal_price, signal_time)
        elif direction.upper() == 'SHORT':
            return self.check_short_confirmation(symbol, signal_price, signal_time)
        else:
            return False, 0, "Invalid direction"
    
    def check_second_confirmation(self, symbol, direction, signal_price, signal_time):
        """
        SECOND CONFIRMATION BLOCK - More strict validation
        Requires additional candles with higher standards
        """
        try:
            df = self.get_confirmation_data(symbol)
            if df is None or len(df) < 10:
                return False, 0, "Insufficient data for second confirmation"
            
            # Get candles after the first confirmation period
            signal_timestamp = pd.to_datetime(signal_time)
            time_threshold = signal_timestamp + timedelta(minutes=self.second_confirmation_delay)
            recent_candles = df[df['timestamp'] > time_threshold].tail(self.second_confirmation_candles)
            
            if len(recent_candles) < self.second_confirmation_candles:
                return False, 0, f"Waiting for second confirmation ({self.second_confirmation_delay}min delay)"
            
            confirmation_score = 0
            total_score = 0
            details = []
            
            for idx, candle in recent_candles.iterrows():
                candle_score = 0
                max_score = 5  # Higher max score for second confirmation
                
                # 1. Direction consistency
                if direction == 'LONG' and candle['is_bullish']:
                    candle_score += 1
                    details.append(f"Second Candle {idx}: Bullish ✓")
                elif direction == 'SHORT' and candle['is_bearish']:
                    candle_score += 1
                    details.append(f"Second Candle {idx}: Bearish ✓")
                else:
                    details.append(f"Second Candle {idx}: Wrong direction ✗")
                
                # 2. Strong body (higher requirement)
                if candle['body_ratio'] > self.second_min_body_ratio:
                    candle_score += 1
                    details.append(f"  Strong body ({candle['body_ratio']:.2f}) ✓")
                else:
                    details.append(f"  Weak body ({candle['body_ratio']:.2f}) ✗")
                
                # 3. High volume (higher requirement)
                if candle['volume_ratio'] > self.second_min_volume_increase:
                    candle_score += 1
                    details.append(f"  High volume ({candle['volume_ratio']:.2f}x) ✓")
                else:
                    details.append(f"  High volume ({candle['volume_ratio']:.2f}x) ✗")
                
                # 4. Price momentum (new requirement)
                if direction == 'LONG' and candle['close'] > signal_price:
                    candle_score += 1
                    details.append(f"  Price above signal ✓")
                elif direction == 'SHORT' and candle['close'] < signal_price:
                    candle_score += 1
                    details.append(f"  Price below signal ✓")
                else:
                    details.append(f"  Price momentum weak ✗")
                
                # 5. Minimal wicks (new requirement)
                max_wick_ratio = 0.3
                if candle['upper_wick'] / candle['total_range'] < max_wick_ratio and candle['lower_wick'] / candle['total_range'] < max_wick_ratio:
                    candle_score += 1
                    details.append(f"  Clean candle (low wicks) ✓")
                else:
                    details.append(f"  Wicky candle ✗")
                
                confirmation_score += candle_score
                total_score += max_score
            
            # Calculate confidence (need 80% for second confirmation)
            confidence = (confirmation_score / total_score) * 100 if total_score > 0 else 0
            confirmed = confidence >= 80
            
            return confirmed, confidence, " | ".join(details)
            
        except Exception as e:
            logger.error(f"Error in second confirmation for {symbol}: {e}")
            return False, 0, f"Second confirmation error: {e}"
    
    def check_third_confirmation(self, symbol, direction, signal_price, signal_time):
        """
        THIRD CONFIRMATION BLOCK - Ultra strict validation
        Requires maximum quality candles with highest standards
        """
        try:
            df = self.get_confirmation_data(symbol)
            if df is None or len(df) < 15:
                return False, 0, "Insufficient data for third confirmation"
            
            # Get candles after the second confirmation period
            signal_timestamp = pd.to_datetime(signal_time)
            time_threshold = signal_timestamp + timedelta(minutes=self.third_confirmation_delay)
            recent_candles = df[df['timestamp'] > time_threshold].tail(self.third_confirmation_candles)
            
            if len(recent_candles) < self.third_confirmation_candles:
                return False, 0, f"Waiting for third confirmation ({self.third_confirmation_delay}min delay)"
            
            confirmation_score = 0
            total_score = 0
            details = []
            
            for idx, candle in recent_candles.iterrows():
                candle_score = 0
                max_score = 6  # Highest max score for third confirmation
                
                # 1. Perfect direction consistency
                if direction == 'LONG' and candle['is_bullish']:
                    candle_score += 1
                    details.append(f"Third Candle {idx}: Bullish ✓")
                elif direction == 'SHORT' and candle['is_bearish']:
                    candle_score += 1
                    details.append(f"Third Candle {idx}: Bearish ✓")
                else:
                    details.append(f"Third Candle {idx}: Wrong direction ✗")
                
                # 2. Very strong body (highest requirement)
                if candle['body_ratio'] > self.third_min_body_ratio:
                    candle_score += 1
                    details.append(f"  Very strong body ({candle['body_ratio']:.2f}) ✓")
                else:
                    details.append(f"  Weak body ({candle['body_ratio']:.2f}) ✗")
                
                # 3. Very high volume (highest requirement)
                if candle['volume_ratio'] > self.third_min_volume_increase:
                    candle_score += 1
                    details.append(f"  Very high volume ({candle['volume_ratio']:.2f}x) ✓")
                else:
                    details.append(f"  Low volume ({candle['volume_ratio']:.2f}x) ✗")
                
                # 4. Strong price momentum
                if direction == 'LONG' and candle['close'] > signal_price * 1.01:  # 1% above signal
                    candle_score += 1
                    details.append(f"  Strong upward momentum ✓")
                elif direction == 'SHORT' and candle['close'] < signal_price * 0.99:  # 1% below signal
                    candle_score += 1
                    details.append(f"  Strong downward momentum ✓")
                else:
                    details.append(f"  Weak momentum ✗")
                
                # 5. Very clean candles (minimal wicks)
                max_wick_ratio = 0.2  # Even stricter
                if candle['upper_wick'] / candle['total_range'] < max_wick_ratio and candle['lower_wick'] / candle['total_range'] < max_wick_ratio:
                    candle_score += 1
                    details.append(f"  Very clean candle ✓")
                else:
                    details.append(f"  Wicky candle ✗")
                
                # 6. Consistent trend (new requirement)
                if idx > 0:  # Check previous candle
                    prev_candle = recent_candles.iloc[idx-1]
                    if direction == 'LONG' and candle['close'] > prev_candle['close']:
                        candle_score += 1
                        details.append(f"  Trend continuation ✓")
                    elif direction == 'SHORT' and candle['close'] < prev_candle['close']:
                        candle_score += 1
                        details.append(f"  Trend continuation ✓")
                    else:
                        details.append(f"  Trend reversal ✗")
                else:
                    candle_score += 1  # First candle gets benefit of doubt
                    details.append(f"  First candle ✓")
                
                confirmation_score += candle_score
                total_score += max_score
            
            # Calculate confidence (need 85% for third confirmation)
            confidence = (confirmation_score / total_score) * 100 if total_score > 0 else 0
            confirmed = confidence >= 85
            
            return confirmed, confidence, " | ".join(details)
            
        except Exception as e:
            logger.error(f"Error in third confirmation for {symbol}: {e}")
            return False, 0, f"Third confirmation error: {e}"
    
    def check_fourth_confirmation(self, symbol, direction, signal_price, signal_time):
        """
        FOURTH CONFIRMATION BLOCK - Maximum strict validation
        Requires perfect candles with highest standards
        """
        try:
            df = self.get_confirmation_data(symbol)
            if df is None or len(df) < 20:
                return False, 0, "Insufficient data for fourth confirmation"
            
            # Get candles after the third confirmation period
            signal_timestamp = pd.to_datetime(signal_time)
            time_threshold = signal_timestamp + timedelta(minutes=self.fourth_confirmation_delay)
            recent_candles = df[df['timestamp'] > time_threshold].tail(self.fourth_confirmation_candles)
            
            if len(recent_candles) < self.fourth_confirmation_candles:
                return False, 0, f"Waiting for fourth confirmation ({self.fourth_confirmation_delay}min delay)"
            
            confirmation_score = 0
            total_score = 0
            details = []
            
            for idx, candle in recent_candles.iterrows():
                candle_score = 0
                max_score = 7  # Highest max score for fourth confirmation
                
                # 1. Perfect direction consistency
                if direction == 'LONG' and candle['is_bullish']:
                    candle_score += 1
                    details.append(f"Fourth Candle {idx}: Bullish ✓")
                elif direction == 'SHORT' and candle['is_bearish']:
                    candle_score += 1
                    details.append(f"Fourth Candle {idx}: Bearish ✓")
                else:
                    details.append(f"Fourth Candle {idx}: Wrong direction ✗")
                
                # 2. Perfect body (highest requirement)
                if candle['body_ratio'] > self.fourth_min_body_ratio:
                    candle_score += 1
                    details.append(f"  Perfect body ({candle['body_ratio']:.2f}) ✓")
                else:
                    details.append(f"  Weak body ({candle['body_ratio']:.2f}) ✗")
                
                # 3. Perfect volume (highest requirement)
                if candle['volume_ratio'] > self.fourth_min_volume_increase:
                    candle_score += 1
                    details.append(f"  Perfect volume ({candle['volume_ratio']:.2f}x) ✓")
                else:
                    details.append(f"  Low volume ({candle['volume_ratio']:.2f}x) ✗")
                
                # 4. Strong price momentum (higher requirement)
                if direction == 'LONG' and candle['close'] > signal_price * 1.02:  # 2% above signal
                    candle_score += 1
                    details.append(f"  Strong upward momentum ✓")
                elif direction == 'SHORT' and candle['close'] < signal_price * 0.98:  # 2% below signal
                    candle_score += 1
                    details.append(f"  Strong downward momentum ✓")
                else:
                    details.append(f"  Weak momentum ✗")
                
                # 5. Perfect clean candles (minimal wicks)
                max_wick_ratio = 0.15  # Even stricter
                if candle['upper_wick'] / candle['total_range'] < max_wick_ratio and candle['lower_wick'] / candle['total_range'] < max_wick_ratio:
                    candle_score += 1
                    details.append(f"  Perfect clean candle ✓")
                else:
                    details.append(f"  Wicky candle ✗")
                
                # 6. Strong trend continuation
                if idx > 0:  # Check previous candle
                    prev_candle = recent_candles.iloc[idx-1]
                    if direction == 'LONG' and candle['close'] > prev_candle['close'] * 1.005:  # 0.5% higher
                        candle_score += 1
                        details.append(f"  Strong trend continuation ✓")
                    elif direction == 'SHORT' and candle['close'] < prev_candle['close'] * 0.995:  # 0.5% lower
                        candle_score += 1
                        details.append(f"  Strong trend continuation ✓")
                    else:
                        details.append(f"  Weak trend ✗")
                else:
                    candle_score += 1  # First candle gets benefit of doubt
                    details.append(f"  First candle ✓")
                
                # 7. No reversal signals (new requirement)
                if direction == 'LONG':
                    # Check if there are any bearish candles in recent history
                    recent_bearish = df[df['timestamp'] > signal_timestamp].tail(5)
                    bearish_count = len(recent_bearish[recent_bearish['is_bearish']])
                    if bearish_count <= 1:  # Allow max 1 bearish candle
                        candle_score += 1
                        details.append(f"  No reversal signals ✓")
                    else:
                        details.append(f"  Reversal signals detected ✗")
                elif direction == 'SHORT':
                    # Check if there are any bullish candles in recent history
                    recent_bullish = df[df['timestamp'] > signal_timestamp].tail(5)
                    bullish_count = len(recent_bullish[recent_bullish['is_bullish']])
                    if bullish_count <= 1:  # Allow max 1 bullish candle
                        candle_score += 1
                        details.append(f"  No reversal signals ✓")
                    else:
                        details.append(f"  Reversal signals detected ✗")
                
                confirmation_score += candle_score
                total_score += max_score
            
            # Calculate confidence (need 90% for fourth confirmation)
            confidence = (confirmation_score / total_score) * 100 if total_score > 0 else 0
            confirmed = confidence >= 90
            
            return confirmed, confidence, " | ".join(details)
            
        except Exception as e:
            logger.error(f"Error in fourth confirmation for {symbol}: {e}")
            return False, 0, f"Fourth confirmation error: {e}"
    
    def get_confirmation_summary(self, symbol, direction, signal_price, signal_time):
        """
        Get a summary of confirmation status with recommendations
        """
        confirmed, confidence, details = self.check_confirmation(symbol, direction, signal_price, signal_time)
        
        summary = {
            'symbol': symbol,
            'direction': direction,
            'signal_price': signal_price,
            'signal_time': signal_time,
            'confirmed': confirmed,
            'confidence': confidence,
            'details': details,
            'recommendation': self._get_recommendation(confirmed, confidence, direction)
        }
        
        return summary
    
    def _get_recommendation(self, confirmed, confidence, direction):
        """Generate trading recommendation based on confirmation"""
        if confirmed and confidence >= 80:
            return f"STRONG {direction.upper()} - High confidence confirmation ({confidence:.1f}%)"
        elif confirmed and confidence >= 60:
            return f"CONFIRMED {direction.upper()} - Moderate confidence ({confidence:.1f}%)"
        elif not confirmed and confidence >= 40:
            return f"WEAK {direction.upper()} - Low confirmation ({confidence:.1f}%)"
        else:
            return f"REJECTED {direction.upper()} - No confirmation ({confidence:.1f}%)"
    
    def update_confirmation_cache(self, symbol, direction, signal_price, signal_time):
        """Update confirmation cache for tracking"""
        cache_key = f"{symbol}_{direction}_{signal_time}"
        self.confirmation_cache[cache_key] = {
            'symbol': symbol,
            'direction': direction,
            'signal_price': signal_price,
            'signal_time': signal_time,
            'last_check': datetime.now(),
            'confirmed': False,
            'confidence': 0
        }
    
    def get_pending_confirmations(self):
        """Get list of pending confirmations that need checking"""
        pending = []
        current_time = datetime.now()
        
        for key, data in self.confirmation_cache.items():
            # Check if enough time has passed for confirmation candles
            signal_time = data['signal_time']
            if isinstance(signal_time, str):
                signal_time = pd.to_datetime(signal_time)
            
            time_since_signal = current_time - signal_time
            minutes_since_signal = time_since_signal.total_seconds() / 60
            
            # Need at least 25 minutes for all four confirmations:
            # - 5 minutes for first confirmation (1 x 5min candle)
            # - 5 minutes additional for second confirmation (1 x 5min candle)
            # - 5 minutes additional for third confirmation (1 x 5min candle)
            # - 10 minutes additional for fourth confirmation (1 x 5min candle)
            if minutes_since_signal >= 25:
                pending.append(data)
        
        return pending
    
    def check_symbol_cooldown(self, symbol):
        """
        Check if symbol is in cooldown period to prevent conflicting signals
        Returns: (in_cooldown, time_remaining_minutes)
        """
        current_time = datetime.now()
        
        if symbol in self.symbol_signal_history:
            last_signal_time = self.symbol_signal_history[symbol]
            time_since_last = current_time - last_signal_time
            minutes_since_last = time_since_last.total_seconds() / 60
            
            if minutes_since_last < self.symbol_cooldown_minutes:
                time_remaining = self.symbol_cooldown_minutes - minutes_since_last
                return True, time_remaining
        
        return False, 0
    
    def update_symbol_signal_history(self, symbol):
        """Update the last signal time for a symbol"""
        self.symbol_signal_history[symbol] = datetime.now()
