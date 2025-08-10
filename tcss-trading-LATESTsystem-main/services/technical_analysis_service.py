#!/usr/bin/env python3
"""
TechnicalAnalysisService - Handles all technical analysis operations
"""

import numpy as np
import pandas as pd
from scipy.stats import linregress
import logging
from typing import Dict, List, Any, Optional
from config.settings import settings, TradingSettings

logger = logging.getLogger(__name__)

class TechnicalAnalysisService:
    """Service responsible for technical analysis operations"""
    
    def __init__(self, config: Optional[TradingSettings] = None):
        # Use provided config or global settings
        self.config = config or settings
        
        # Advanced FVG Detection Settings from configuration
        self.FVG_THRESHOLD = self.config.fvg_threshold
        self.FVG_PROXIMITY = self.config.fvg_proximity
        self.FVG_VOLUME_CONFIRM = self.config.fvg_volume_confirm
        self.FVG_MAX_AGE = self.config.fvg_max_age
        
        # Pattern Recognition Settings from configuration
        self.PATTERN_TOLERANCE = self.config.pattern_tolerance
        self.MIN_PATTERN_PERIODS = self.config.min_pattern_periods
    
    def detect_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Advanced Fair Value Gap Detection"""
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
            
            # Advanced 3-candle FVG detection
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
                    
                    # Bullish FVG Detection
                    if candle3['low'] > candle1['high']:
                        gap_size = (candle3['low'] - candle1['high']) / candle1['high']
                        
                        if gap_size > self.FVG_THRESHOLD:
                            # Volume confirmation
                            volume_strength = candle2['volume'] / df['volume'].rolling(20).mean().iloc[i-1] if i >= 20 else 1.0
                            volume_confirmed = volume_strength > self.FVG_VOLUME_CONFIRM
                            
                            # Calculate gap age
                            gap_age = len(df) - i
                            
                            # Check proximity
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
                                'formation_index': int(i-1),
                                'status': 'UNFILLED' if not self._is_gap_filled(df, i, candle1['high'], candle3['low']) else 'FILLED'
                            })
                    
                    # Bearish FVG Detection
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
                                'formation_index': int(i-1),
                                'status': 'UNFILLED' if not self._is_gap_filled(df, i, candle3['high'], candle1['low']) else 'FILLED'
                            })
                                
                except Exception as e:
                    logger.warning(f"Error processing FVG at index {i}: {e}")
                    continue
            
            # Filter out old gaps and prioritize unfilled gaps
            active_fvg_zones = [gap for gap in fvg_zones if gap['age'] <= self.FVG_MAX_AGE]
            unfilled_gaps = [gap for gap in active_fvg_zones if gap['status'] == 'UNFILLED']
            
            logger.info(f"Detected {len(fvg_zones)} total FVG zones, {len(unfilled_gaps)} unfilled, {len(active_fvg_zones)} active")
            
            return unfilled_gaps + [gap for gap in active_fvg_zones if gap['status'] == 'FILLED']
            
        except Exception as e:
            logger.error(f"Error in FVG detection: {e}")
            return []
    
    def _is_gap_filled(self, df: pd.DataFrame, gap_index: int, gap_low: float, gap_high: float) -> bool:
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
    
    def calculate_trendlines(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Calculate trendlines using linear regression"""
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
            
            # Calculate trendlines
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
            
            # Current price vs trendlines
            current_price = df.iloc[-1]['close']
            if pd.isna(current_price) or current_price <= 0:
                logger.error("Invalid current price for trendline analysis")
                return None
            
            # Calculate projected trendline values
            next_period = len(recent_df)
            resistance_level = slope_high * next_period + intercept_high
            support_level = slope_low * next_period + intercept_low
            
            # Trendline strength based on R-squared
            resistance_strength = abs(r_high) * 10  # 0-10 scale
            support_strength = abs(r_low) * 10
            
            # Price position relative to trendlines
            resistance_distance = (resistance_level - current_price) / current_price
            support_distance = (current_price - support_level) / current_price
            
            return {
                'resistance': {
                    'level': float(resistance_level),
                    'slope': float(slope_high),
                    'strength': float(resistance_strength),
                    'r_squared': float(r_high ** 2),
                    'distance_from_price': float(resistance_distance)
                },
                'support': {
                    'level': float(support_level),
                    'slope': float(slope_low),
                    'strength': float(support_strength),
                    'r_squared': float(r_low ** 2),
                    'distance_from_price': float(support_distance)
                },
                'trend_direction': 'BULLISH' if slope_high > 0 and slope_low > 0 else 'BEARISH' if slope_high < 0 and slope_low < 0 else 'SIDEWAYS',
                'price_position': 'NEAR_RESISTANCE' if resistance_distance < 0.02 else 'NEAR_SUPPORT' if support_distance < 0.02 else 'MIDDLE'
            }
            
        except Exception as e:
            logger.error(f"Error calculating trendlines: {e}")
            return None
    
    def analyze_volume(self, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze volume patterns and anomalies"""
        try:
            if df is None or len(df) < 20:
                logger.warning("Insufficient data for volume analysis")
                return None
            
            if 'volume' not in df.columns:
                logger.error("Volume column missing for analysis")
                return None
            
            volumes = df['volume'].values
            if len(volumes) == 0 or np.all(volumes == 0):
                logger.warning("No volume data available")
                return None
            
            # Calculate volume metrics
            current_volume = volumes[-1]
            avg_volume_20 = np.mean(volumes[-20:])
            avg_volume_5 = np.mean(volumes[-5:])
            volume_std = np.std(volumes[-20:])
            
            # Volume ratios
            volume_ratio_20 = current_volume / avg_volume_20 if avg_volume_20 > 0 else 0
            volume_ratio_5 = current_volume / avg_volume_5 if avg_volume_5 > 0 else 0
            
            # Volume trend
            recent_volumes = volumes[-10:]
            volume_trend = 'INCREASING' if np.mean(recent_volumes[:5]) < np.mean(recent_volumes[5:]) else 'DECREASING'
            
            # Volume spikes (Z-score based)
            z_score = (current_volume - avg_volume_20) / volume_std if volume_std > 0 else 0
            volume_spike = abs(z_score) > 2.0  # 2 standard deviations
            
            return {
                'current_volume': float(current_volume),
                'avg_volume_20': float(avg_volume_20),
                'volume_ratio_20': float(volume_ratio_20),
                'volume_ratio_5': float(volume_ratio_5),
                'volume_trend': volume_trend,
                'volume_spike': bool(volume_spike),
                'z_score': float(z_score),
                'strength': min(volume_ratio_20 * 2, 10)  # 0-10 scale
            }
            
        except Exception as e:
            logger.error(f"Error in volume analysis: {e}")
            return None
    
    def detect_pattern_formations(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect various chart patterns"""
        try:
            if df is None or len(df) < self.MIN_PATTERN_PERIODS:
                logger.warning("Insufficient data for pattern detection")
                return []
            
            patterns = []
            
            # Detect double/triple patterns
            double_triple = self._detect_double_triple_patterns(df)
            if double_triple:
                patterns.extend(double_triple)
            
            # Detect head and shoulders
            head_shoulders = self._detect_head_shoulders(df)
            if head_shoulders:
                patterns.extend(head_shoulders)
            
            # Detect flag/pennant patterns
            flag_pennant = self._detect_flag_pennant(df)
            if flag_pennant:
                patterns.extend(flag_pennant)
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error in pattern detection: {e}")
            return []
    
    def _detect_double_triple_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect double top/bottom and triple top/bottom patterns"""
        try:
            patterns = []
            
            # Find peaks and troughs
            highs = df['high'].values
            lows = df['low'].values
            
            peaks = self._find_peaks_troughs(highs, 'peaks')
            troughs = self._find_peaks_troughs(lows, 'troughs')
            
            # Double top detection
            if len(peaks) >= 2:
                for i in range(len(peaks) - 1):
                    peak1_idx, peak1_val = peaks[i]
                    peak2_idx, peak2_val = peaks[i + 1]
                    
                    # Check if peaks are similar height
                    height_diff = abs(peak1_val - peak2_val) / peak1_val
                    if height_diff < self.PATTERN_TOLERANCE:
                        patterns.append({
                            'type': 'DOUBLE_TOP',
                            'confidence': float(max(0, 1 - height_diff * 10)),
                            'level': float((peak1_val + peak2_val) / 2),
                            'formation_period': int(peak2_idx - peak1_idx)
                        })
            
            # Double bottom detection
            if len(troughs) >= 2:
                for i in range(len(troughs) - 1):
                    trough1_idx, trough1_val = troughs[i]
                    trough2_idx, trough2_val = troughs[i + 1]
                    
                    # Check if troughs are similar depth
                    depth_diff = abs(trough1_val - trough2_val) / trough1_val
                    if depth_diff < self.PATTERN_TOLERANCE:
                        patterns.append({
                            'type': 'DOUBLE_BOTTOM',
                            'confidence': float(max(0, 1 - depth_diff * 10)),
                            'level': float((trough1_val + trough2_val) / 2),
                            'formation_period': int(trough2_idx - trough1_idx)
                        })
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Error detecting double/triple patterns: {e}")
            return []
    
    def _detect_head_shoulders(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect head and shoulders patterns"""
        try:
            patterns = []
            peaks = self._find_peaks_troughs(df['high'].values, 'peaks')
            
            if len(peaks) >= 3:
                for i in range(len(peaks) - 2):
                    left_shoulder = peaks[i][1]
                    head = peaks[i + 1][1]
                    right_shoulder = peaks[i + 2][1]
                    
                    # Check head and shoulders formation
                    if (head > left_shoulder and head > right_shoulder and
                        abs(left_shoulder - right_shoulder) / left_shoulder < self.PATTERN_TOLERANCE):
                        
                        patterns.append({
                            'type': 'HEAD_AND_SHOULDERS',
                            'confidence': 0.7,
                            'neckline': float((left_shoulder + right_shoulder) / 2),
                            'head_level': float(head)
                        })
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Error detecting head and shoulders: {e}")
            return []
    
    def _detect_flag_pennant(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect flag and pennant patterns"""
        try:
            patterns = []
            
            # Simple flag detection based on price consolidation after strong move
            if len(df) >= 20:
                recent_high = df['high'].tail(10).max()
                recent_low = df['low'].tail(10).min()
                range_size = (recent_high - recent_low) / recent_low
                
                # Previous strong move
                prev_range = (df['high'].iloc[-20:-10].max() - df['low'].iloc[-20:-10].min()) / df['low'].iloc[-20:-10].min()
                
                if range_size < prev_range * 0.5:  # Consolidation after strong move
                    patterns.append({
                        'type': 'FLAG',
                        'confidence': 0.6,
                        'consolidation_range': float(range_size),
                        'breakout_level': float(recent_high)
                    })
            
            return patterns
            
        except Exception as e:
            logger.warning(f"Error detecting flag/pennant: {e}")
            return []
    
    def _find_peaks_troughs(self, data: np.ndarray, peak_type: str = 'peaks') -> List[tuple]:
        """Find peaks or troughs in price data"""
        try:
            extremes = []
            
            for i in range(1, len(data) - 1):
                if peak_type == 'peaks':
                    if data[i] > data[i-1] and data[i] > data[i+1]:
                        extremes.append((i, data[i]))
                else:  # troughs
                    if data[i] < data[i-1] and data[i] < data[i+1]:
                        extremes.append((i, data[i]))
            
            return extremes
            
        except Exception as e:
            logger.warning(f"Error finding {peak_type}: {e}")
            return [] 