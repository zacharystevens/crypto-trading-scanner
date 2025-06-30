#!/usr/bin/env python3
"""
STAGE 1: OPPORTUNITY SCANNER
Multi-coin technical analysis to find the best trading opportunities
Combines FVG, trendlines, patterns, volume analysis with professional ranking
"""

import ccxt
import numpy as np
import pandas as pd
from scipy.stats import linregress
from datetime import datetime, timedelta
import json
import os
import sys
import warnings
import logging
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpportunityScanner:
    def __init__(self):
        # Dynamic Market Coverage Settings
        self.MIN_VOLUME_USDT = 1000000  # $1M minimum 24h volume
        self.MIN_PRICE = 0.0001  # Minimum price to avoid micro-cap chaos
        self.MAX_PRICE = 100000  # Maximum price filter
        self.EXCLUDED_SYMBOLS = ['USDT', 'BUSD', 'USDC', 'DAI', 'TUSD']  # Stablecoins
        
        # Multi-Timeframe Analysis Settings - Professional Confluence System
        self.TIMEFRAMES = ['15m', '1h', '4h', '1d']  # Active analysis timeframes
        self.PRIMARY_TIMEFRAME = '1h'  # Main analysis timeframe
        self.TIMEFRAME_WEIGHTS = {  # Importance weighting for each timeframe
            '1d': 0.35,  # Daily timeframe gets highest weight for long-term trend
            '4h': 0.30,  # Higher timeframe for medium-term
            '1h': 0.25,  # Primary timeframe for short-term
            '15m': 0.10  # Lowest weight for precision/entries
        }
        
        # Advanced FVG Detection Settings (from original design)
        self.FVG_THRESHOLD = 0.005  # 0.5% minimum gap threshold
        self.FVG_PROXIMITY = 0.02   # 2% proximity for alerts
        self.FVG_VOLUME_CONFIRM = 1.5  # Volume confirmation threshold
        self.FVG_MAX_AGE = 50  # Maximum candles to track unfilled gaps
        
        # Pattern Recognition Settings
        self.PATTERN_TOLERANCE = 0.01  # 1% tolerance for pattern matching
        self.MIN_PATTERN_PERIODS = 5   # Minimum periods for pattern formation
        
        # Multi-timeframe Confluence Settings
        self.CONFLUENCE_THRESHOLD = 0.6  # 60% agreement required across timeframes
        self.MIN_TIMEFRAMES_AGREE = 2   # Minimum timeframes that must agree
        self.STRONG_CONFLUENCE_THRESHOLD = 0.8  # 80% for strong signals
        
        # Initialize exchange with comprehensive error handling
        self.exchange = None
        self._initialize_exchange()
        
        # Create output directories with error handling
        self._create_directories()
        
        print("🔍 OPPORTUNITY SCANNER INITIALIZED")
        print(f"📊 Dynamic symbol loading from exchange | Market Movers: Available")
        print(f"🎯 Looking for: FVG setups, trendline breaks, patterns, volume spikes")
        print()
    
    def _initialize_exchange(self):
        """Initialize exchange connection with comprehensive error handling"""
        try:
            self.exchange = ccxt.binance({
                'sandbox': False,
                'enableRateLimit': True,
                'timeout': 10000,
            })
            # Test connection
            self.exchange.load_markets()
            print("✅ Exchange connected: Binance")
            logger.info("Successfully connected to Binance exchange")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Failed to connect to exchange: {error_type}: {e}")
            print(f"❌ CRITICAL ERROR: Exchange connection failed: {error_type}")
            print(f"   Check your internet connection and VPN settings")
            print(f"🔴 Cannot operate without market data connection. Exiting...")
            sys.exit(1)
    
    def _create_directories(self):
        """Create necessary directories with error handling"""
        directories = ['opportunities', 'charts']
        for directory in directories:
            try:
                os.makedirs(directory, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
            except PermissionError as e:
                logger.error(f"Permission denied creating {directory}: {e}")
                print(f"❌ Permission error creating {directory}")
            except Exception as e:
                logger.error(f"Error creating {directory}: {e}")
                print(f"⚠️  Warning: Could not create {directory}")
    
    def fetch_ohlcv_data(self, symbol, timeframe, limit=100):
        """Fetch OHLCV data with comprehensive error handling"""
        if not self.exchange:
            logger.error(f"No exchange connection available for {symbol}")
            print(f"❌ No exchange connection - cannot fetch {symbol}")
            return None
        
        try:
            # Validate inputs
            if not symbol or not timeframe or limit <= 0:
                raise ValueError(f"Invalid parameters: symbol={symbol}, timeframe={timeframe}, limit={limit}")
            
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv or len(ohlcv) < 10:
                logger.warning(f"Insufficient data returned for {symbol} {timeframe}")
                return None
            
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Validate data integrity
            if df.isnull().any().any():
                logger.warning(f"NaN values detected in {symbol} data")
                df = df.fillna(method='ffill').fillna(method='bfill')
            
            # Check for reasonable price ranges
            if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
                logger.error(f"Invalid price data detected for {symbol}")
                return None
            
            return df
            
        except Exception as e:
            # Log error and return None - no fake data in production
            error_type = type(e).__name__
            logger.error(f"{error_type} fetching {symbol} {timeframe}: {e}")
            print(f"❌ API error for {symbol}: {error_type}")
            return None
    

    
    def detect_fair_value_gaps(self, df):
        """Advanced Fair Value Gap Detection - Enhanced from Original Design
        
        Features:
        - Multi-candle gap analysis
        - Volume confirmation
        - Gap age tracking
        - Proximity alerts
        - Strength scoring
        """
        try:
            if df is None or len(df) < 3:
                logger.warning("Insufficient data for advanced FVG detection")
                return []
            
            # Validate required columns
            required_columns = ['high', 'low', 'close', 'volume']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns for FVG detection: {required_columns}")
                return []
            
            fvg_zones = []
            current_price = df.iloc[-1]['close']
            
            # Advanced 3-candle FVG detection (more accurate than 2-candle)
            for i in range(2, len(df)):
                try:
                    # Get 3-candle sequence for better accuracy
                    candle1 = df.iloc[i-2]  # First candle
                    candle2 = df.iloc[i-1]  # Middle candle (gap formation)
                    candle3 = df.iloc[i]    # Third candle (confirms gap)
                    
                    # Validate all values
                    values = [candle1['high'], candle1['low'], candle2['high'], 
                             candle2['low'], candle3['high'], candle3['low'], 
                             candle2['volume']]
                    if any(pd.isna(val) or val <= 0 for val in values):
                        continue
                    
                    # Bullish FVG Detection (Enhanced)
                    # Gap between candle1 high and candle3 low
                    if candle3['low'] > candle1['high']:
                        gap_size = (candle3['low'] - candle1['high']) / candle1['high']
                        
                        if gap_size > self.FVG_THRESHOLD:
                            # Volume confirmation
                            volume_strength = candle2['volume'] / df['volume'].rolling(20).mean().iloc[i-1] if i >= 20 else 1.0
                            volume_confirmed = volume_strength > self.FVG_VOLUME_CONFIRM
                            
                            # Calculate gap age (how many candles since formation)
                            gap_age = len(df) - i
                            
                            # Check if price is approaching gap (proximity alert)
                            gap_center = (candle1['high'] + candle3['low']) / 2
                            proximity_ratio = abs(current_price - gap_center) / gap_center
                            near_gap = proximity_ratio < self.FVG_PROXIMITY
                            
                            # Enhanced strength calculation
                            strength = min(gap_size * 100, 10)
                            if volume_confirmed:
                                strength *= 1.5
                            if near_gap:
                                strength *= 1.3
                            
                            fvg_zones.append({
                                'type': 'BULLISH_FVG',
                                'gap_low': float(candle1['high']),
                                'gap_high': float(candle3['low']),
                                'gap_center': float(gap_center),
                                'gap_size': float(gap_size),
                                'strength': float(min(strength, 15)),
                                'volume_confirmed': bool(volume_confirmed),
                                'volume_strength': float(volume_strength),
                                'age': int(gap_age),
                                'near_price': bool(near_gap),
                                'proximity_ratio': float(proximity_ratio),
                                'formation_index': int(i-1),  # Start from middle candle where gap forms
                                'status': 'UNFILLED' if not self._is_gap_filled(df, i, candle1['high'], candle3['low']) else 'FILLED'
                            })
                    
                    # Bearish FVG Detection (Enhanced)
                    elif candle3['high'] < candle1['low']:
                        gap_size = (candle1['low'] - candle3['high']) / candle1['low']
                        
                        if gap_size > self.FVG_THRESHOLD:
                            # Volume confirmation
                            volume_strength = candle2['volume'] / df['volume'].rolling(20).mean().iloc[i-1] if i >= 20 else 1.0
                            volume_confirmed = volume_strength > self.FVG_VOLUME_CONFIRM
                            
                            # Calculate gap age
                            gap_age = len(df) - i
                            
                            # Check proximity
                            gap_center = (candle1['low'] + candle3['high']) / 2
                            proximity_ratio = abs(current_price - gap_center) / gap_center
                            near_gap = proximity_ratio < self.FVG_PROXIMITY
                            
                            # Enhanced strength calculation
                            strength = min(gap_size * 100, 10)
                            if volume_confirmed:
                                strength *= 1.5
                            if near_gap:
                                strength *= 1.3
                            
                            fvg_zones.append({
                                'type': 'BEARISH_FVG',
                                'gap_low': float(candle3['high']),
                                'gap_high': float(candle1['low']),
                                'gap_center': float(gap_center),
                                'gap_size': float(gap_size),
                                'strength': float(min(strength, 15)),
                                'volume_confirmed': bool(volume_confirmed),
                                'volume_strength': float(volume_strength),
                                'age': int(gap_age),
                                'near_price': bool(near_gap),
                                'proximity_ratio': float(proximity_ratio),
                                'formation_index': int(i-1),  # Start from middle candle where gap forms
                                'status': 'UNFILLED' if not self._is_gap_filled(df, i, candle3['high'], candle1['low']) else 'FILLED'
                            })
                                
                except Exception as e:
                    logger.warning(f"Error processing advanced FVG at index {i}: {e}")
                    continue
            
            # Filter out old gaps (beyond max age) and prioritize unfilled gaps
            active_fvg_zones = [gap for gap in fvg_zones if gap['age'] <= self.FVG_MAX_AGE]
            unfilled_gaps = [gap for gap in active_fvg_zones if gap['status'] == 'UNFILLED']
            
            logger.info(f"Detected {len(fvg_zones)} total FVG zones, {len(unfilled_gaps)} unfilled, {len(active_fvg_zones)} active")
            
            # Return unfilled gaps first, then filled gaps
            return unfilled_gaps + [gap for gap in active_fvg_zones if gap['status'] == 'FILLED']
            
        except Exception as e:
            logger.error(f"Error in advanced FVG detection: {e}")
            return []
    
    def _is_gap_filled(self, df, gap_index, gap_low, gap_high):
        """Check if FVG has been filled by subsequent price action"""
        try:
            # Check candles after gap formation
            for i in range(gap_index + 1, len(df)):
                candle_low = df.iloc[i]['low']
                candle_high = df.iloc[i]['high']
                
                # Gap is filled if price trades through the gap range
                if candle_low <= gap_low and candle_high >= gap_high:
                    return True
                # Partial fill check - if significant portion is filled
                gap_range = gap_high - gap_low
                overlap = min(candle_high, gap_high) - max(candle_low, gap_low)
                if overlap > gap_range * 0.7:  # 70% of gap filled
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking gap fill status: {e}")
            return False
    
    def calculate_trendlines(self, df):
        """Calculate trendlines using linear regression with comprehensive error handling"""
        try:
            if df is None or len(df) < 20:
                logger.warning(f"Insufficient data for trendline calculation: {len(df) if df is not None else 0} periods")
                return None
            
            # Validate required columns
            required_columns = ['high', 'low', 'close']
            if not all(col in df.columns for col in required_columns):
                logger.error(f"Missing required columns for trendline calculation: {required_columns}")
                return None
            
            # Use last 20 periods for trendline calculation
            recent_df = df.tail(20).copy()
            recent_df.reset_index(drop=True, inplace=True)
            
            # Validate data integrity
            if recent_df[required_columns].isnull().any().any():
                logger.warning("NaN values detected in trendline data")
                recent_df = recent_df.fillna(method='ffill').fillna(method='bfill')
            
            highs = recent_df['high'].values
            lows = recent_df['low'].values
            x = np.arange(len(recent_df))
            
            # Validate arrays
            if len(highs) != len(lows) or len(highs) != len(x):
                logger.error("Array length mismatch in trendline calculation")
                return None
            
            if np.any(np.isnan(highs)) or np.any(np.isnan(lows)):
                logger.error("NaN values in price arrays")
                return None
            
            # Calculate trendlines with error handling
            try:
                slope_high, intercept_high, r_high, p_high, se_high = linregress(x, highs)
                slope_low, intercept_low, r_low, p_low, se_low = linregress(x, lows)
                
                # Validate regression results
                if np.isnan(slope_high) or np.isnan(intercept_high) or np.isnan(slope_low) or np.isnan(intercept_low):
                    logger.warning("Invalid regression results")
                    return None
                    
            except ValueError as e:
                logger.error(f"Linear regression error: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error in linear regression: {e}")
                return None
            
            # Current price vs trendlines
            current_price = df.iloc[-1]['close']
            if pd.isna(current_price) or current_price <= 0:
                logger.error("Invalid current price for trendline analysis")
                return None
                
            current_x = len(recent_df) - 1
            
            resistance_level = slope_high * current_x + intercept_high
            support_level = slope_low * current_x + intercept_low
            
            # Validate calculated levels
            if resistance_level <= 0 or support_level <= 0:
                logger.warning("Invalid trendline levels calculated")
                return None
            
            # Detect breakouts with safe comparisons
            resistance_break = current_price > resistance_level * 1.01
            support_break = current_price < support_level * 0.99
            
            result = {
                'resistance_level': float(resistance_level),
                'support_level': float(support_level),
                'resistance_break': bool(resistance_break),
                'support_break': bool(support_break),
                'r_squared_high': float(r_high ** 2),
                'r_squared_low': float(r_low ** 2)
            }
            
            logger.debug(f"Trendlines calculated: R={resistance_level:.4f}, S={support_level:.4f}")
            return result
            
        except Exception as e:
            logger.error(f"Error in trendline calculation: {e}")
            return None
    
    def analyze_volume(self, df):
        """Analyze volume patterns with comprehensive error handling"""
        try:
            if df is None or len(df) < 20:
                logger.warning(f"Insufficient data for volume analysis: {len(df) if df is not None else 0} periods")
                return {'volume_spike': False, 'volume_ratio': 1.0}
            
            # Validate required columns
            if 'volume' not in df.columns:
                logger.error("Missing volume column for volume analysis")
                return {'volume_spike': False, 'volume_ratio': 1.0}
            
            # Validate volume data
            if df['volume'].isnull().all():
                logger.warning("All volume data is null")
                return {'volume_spike': False, 'volume_ratio': 1.0}
            
            # Clean volume data
            df_clean = df.copy()
            df_clean['volume'] = df_clean['volume'].fillna(0)
            df_clean['volume'] = df_clean['volume'].clip(lower=0)  # Ensure non-negative
            
            # Calculate rolling average with error handling
            try:
                df_clean['volume_avg'] = df_clean['volume'].rolling(window=20, min_periods=10).mean()
            except Exception as e:
                logger.error(f"Error calculating volume average: {e}")
                return {'volume_spike': False, 'volume_ratio': 1.0}
            
            current_volume = df_clean['volume'].iloc[-1]
            avg_volume = df_clean['volume_avg'].iloc[-1]
            
            # Validate values
            if pd.isna(current_volume) or pd.isna(avg_volume) or avg_volume <= 0:
                logger.warning("Invalid volume data for ratio calculation")
                return {'volume_spike': False, 'volume_ratio': 1.0}
            
            volume_ratio = current_volume / avg_volume
            
            # Sanity check on ratio (should be reasonable)
            if volume_ratio > 100 or volume_ratio < 0:
                logger.warning(f"Unrealistic volume ratio: {volume_ratio}")
                volume_ratio = min(max(volume_ratio, 0), 100)
            
            result = {
                'volume_spike': bool(volume_ratio > 2.0),
                'volume_ratio': float(volume_ratio),
                'current_volume': float(current_volume),
                'average_volume': float(avg_volume)
            }
            
            logger.debug(f"Volume analysis: ratio={volume_ratio:.2f}, spike={result['volume_spike']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in volume analysis: {e}")
            return {'volume_spike': False, 'volume_ratio': 1.0}
    
    def detect_pattern_formations(self, df):
        """Advanced Pattern Recognition - Enhanced from Original Design
        
        Detects:
        - Double/Triple Tops/Bottoms
        - Head and Shoulders
        - Flag and Pennant patterns
        - Triangle patterns
        """
        patterns = []
        
        try:
            if df is None or len(df) < 20:
                logger.warning("Insufficient data for pattern recognition")
                return patterns
            
            # Get recent data for pattern analysis
            recent_df = df.tail(50).reset_index(drop=True)
            
            # Detect Double/Triple Tops/Bottoms
            patterns.extend(self._detect_double_triple_patterns(recent_df))
            
            # Detect Head and Shoulders
            patterns.extend(self._detect_head_shoulders(recent_df))
            
            # Detect Flag/Pennant patterns
            patterns.extend(self._detect_flag_pennant(recent_df))
            
            logger.debug(f"Detected {len(patterns)} chart patterns")
            return patterns
            
        except Exception as e:
            logger.error(f"Error in pattern recognition: {e}")
            return patterns
    
    def _detect_double_triple_patterns(self, df):
        """Detect Double/Triple Top/Bottom patterns"""
        patterns = []
        
        try:
            highs = df['high'].values
            lows = df['low'].values
            closes = df['close'].values
            
            # Find significant peaks and troughs
            peaks = self._find_peaks_troughs(highs, 'peaks')
            troughs = self._find_peaks_troughs(lows, 'troughs')
            
            # Double/Triple Top Detection
            for i in range(len(peaks) - 1):
                peak1_idx, peak1_val = peaks[i]
                peak2_idx, peak2_val = peaks[i + 1]
                
                # Check if peaks are similar in height (within tolerance)
                height_diff = abs(peak1_val - peak2_val) / peak1_val
                
                if height_diff < self.PATTERN_TOLERANCE:
                    # Find the trough between peaks
                    troughs_between = [t for t in troughs if peak1_idx < t[0] < peak2_idx]
                    
                    if troughs_between:
                        trough_val = min(troughs_between, key=lambda x: x[1])[1]
                        retracement = (peak1_val - trough_val) / peak1_val
                        
                        if retracement > 0.1:  # Minimum 10% retracement
                            pattern_type = 'DOUBLE_TOP'
                            
                            # Check for triple top
                            if i < len(peaks) - 2:
                                peak3_idx, peak3_val = peaks[i + 2]
                                height_diff3 = abs(peak1_val - peak3_val) / peak1_val
                                
                                if height_diff3 < self.PATTERN_TOLERANCE:
                                    pattern_type = 'TRIPLE_TOP'
                            
                            patterns.append({
                                'type': pattern_type,
                                'direction': 'BEARISH',
                                'strength': min((1 - height_diff + retracement) * 5, 10),
                                'resistance_level': float(max(peak1_val, peak2_val)),
                                'target': float(trough_val - (peak1_val - trough_val)),
                                'invalidation': float(max(peak1_val, peak2_val) * 1.02),
                                'confidence': float(min((1 - height_diff) * 100, 95))
                            })
            
            # Double/Triple Bottom Detection
            for i in range(len(troughs) - 1):
                trough1_idx, trough1_val = troughs[i]
                trough2_idx, trough2_val = troughs[i + 1]
                
                # Check if troughs are similar in depth
                depth_diff = abs(trough1_val - trough2_val) / trough1_val
                
                if depth_diff < self.PATTERN_TOLERANCE:
                    # Find peak between troughs
                    peaks_between = [p for p in peaks if trough1_idx < p[0] < trough2_idx]
                    
                    if peaks_between:
                        peak_val = max(peaks_between, key=lambda x: x[1])[1]
                        retracement = (peak_val - trough1_val) / trough1_val
                        
                        if retracement > 0.1:  # Minimum 10% retracement
                            pattern_type = 'DOUBLE_BOTTOM'
                            
                            # Check for triple bottom
                            if i < len(troughs) - 2:
                                trough3_idx, trough3_val = troughs[i + 2]
                                depth_diff3 = abs(trough1_val - trough3_val) / trough1_val
                                
                                if depth_diff3 < self.PATTERN_TOLERANCE:
                                    pattern_type = 'TRIPLE_BOTTOM'
                            
                            patterns.append({
                                'type': pattern_type,
                                'direction': 'BULLISH',
                                'strength': min((1 - depth_diff + retracement) * 5, 10),
                                'support_level': float(min(trough1_val, trough2_val)),
                                'target': float(peak_val + (peak_val - trough1_val)),
                                'invalidation': float(min(trough1_val, trough2_val) * 0.98),
                                'confidence': float(min((1 - depth_diff) * 100, 95))
                            })
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Error detecting double/triple patterns: {e}")
            return []
    
    def _detect_head_shoulders(self, df):
        """Detect Head and Shoulders patterns"""
        patterns = []
        
        try:
            highs = df['high'].values
            lows = df['low'].values
            peaks = self._find_peaks_troughs(highs, 'peaks')
            
            # Need at least 3 peaks for head and shoulders
            if len(peaks) < 3:
                return patterns
            
            # Check each set of 3 consecutive peaks
            for i in range(len(peaks) - 2):
                left_shoulder = peaks[i]
                head = peaks[i + 1]
                right_shoulder = peaks[i + 2]
                
                # Head should be higher than both shoulders
                if (head[1] > left_shoulder[1] and head[1] > right_shoulder[1]):
                    # Shoulders should be roughly equal
                    shoulder_diff = abs(left_shoulder[1] - right_shoulder[1]) / left_shoulder[1]
                    
                    if shoulder_diff < self.PATTERN_TOLERANCE * 2:  # Allow more tolerance for shoulders
                        # Calculate neckline (support level)
                        neckline = min(left_shoulder[1], right_shoulder[1]) * 0.95
                        
                        patterns.append({
                            'type': 'HEAD_AND_SHOULDERS',
                            'direction': 'BEARISH',
                            'strength': min((1 - shoulder_diff + 0.5) * 5, 10),
                            'neckline': float(neckline),
                            'head_level': float(head[1]),
                            'target': float(neckline - (head[1] - neckline)),
                            'invalidation': float(head[1] * 1.02),
                            'confidence': float(min((1 - shoulder_diff) * 80, 90))
                        })
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Error detecting head and shoulders: {e}")
            return []
    
    def _detect_flag_pennant(self, df):
        """Detect Flag and Pennant patterns"""
        patterns = []
        
        try:
            # Look for strong directional moves followed by consolidation
            closes = df['close'].values
            volumes = df['volume'].values
            
            if len(closes) < 15:
                return patterns
            
            # Find strong moves (flagpole)
            for i in range(10, len(closes) - 5):
                # Check for strong upward move
                flagpole_start = closes[i - 10]
                flagpole_end = closes[i]
                flagpole_move = (flagpole_end - flagpole_start) / flagpole_start
                
                if abs(flagpole_move) > 0.05:  # Minimum 5% move for flagpole
                    # Check for consolidation after flagpole
                    consolidation = closes[i:i + 5]
                    consolidation_range = (max(consolidation) - min(consolidation)) / min(consolidation)
                    
                    if consolidation_range < 0.03:  # Max 3% range for consolidation
                        pattern_type = 'BULL_FLAG' if flagpole_move > 0 else 'BEAR_FLAG'
                        direction = 'BULLISH' if flagpole_move > 0 else 'BEARISH'
                        
                        patterns.append({
                            'type': pattern_type,
                            'direction': direction,
                            'strength': min(abs(flagpole_move) * 50, 10),
                            'flagpole_start': float(flagpole_start),
                            'flagpole_end': float(flagpole_end),
                            'target': float(flagpole_end + flagpole_move * flagpole_start),
                            'confidence': float(min((1 - consolidation_range) * 70, 85))
                        })
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Error detecting flag/pennant patterns: {e}")
            return []
    
    def _find_peaks_troughs(self, data, type='peaks'):
        """Find significant peaks or troughs in price data"""
        try:
            points = []
            min_distance = 3  # Minimum distance between peaks/troughs
            
            for i in range(min_distance, len(data) - min_distance):
                if type == 'peaks':
                    # Check if current point is a peak
                    is_peak = all(data[i] >= data[j] for j in range(i - min_distance, i + min_distance + 1) if j != i)
                    if is_peak and data[i] > np.mean(data) * 1.01:  # Above average + threshold
                        points.append((i, data[i]))
                else:
                    # Check if current point is a trough
                    is_trough = all(data[i] <= data[j] for j in range(i - min_distance, i + min_distance + 1) if j != i)
                    if is_trough and data[i] < np.mean(data) * 0.99:  # Below average - threshold
                        points.append((i, data[i]))
            
            return points
            
        except Exception as e:
            logger.warning(f"Error finding {type}: {e}")
            return []
    
    def fetch_multi_timeframe_data(self, symbol):
        """Fetch data across multiple timeframes for confluence analysis"""
        timeframe_data = {}
        
        try:
            for timeframe in self.TIMEFRAMES:
                # Adjust limit based on timeframe (higher timeframes need fewer periods)
                limits = {'15m': 100, '1h': 100, '4h': 60, '1d': 30}
                limit = limits.get(timeframe, 100)
                
                df = self.fetch_ohlcv_data(symbol, timeframe, limit)
                if df is not None and len(df) >= 20:
                    timeframe_data[timeframe] = df
                    logger.debug(f"Successfully fetched {timeframe} data: {len(df)} periods")
                else:
                    logger.warning(f"Insufficient {timeframe} data for {symbol}")
            
            logger.info(f"Multi-timeframe data: {list(timeframe_data.keys())} available for {symbol}")
            return timeframe_data
            
        except Exception as e:
            logger.error(f"Error fetching multi-timeframe data for {symbol}: {e}")
            return {}
    
    def fetch_market_movers(self, move_type='gainers', limit=10):
        """Fetch top market gainers or losers dynamically"""
        try:
            logger.info(f"Fetching top {limit} {move_type} from the market...")
            
            # Fetch all tickers
            tickers = self.exchange.fetch_tickers()
            
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
            
            # Log the results
            logger.info(f"Top {limit} {move_type}:")
            for i, mover in enumerate(top_movers, 1):
                logger.info(f"{i}. {mover['symbol']}: {mover['change_24h']:.2f}% (Vol: ${mover['volume_24h']:,.0f})")
            
            # Return full market data objects with proper field names for frontend
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
            print(f"⚠️  Could not fetch market movers: {e}")
            print("📋 Falling back to static coin list...")
            # Return static coins as market data objects
            return [{
                'symbol': symbol,
                'price': 0.0,
                'change_24h': 0.0,
                'volume': 0,
                'high_24h': 0.0,
                'low_24h': 0.0
            } for symbol in ['BTC/USDT', 'ETH/USDT', 'BNB/USDT'][:limit]]
    
    def get_market_mover_summary(self, symbols):
        """Get summary of market movers for display"""
        try:
            tickers = self.exchange.fetch_tickers()
            summary = []
            
            for symbol in symbols:
                if symbol in tickers:
                    ticker = tickers[symbol]
                    summary.append({
                        'symbol': symbol,
                        'price': ticker['last'],
                        'change_24h': ticker['percentage'],
                        'volume_24h': ticker['quoteVolume']
                    })
            
            return summary
        except Exception as e:
            logger.warning(f"Could not fetch mover summary: {e}")
            return []
    
    def analyze_timeframe_confluence(self, symbol, timeframe_data):
        """Analyze confluence across multiple timeframes - Professional Grade"""
        confluence_analysis = {
            'symbol': symbol,
            'timeframes_analyzed': list(timeframe_data.keys()),
            'timeframe_results': {},
            'confluence_score': 0.0,
            'agreement_count': 0,
            'strong_signals': [],
            'conflicting_signals': [],
            'dominant_direction': 'NEUTRAL'
        }
        
        try:
            bullish_weight = 0.0
            bearish_weight = 0.0
            neutral_weight = 0.0
            
            # Analyze each timeframe individually
            for timeframe, df in timeframe_data.items():
                tf_analysis = self._analyze_single_timeframe(timeframe, df)
                confluence_analysis['timeframe_results'][timeframe] = tf_analysis
                
                # Calculate weighted vote for this timeframe
                weight = self.TIMEFRAME_WEIGHTS.get(timeframe, 0.33)
                direction = tf_analysis['dominant_direction']
                strength = tf_analysis['signal_strength']
                
                if direction == 'BULLISH':
                    bullish_weight += weight * strength
                elif direction == 'BEARISH':
                    bearish_weight += weight * strength
                else:
                    neutral_weight += weight * strength
                
                logger.debug(f"{timeframe}: {direction} (strength: {strength:.2f}, weight: {weight})")
            
            # Determine overall confluence
            total_weight = bullish_weight + bearish_weight + neutral_weight
            
            if total_weight > 0:
                bull_ratio = bullish_weight / total_weight
                bear_ratio = bearish_weight / total_weight
                neutral_ratio = neutral_weight / total_weight
                
                # Determine dominant direction
                if bull_ratio > bear_ratio and bull_ratio > neutral_ratio:
                    confluence_analysis['dominant_direction'] = 'BULLISH'
                    confluence_analysis['confluence_score'] = bull_ratio
                elif bear_ratio > bull_ratio and bear_ratio > neutral_ratio:
                    confluence_analysis['dominant_direction'] = 'BEARISH'
                    confluence_analysis['confluence_score'] = bear_ratio
                else:
                    confluence_analysis['dominant_direction'] = 'NEUTRAL'
                    confluence_analysis['confluence_score'] = neutral_ratio
                
                # Count agreements (timeframes pointing same direction)
                dominant_dir = confluence_analysis['dominant_direction']
                agreement_count = sum(1 for tf_data in confluence_analysis['timeframe_results'].values() 
                                    if tf_data['dominant_direction'] == dominant_dir)
                confluence_analysis['agreement_count'] = agreement_count
                
                # Identify strong signals (high confluence)
                if confluence_analysis['confluence_score'] >= self.STRONG_CONFLUENCE_THRESHOLD:
                    confluence_analysis['strong_signals'].append({
                        'type': 'STRONG_CONFLUENCE',
                        'direction': dominant_dir,
                        'score': confluence_analysis['confluence_score'],
                        'agreeing_timeframes': agreement_count
                    })
                
                # Identify conflicts (timeframes disagreeing)
                conflicting_tfs = [tf for tf, data in confluence_analysis['timeframe_results'].items() 
                                 if data['dominant_direction'] != dominant_dir and data['signal_strength'] > 0.3]
                if conflicting_tfs:
                    confluence_analysis['conflicting_signals'] = conflicting_tfs
                
                logger.info(f"Confluence Analysis: {dominant_dir} ({confluence_analysis['confluence_score']:.2f}) - {agreement_count}/{len(timeframe_data)} agree")
            
            return confluence_analysis
            
        except Exception as e:
            logger.error(f"Error in confluence analysis for {symbol}: {e}")
            return confluence_analysis
    
    def _analyze_single_timeframe(self, timeframe, df):
        """Analyze a single timeframe for signals"""
        analysis = {
            'timeframe': timeframe,
            'dominant_direction': 'NEUTRAL',
            'signal_strength': 0.0,
            'fvg_signals': 0,
            'trend_signals': 0,
            'pattern_signals': 0,
            'volume_signals': 0,
            'total_signals': 0
        }
        
        try:
            signals_count = 0
            bullish_signals = 0
            bearish_signals = 0
            
            # FVG Analysis for this timeframe
            fvg_zones = self.detect_fair_value_gaps(df)
            strong_fvgs = [fvg for fvg in fvg_zones if fvg.get('strength', 0) > 5 and fvg.get('status') == 'UNFILLED']
            
            for fvg in strong_fvgs:
                if fvg['type'] == 'BULLISH_FVG':
                    bullish_signals += 1
                else:
                    bearish_signals += 1
                signals_count += 1
            
            analysis['fvg_signals'] = len(strong_fvgs)
            
            # Trendline Analysis for this timeframe
            trendlines = self.calculate_trendlines(df)
            if trendlines:
                if trendlines.get('resistance_break'):
                    bullish_signals += 1
                    signals_count += 1
                    analysis['trend_signals'] += 1
                elif trendlines.get('support_break'):
                    bearish_signals += 1
                    signals_count += 1
                    analysis['trend_signals'] += 1
            
            # Pattern Analysis for this timeframe
            patterns = self.detect_pattern_formations(df)
            strong_patterns = [p for p in patterns if p.get('confidence', 0) > 70]
            
            for pattern in strong_patterns:
                if pattern['direction'] == 'BULLISH':
                    bullish_signals += 1
                else:
                    bearish_signals += 1
                signals_count += 1
            
            analysis['pattern_signals'] = len(strong_patterns)
            
            # Volume Analysis for this timeframe
            volume_data = self.analyze_volume(df)
            if volume_data.get('volume_spike'):
                # Volume spike supports the current price direction
                current_price = df.iloc[-1]['close']
                previous_price = df.iloc[-5]['close'] if len(df) > 5 else current_price
                
                if current_price > previous_price:
                    bullish_signals += 1
                else:
                    bearish_signals += 1
                
                signals_count += 1
                analysis['volume_signals'] = 1
            
            # Calculate dominant direction and strength
            analysis['total_signals'] = signals_count
            
            if signals_count > 0:
                bull_ratio = bullish_signals / signals_count
                bear_ratio = bearish_signals / signals_count
                
                if bull_ratio > bear_ratio and bull_ratio > 0.5:
                    analysis['dominant_direction'] = 'BULLISH'
                    analysis['signal_strength'] = bull_ratio
                elif bear_ratio > bull_ratio and bear_ratio > 0.5:
                    analysis['dominant_direction'] = 'BEARISH'
                    analysis['signal_strength'] = bear_ratio
                else:
                    analysis['signal_strength'] = max(bull_ratio, bear_ratio) * 0.5  # Reduced for unclear signals
            
            logger.debug(f"{timeframe} analysis: {analysis['dominant_direction']} (strength: {analysis['signal_strength']:.2f}, signals: {signals_count})")
            return analysis
            
        except Exception as e:
            logger.warning(f"Error analyzing {timeframe}: {e}")
            return analysis
    
    def score_opportunity(self, analysis):
        """Enhanced multi-timeframe scoring system - Professional Grade (0-100 points)
        
        Scoring Components:
        - Enhanced FVG (0-22): Prioritizes unfilled gaps near current price
        - Patterns (0-22): High-confidence pattern formations
        - Multi-Timeframe Confluence (0-18): Cross-timeframe agreement
        - Trendlines (0-18): Breakouts and trend strength validation
        - Volume (0-12): Volume spike confirmation
        - Momentum (0-8): Short-term price momentum
        """
        score = 0
        score_breakdown = {}
        
        # Enhanced FVG Score (0-22 points)
        fvg_score = 0
        unfilled_gaps = [fvg for fvg in analysis['fvg_zones'] if fvg.get('status') == 'UNFILLED']
        near_gaps = [fvg for fvg in unfilled_gaps if fvg.get('near_price', False)]
        
        for fvg in unfilled_gaps:
            base_score = fvg['strength'] * 1.8  # Adjusted for 22-point scale
            if fvg.get('volume_confirmed', False):
                base_score *= 1.5
            if fvg.get('near_price', False):
                base_score *= 2  # Double score for gaps near current price
            fvg_score += base_score
        
        fvg_score = min(fvg_score, 22)
        score += fvg_score
        score_breakdown['fvg'] = round(fvg_score, 1)
        
        # Enhanced Trendline Score (0-18 points)
        trendline_score = 0
        if analysis['trendlines']:
            tl = analysis['trendlines']
            if tl.get('resistance_break'):
                trendline_score += 18
            elif tl.get('support_break'):
                trendline_score += 18
            else:
                # Bonus for strong trendlines even without breakout
                r_squared_avg = (tl.get('r_squared_high', 0) + tl.get('r_squared_low', 0)) / 2
                trendline_score += r_squared_avg * 9  # Adjusted for 18-point scale
        
        trendline_score = min(trendline_score, 18)
        score += trendline_score
        score_breakdown['trendlines'] = round(trendline_score, 1)
        
        # Pattern Recognition Score (0-22 points)
        pattern_score = 0
        high_confidence_patterns = [p for p in analysis['patterns'] if p.get('confidence', 0) > 70]
        
        for pattern in high_confidence_patterns:
            base_pattern_score = pattern.get('strength', 0) * 1.8  # Adjusted for 22-point scale
            confidence_multiplier = pattern.get('confidence', 50) / 100
            pattern_score += base_pattern_score * confidence_multiplier
        
        pattern_score = min(pattern_score, 22)
        score += pattern_score
        score_breakdown['patterns'] = round(pattern_score, 1)
        
        # Enhanced Volume Score (0-12 points)
        volume_score = 0
        if analysis['volume']['volume_spike']:
            volume_ratio = analysis['volume']['volume_ratio']
            volume_score = min(volume_ratio * 2.4, 12)  # Adjusted for 12-point scale
        
        score += volume_score
        score_breakdown['volume'] = round(volume_score, 1)
        
        # Price Momentum Score (0-8 points)
        momentum_score = 0
        if len(analysis.get('price_data', [])) >= 10:
            # Short-term momentum (last 5 vs previous 5)
            recent_avg = np.mean(analysis['price_data'][-5:])
            previous_avg = np.mean(analysis['price_data'][-10:-5])
            momentum = (recent_avg - previous_avg) / previous_avg
            momentum_score = min(abs(momentum) * 80, 8)  # Adjusted for 8-point scale
        
        score += momentum_score
        score_breakdown['momentum'] = round(momentum_score, 1)
        
        # Multi-Timeframe Confluence Score (0-18 points) - ENHANCED!
        confluence_score = 0
        signals_count = 0
        
        # Count active signals from single timeframe analysis
        if fvg_score > 10:
            signals_count += 1
        if trendline_score > 10:
            signals_count += 1
        if pattern_score > 10:
            signals_count += 1
        if volume_score > 5:
            signals_count += 1
        
        # Multi-timeframe confluence scoring
        if 'multi_timeframe' in analysis:
            mtf = analysis['multi_timeframe']
            confluence_strength = mtf.get('confluence_score', 0)
            agreement_count = mtf.get('agreement_count', 0)
            total_timeframes = len(mtf.get('timeframes_analyzed', []))
            
            # Base confluence score
            confluence_score = confluence_strength * 9  # Adjusted for 18-point scale
            
            # Bonus for strong agreement across timeframes
            if agreement_count >= self.MIN_TIMEFRAMES_AGREE and total_timeframes >= 2:
                agreement_ratio = agreement_count / total_timeframes
                confluence_score += agreement_ratio * 9  # Adjusted for 18-point scale
                
                # Extra bonus for all timeframes agreeing
                if agreement_count == total_timeframes and total_timeframes >= 3:
                    confluence_score += 4  # Perfect confluence bonus (adjusted)
            
            # Strong signal bonus
            if mtf.get('strong_signals'):
                confluence_score += len(mtf['strong_signals']) * 2.5  # Adjusted
            
            # Penalty for conflicting signals
            if mtf.get('conflicting_signals'):
                confluence_score -= len(mtf['conflicting_signals']) * 1.8  # Adjusted
            
            confluence_score = max(0, min(confluence_score, 18))  # Cap at 18 points
        else:
            # Fallback to single timeframe confluence (original logic)
            if signals_count >= 3:
                confluence_score = 10
            elif signals_count == 2:
                confluence_score = 5
        
        score += confluence_score
        score_breakdown['confluence'] = round(confluence_score, 1)
        
        # Store breakdown for detailed analysis
        analysis['score_breakdown'] = score_breakdown
        analysis['total_signals'] = signals_count
        
        return min(score, 100)  # Professional grade scoring with multi-timeframe confluence
    
    def analyze_single_coin(self, symbol):
        """Complete multi-timeframe analysis for a single coin - Professional Grade"""
        print(f"🔍 Analyzing {symbol} across {len(self.TIMEFRAMES)} timeframes...")
        
        # Fetch multi-timeframe data
        timeframe_data = self.fetch_multi_timeframe_data(symbol)
        
        if not timeframe_data:
            print(f"❌ No timeframe data available for {symbol} - skipping analysis")
            return None
        
        # Check if we have minimum required timeframes
        if len(timeframe_data) < self.MIN_TIMEFRAMES_AGREE:
            print(f"❌ Insufficient timeframes for {symbol} ({len(timeframe_data)}/{self.MIN_TIMEFRAMES_AGREE} required)")
            return None
        
        # Get primary timeframe data for main analysis
        primary_df = timeframe_data.get(self.PRIMARY_TIMEFRAME)
        if primary_df is None:
            # Fall back to any available timeframe
            primary_df = next(iter(timeframe_data.values()))
            fallback_tf = next(iter(timeframe_data.keys()))
            print(f"⚠️  Using {fallback_tf} as fallback timeframe for {symbol}")
        
        # Perform multi-timeframe confluence analysis
        print(f"📊 Running confluence analysis across {list(timeframe_data.keys())}...")
        multi_timeframe_analysis = self.analyze_timeframe_confluence(symbol, timeframe_data)
        
        # Perform detailed analysis on primary timeframe
        analysis = {
            'symbol': symbol,
            'current_price': primary_df['close'].iloc[-1],
            'fvg_zones': self.detect_fair_value_gaps(primary_df),
            'trendlines': self.calculate_trendlines(primary_df),
            'volume': self.analyze_volume(primary_df),
            'patterns': self.detect_pattern_formations(primary_df),
            'price_data': primary_df['close'].tolist(),
            'timestamp': datetime.now().isoformat(),
            'multi_timeframe': multi_timeframe_analysis,
            'primary_timeframe': self.PRIMARY_TIMEFRAME,
            'analyzed_timeframes': list(timeframe_data.keys())
        }
        
        # Calculate overall score with multi-timeframe confluence
        analysis['score'] = self.score_opportunity(analysis)
        
        # Add confluence quality indicators
        mtf = multi_timeframe_analysis
        analysis['confluence_quality'] = {
            'direction': mtf['dominant_direction'],
            'strength': mtf['confluence_score'],
            'agreement': f"{mtf['agreement_count']}/{len(mtf['timeframes_analyzed'])}",
            'is_strong_signal': len(mtf.get('strong_signals', [])) > 0,
            'has_conflicts': len(mtf.get('conflicting_signals', [])) > 0
        }
        
        # Professional signal classification
        if mtf['confluence_score'] >= self.STRONG_CONFLUENCE_THRESHOLD:
            analysis['signal_class'] = 'STRONG'
        elif mtf['confluence_score'] >= self.CONFLUENCE_THRESHOLD:
            analysis['signal_class'] = 'MODERATE'
        else:
            analysis['signal_class'] = 'WEAK'
        
        print(f"✅ {symbol}: {analysis['signal_class']} {mtf['dominant_direction']} signal (Score: {analysis['score']:.0f})")
        
        return analysis
    
    def get_all_usdt_symbols(self):
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
            print(f"📈 Found {len(usdt_symbols)} USDT trading pairs")
            return usdt_symbols
            
        except Exception as e:
            print(f"❌ Error fetching all symbols: {e}")
            # Fallback to major pairs if API fails
            return ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']

    def scan_all_opportunities(self, scan_type='static', limit=15):
        """Scan coins for trading opportunities with dynamic market mover support"""
        
        # Determine which coins to scan
        if scan_type == 'static':
            coins_to_scan = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 
                           'SOL/USDT', 'AVAX/USDT', 'DOT/USDT', 'MATIC/USDT', 'LINK/USDT']
            scan_description = f"Major Coins ({len(coins_to_scan)} symbols)"
        elif scan_type == 'gainers':
            coins_to_scan = self.fetch_market_movers('gainers', limit)
            scan_description = f"Top {len(coins_to_scan)} Market Gainers (24h)"
        elif scan_type == 'losers':
            coins_to_scan = self.fetch_market_movers('losers', limit)
            scan_description = f"Top {len(coins_to_scan)} Market Losers (24h)"
        elif scan_type == 'mixed':
            gainers = self.fetch_market_movers('gainers', limit//2)
            losers = self.fetch_market_movers('losers', limit//2)
            coins_to_scan = gainers + losers
            scan_description = f"Top {len(gainers)} Gainers + {len(losers)} Losers"
        elif scan_type == 'all_coins':
            # Get all available symbols and sample them intelligently
            all_symbols = self.get_all_usdt_symbols()
            # Combine market movers with random sampling for comprehensive coverage
            try:
                gainers = self.fetch_market_movers('gainers', limit//3)
                losers = self.fetch_market_movers('losers', limit//3)
                
                # Get remaining symbols excluding market movers
                mover_symbols = set([coin['symbol'] if isinstance(coin, dict) else coin for coin in gainers + losers])
                remaining_symbols = [s for s in all_symbols if s not in mover_symbols]
                
                # Sample remaining symbols (prioritize higher volume coins)
                import random
                random.shuffle(remaining_symbols)
                additional_coins = remaining_symbols[:limit - len(gainers) - len(losers)]
                
                coins_to_scan = gainers + losers + additional_coins
                scan_description = f"Comprehensive Scan: {len(gainers)} Gainers + {len(losers)} Losers + {len(additional_coins)} Others"
            except:
                # Fallback to simple random sampling
                all_symbols = self.get_all_usdt_symbols()
                import random
                random.shuffle(all_symbols)
                coins_to_scan = all_symbols[:limit]
                scan_description = f"Random Sample of {len(coins_to_scan)} Coins"
        else:
            coins_to_scan = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            scan_description = "Default Major Pairs"
        print(f"🚀 PROFESSIONAL OPPORTUNITY SCANNER - ENHANCED VERSION")
        print(f"📊 Scanning: {scan_description}")
        print(f"🎯 Advanced FVG + Pattern Recognition + Multi-Timeframe Confluence")
        print("=" * 80)
        
        # Show market mover summary if dynamic scan
        if scan_type != 'static':
            print(f"🔥 {scan_description.upper()}:")
            summary = self.get_market_mover_summary(coins_to_scan)
            for i, mover in enumerate(summary[:10], 1):  # Show top 10 in summary
                change_emoji = "🚀" if mover['change_24h'] > 0 else "📉"
                print(f"   {i:2d}. {mover['symbol']:12} {change_emoji} {mover['change_24h']:+6.2f}% (Vol: ${mover['volume_24h']:,.0f})")
            print("=" * 80)
        
        opportunities = []
        failed_count = 0
        
        for symbol in coins_to_scan:
            try:
                analysis = self.analyze_single_coin(symbol)
                if analysis:
                    opportunities.append(analysis)
                else:
                    failed_count += 1
            except Exception as e:
                print(f"❌ Error analyzing {symbol}: {e}")
                failed_count += 1
        
        # Check if all symbols failed (critical error)
        if failed_count == len(coins_to_scan):
            print(f"\n🔴 CRITICAL ERROR: All {len(coins_to_scan)} symbols failed to fetch data")
            print("   This indicates a serious connectivity or API issue")
            print("   • Check your internet connection")
            print("   • Verify VPN settings") 
            print("   • Check if Binance API is accessible from your location")
            print("\n🛑 Cannot proceed without market data. Exiting...")
            sys.exit(1)
        
        # Warn if most symbols failed
        failure_rate = failed_count / len(coins_to_scan)
        if failure_rate > 0.5:
            print(f"\n⚠️  WARNING: {failed_count}/{len(coins_to_scan)} symbols failed ({failure_rate:.1%})")
            print("   Market data may be unreliable. Consider checking connection.")
        
        # Filter out neutral opportunities (only show directional moves)
        print(f"📊 Filtering neutral opportunities...")
        pre_filter_count = len(opportunities)
        opportunities = [opp for opp in opportunities 
                        if opp.get('confluence_quality', {}).get('direction', 'NEUTRAL') in ['BULLISH', 'BEARISH']]
        filtered_count = pre_filter_count - len(opportunities)
        
        if filtered_count > 0:
            print(f"🔄 Filtered out {filtered_count} neutral opportunities (no clear direction)")
        
        # Sort by score (highest first)
        opportunities.sort(key=lambda x: x['score'], reverse=True)
        
        # Add scan metadata
        for opp in opportunities:
            opp['scan_metadata'] = {
                'scan_type': scan_type,
                'scan_description': scan_description,
                'coins_scanned': len(coins_to_scan),
                'opportunities_found': len(opportunities)
            }
        
        return opportunities
    
    def display_top_opportunities(self, opportunities, top_n=10):
        """Enhanced display with advanced FVG and pattern information"""
        print(f"\n🔥 TOP {min(top_n, len(opportunities))} OPPORTUNITIES:")
        print("="*90)
        
        for i, opp in enumerate(opportunities[:top_n], 1):
            signal_class = opp.get('signal_class', 'UNKNOWN')
            class_emoji = {'STRONG': '🔥', 'MODERATE': '⚡', 'WEAK': '💤', 'UNKNOWN': '❓'}
            
            print(f"\n#{i}. {opp['symbol']} - Score: {opp['score']:.0f}/100 {class_emoji.get(signal_class, '❓')} {signal_class}")
            print(f"    💰 Current Price: ${opp['current_price']:.4f}")
            
            # Multi-Timeframe Confluence Summary
            if 'confluence_quality' in opp:
                cq = opp['confluence_quality']
                direction_emoji = '📈' if cq['direction'] == 'BULLISH' else '📉' if cq['direction'] == 'BEARISH' else '➡️'
                conflict_indicator = ' ⚠️ CONFLICTS' if cq['has_conflicts'] else ''
                strong_indicator = ' 🎯 STRONG' if cq['is_strong_signal'] else ''
                
                print(f"    🎯 Confluence: {direction_emoji} {cq['direction']} ({cq['strength']:.1%}) - {cq['agreement']} timeframes agree{strong_indicator}{conflict_indicator}")
                
                # Show individual timeframe breakdown
                if 'multi_timeframe' in opp and 'timeframe_results' in opp['multi_timeframe']:
                    tf_results = opp['multi_timeframe']['timeframe_results']
                    tf_summary = []
                    for tf, data in tf_results.items():
                        direction = data['dominant_direction']
                        strength = data['signal_strength']
                        emoji = '📈' if direction == 'BULLISH' else '📉' if direction == 'BEARISH' else '➡️'
                        tf_summary.append(f"{tf}:{emoji}{strength:.1f}")
                    
                    if tf_summary:
                        print(f"    📊 Timeframes: {' | '.join(tf_summary)}")
            
            # Score Breakdown
            if 'score_breakdown' in opp:
                breakdown = opp['score_breakdown']
                score_parts = []
                if breakdown.get('fvg', 0) > 0:
                    score_parts.append(f"FVG:{breakdown['fvg']}")
                if breakdown.get('patterns', 0) > 0:
                    score_parts.append(f"Patterns:{breakdown['patterns']}")
                if breakdown.get('trendlines', 0) > 0:
                    score_parts.append(f"Trends:{breakdown['trendlines']}")
                if breakdown.get('volume', 0) > 0:
                    score_parts.append(f"Vol:{breakdown['volume']}")
                if breakdown.get('confluence', 0) > 0:
                    score_parts.append(f"MTF-Confluence:{breakdown['confluence']}")
                
                if score_parts:
                    print(f"    💯 Score Sources: {' | '.join(score_parts)}")
            
            # Enhanced FVG Summary
            if opp['fvg_zones']:
                unfilled_gaps = [fvg for fvg in opp['fvg_zones'] if fvg.get('status') == 'UNFILLED']
                near_gaps = [fvg for fvg in unfilled_gaps if fvg.get('near_price', False)]
                
                fvg_summary = f"{len(opp['fvg_zones'])} total FVG zones"
                if unfilled_gaps:
                    fvg_summary += f", {len(unfilled_gaps)} unfilled"
                if near_gaps:
                    fvg_summary += f", {len(near_gaps)} NEAR PRICE ⚡"
                
                print(f"    🎯 FVG: {fvg_summary}")
                
                # Show most significant FVG
                if unfilled_gaps:
                    strongest_fvg = max(unfilled_gaps, key=lambda x: x['strength'])
                    gap_type = "📈 BULLISH" if strongest_fvg['type'] == 'BULLISH_FVG' else "📉 BEARISH"
                    volume_conf = "✅ Vol-Confirmed" if strongest_fvg.get('volume_confirmed') else ""
                    print(f"         Best Gap: {gap_type} ${strongest_fvg['gap_low']:.4f}-${strongest_fvg['gap_high']:.4f} ({strongest_fvg['gap_size']:.1%}) {volume_conf}")
            
            # Pattern Recognition Summary
            if opp['patterns']:
                high_conf_patterns = [p for p in opp['patterns'] if p.get('confidence', 0) > 70]
                if high_conf_patterns:
                    pattern_names = [p['type'].replace('_', ' ') for p in high_conf_patterns]
                    print(f"    🔍 Patterns: {', '.join(pattern_names)}")
                    
                    # Show best pattern details
                    best_pattern = max(high_conf_patterns, key=lambda x: x.get('confidence', 0))
                    direction = "📈 BULLISH" if best_pattern['direction'] == 'BULLISH' else "📉 BEARISH"
                    print(f"         Best: {best_pattern['type'].replace('_', ' ')} - {direction} (Confidence: {best_pattern.get('confidence', 0):.0f}%)")
            
            # Enhanced Trendline Summary
            if opp['trendlines']:
                tl = opp['trendlines']
                if tl.get('resistance_break'):
                    print(f"    📈 RESISTANCE BREAKOUT at ${tl['resistance_level']:.4f} (R²: {tl.get('r_squared_high', 0):.2f})")
                elif tl.get('support_break'):
                    print(f"    📉 SUPPORT BREAKDOWN at ${tl['support_level']:.4f} (R²: {tl.get('r_squared_low', 0):.2f})")
                else:
                    print(f"    📊 Trendlines: R=${tl['resistance_level']:.4f} | S=${tl['support_level']:.4f}")
            
            # Enhanced Volume Summary  
            if opp['volume']['volume_spike']:
                volume_strength = "🔥 EXPLOSIVE" if opp['volume']['volume_ratio'] > 5 else "🔊 SPIKE"
                print(f"    📈 Volume: {opp['volume']['volume_ratio']:.1f}x average ({volume_strength})")
                
            print("    " + "─" * 70)

def main():
    """Main scanning function with dynamic market mover support"""
    print("🔍 OPPORTUNITY SCANNER - STAGE 1")
    print("="*50)
    print("Finding the best trading opportunities across the market")
    print()
    
    scanner = OpportunityScanner()
    
    print("🎯 ENHANCED SCAN OPTIONS:")
    print("1. Static coin list (15 top coins)")
    print("2. Top 10 market gainers (24h)")  
    print("3. Top 10 market losers (24h)")
    print("4. Mixed scan (5 gainers + 5 losers)")
    print("5. Custom scan (specify your own limit)")
    
    choice = input("Enter choice (1-5): ").strip()
    
    try:
        if choice == '1':
            opportunities = scanner.scan_all_opportunities('static')
        elif choice == '2':
            opportunities = scanner.scan_all_opportunities('gainers', 10)
        elif choice == '3':
            opportunities = scanner.scan_all_opportunities('losers', 10)
        elif choice == '4':
            opportunities = scanner.scan_all_opportunities('mixed', 10)
        elif choice == '5':
            try:
                scan_type = input("Scan type (gainers/losers/mixed): ").strip().lower()
                if scan_type not in ['gainers', 'losers', 'mixed']:
                    scan_type = 'static'
                limit = int(input("Number of coins to scan (5-25): "))
                limit = max(5, min(25, limit))  # Clamp between 5-25
                opportunities = scanner.scan_all_opportunities(scan_type, limit)
            except ValueError:
                print("⚠️  Invalid input, using default static scan")
                opportunities = scanner.scan_all_opportunities('static')
        else:
            print("⚠️  Invalid choice, using default static scan")
            opportunities = scanner.scan_all_opportunities('static')
        
        scanner.display_top_opportunities(opportunities)
        
        # Save for Stage 2
        with open('opportunities/latest_scan.json', 'w') as f:
            json.dump(opportunities, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to opportunities/latest_scan.json")
        print("🎯 Ready for Stage 2: Human selection and strategy execution")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scan interrupted by user")
    except Exception as e:
        print(f"\n❌ Scan failed: {e}")
        print("🔄 Please try again or check your connection")

if __name__ == "__main__":
    main() 