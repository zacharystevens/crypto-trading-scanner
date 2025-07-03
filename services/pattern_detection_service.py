#!/usr/bin/env python3
"""
PatternDetectionService - Handles advanced pattern detection and recognition
"""

import numpy as np
import pandas as pd
import logging
from typing import Dict, List, Any, Optional
from config.settings import settings, TradingSettings

logger = logging.getLogger(__name__)

class PatternDetectionService:
    """Service responsible for detecting chart patterns and formations"""
    
    def __init__(self, config: Optional[TradingSettings] = None):
        # Use provided config or global settings
        self.config = config or settings
        
        # Pattern Recognition Settings from configuration
        self.PATTERN_TOLERANCE = self.config.pattern_tolerance
        self.MIN_PATTERN_PERIODS = self.config.min_pattern_periods
        self.CONFLUENCE_THRESHOLD = self.config.confluence_threshold
        
        # Multi-timeframe settings from configuration
        self.TIMEFRAMES = self.config.timeframes
        self.TIMEFRAME_WEIGHTS = self.config.timeframe_weights
    
    def analyze_timeframe_confluence(self, symbol: str, timeframe_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Analyze confluence across multiple timeframes"""
        try:
            if not timeframe_data:
                logger.warning(f"No timeframe data provided for {symbol}")
                return self._get_default_confluence()
            
            timeframe_analyses = {}
            total_weighted_score = 0
            total_weight = 0
            directions = []
            
            # Analyze each timeframe
            for timeframe, df in timeframe_data.items():
                if df is not None and len(df) >= 10:
                    analysis = self._analyze_single_timeframe(timeframe, df)
                    if analysis:
                        timeframe_analyses[timeframe] = analysis
                        
                        # Weight the analysis
                        weight = self.TIMEFRAME_WEIGHTS.get(timeframe, 0.1)
                        weighted_score = analysis['score'] * weight
                        total_weighted_score += weighted_score
                        total_weight += weight
                        
                        # Collect directions for confluence
                        if analysis['direction'] != 'NEUTRAL':
                            directions.append(analysis['direction'])
            
            # Calculate confluence metrics
            if not timeframe_analyses:
                logger.warning(f"No valid timeframe analyses for {symbol}")
                return self._get_default_confluence()
            
            # Determine overall direction
            bullish_count = directions.count('BULLISH')
            bearish_count = directions.count('BEARISH')
            total_directional = bullish_count + bearish_count
            
            if total_directional == 0:
                overall_direction = 'NEUTRAL'
                confluence_strength = 0
            else:
                if bullish_count > bearish_count:
                    overall_direction = 'BULLISH'
                    confluence_strength = bullish_count / len(timeframe_analyses)
                elif bearish_count > bullish_count:
                    overall_direction = 'BEARISH'
                    confluence_strength = bearish_count / len(timeframe_analyses)
                else:
                    overall_direction = 'MIXED'
                    confluence_strength = 0.5
            
            # Calculate final weighted score
            final_score = total_weighted_score / total_weight if total_weight > 0 else 0
            
            # Confluence quality assessment
            quality_score = confluence_strength
            if len(timeframe_analyses) >= 3:
                quality_score *= 1.2  # Bonus for multiple timeframes
            if confluence_strength >= 0.8:
                quality_score *= 1.1  # Strong confluence bonus
            
            confluence_quality = min(quality_score, 1.0)
            
            return {
                'symbol': symbol,
                'timeframe_count': len(timeframe_analyses),
                'direction': overall_direction,
                'confluence_strength': round(confluence_strength, 3),
                'confluence_quality': round(confluence_quality, 3),
                'weighted_score': round(final_score, 2),
                'timeframe_analyses': timeframe_analyses,
                'bullish_timeframes': bullish_count,
                'bearish_timeframes': bearish_count,
                'neutral_timeframes': len(timeframe_analyses) - total_directional
            }
            
        except Exception as e:
            logger.error(f"Error in timeframe confluence analysis for {symbol}: {e}")
            return self._get_default_confluence()
    
    def _analyze_single_timeframe(self, timeframe: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        """Analyze a single timeframe for patterns and signals"""
        try:
            if df is None or len(df) < 10:
                return None
            
            # Get current price and recent price action
            current_price = df.iloc[-1]['close']
            prev_price = df.iloc[-2]['close'] if len(df) > 1 else current_price
            price_change = (current_price - prev_price) / prev_price if prev_price > 0 else 0
            
            # Calculate basic metrics
            sma_20 = df['close'].rolling(20).mean().iloc[-1] if len(df) >= 20 else current_price
            volume_avg = df['volume'].rolling(10).mean().iloc[-1] if len(df) >= 10 else df['volume'].iloc[-1]
            current_volume = df['volume'].iloc[-1]
            
            # Trend analysis
            trend_score = 0
            direction = 'NEUTRAL'
            
            # Price vs SMA
            if current_price > sma_20:
                trend_score += 2
                direction = 'BULLISH'
            elif current_price < sma_20:
                trend_score -= 2
                direction = 'BEARISH'
            
            # Recent price momentum
            if price_change > 0.005:  # > 0.5% up
                trend_score += 1
            elif price_change < -0.005:  # > 0.5% down
                trend_score -= 1
            
            # Volume confirmation
            volume_ratio = current_volume / volume_avg if volume_avg > 0 else 1
            if volume_ratio > 1.5:  # High volume
                trend_score += 1 if trend_score > 0 else -1
            
            # Normalize score to 0-10 scale
            normalized_score = max(0, min(10, (trend_score + 5)))  # Convert -5 to +5 range to 0-10
            
            # Determine final direction
            if trend_score >= 2:
                direction = 'BULLISH'
            elif trend_score <= -2:
                direction = 'BEARISH'
            else:
                direction = 'NEUTRAL'
            
            return {
                'timeframe': timeframe,
                'score': normalized_score,
                'direction': direction,
                'trend_score': trend_score,
                'price_change': round(price_change * 100, 2),
                'volume_ratio': round(volume_ratio, 2),
                'price_vs_sma': 'ABOVE' if current_price > sma_20 else 'BELOW',
                'current_price': current_price,
                'sma_20': sma_20
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing {timeframe} timeframe: {e}")
            return None
    
    def _get_default_confluence(self) -> Dict[str, Any]:
        """Return default confluence result for error cases"""
        return {
            'symbol': 'UNKNOWN',
            'timeframe_count': 0,
            'direction': 'NEUTRAL',
            'confluence_strength': 0,
            'confluence_quality': 0,
            'weighted_score': 0,
            'timeframe_analyses': {},
            'bullish_timeframes': 0,
            'bearish_timeframes': 0,
            'neutral_timeframes': 0
        }
    
    def detect_breakout_patterns(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect breakout patterns like triangles, wedges, etc."""
        try:
            patterns = []
            
            if df is None or len(df) < 20:
                return patterns
            
            # Simple triangle detection
            recent_highs = df['high'].tail(10)
            recent_lows = df['low'].tail(10)
            
            # Check for converging highs and lows
            if len(recent_highs) >= 5 and len(recent_lows) >= 5:
                high_trend = np.polyfit(range(len(recent_highs)), recent_highs, 1)[0]
                low_trend = np.polyfit(range(len(recent_lows)), recent_lows, 1)[0]
                
                # Converging triangle (highs decreasing, lows increasing)
                if high_trend < -0.001 and low_trend > 0.001:
                    patterns.append({
                        'type': 'TRIANGLE_CONVERGING',
                        'confidence': 0.7,
                        'breakout_level': recent_highs.max(),
                        'support_level': recent_lows.min()
                    })
                
                # Ascending triangle (highs flat, lows rising)
                elif abs(high_trend) < 0.001 and low_trend > 0.001:
                    patterns.append({
                        'type': 'TRIANGLE_ASCENDING',
                        'confidence': 0.8,
                        'breakout_level': recent_highs.max(),
                        'support_level': recent_lows.min()
                    })
                
                # Descending triangle (highs falling, lows flat)
                elif high_trend < -0.001 and abs(low_trend) < 0.001:
                    patterns.append({
                        'type': 'TRIANGLE_DESCENDING',
                        'confidence': 0.8,
                        'breakout_level': recent_highs.max(),
                        'support_level': recent_lows.min()
                    })
            
            return patterns
            
        except Exception as e:
            logger.error(f"Error detecting breakout patterns: {e}")
            return []
    
    def detect_support_resistance_levels(self, df: pd.DataFrame) -> Dict[str, List[float]]:
        """Detect key support and resistance levels"""
        try:
            if df is None or len(df) < 20:
                return {'support': [], 'resistance': []}
            
            # Find peaks and troughs
            highs = df['high'].values
            lows = df['low'].values
            
            support_levels = []
            resistance_levels = []
            
            # Simple peak/trough detection
            for i in range(2, len(df) - 2):
                # Resistance (peaks)
                if (highs[i] > highs[i-1] and highs[i] > highs[i+1] and
                    highs[i] > highs[i-2] and highs[i] > highs[i+2]):
                    resistance_levels.append(highs[i])
                
                # Support (troughs)
                if (lows[i] < lows[i-1] and lows[i] < lows[i+1] and
                    lows[i] < lows[i-2] and lows[i] < lows[i+2]):
                    support_levels.append(lows[i])
            
            # Remove duplicates and sort
            support_levels = sorted(list(set(support_levels)))[-5:]  # Keep top 5
            resistance_levels = sorted(list(set(resistance_levels)), reverse=True)[:5]  # Keep top 5
            
            return {
                'support': support_levels,
                'resistance': resistance_levels
            }
            
        except Exception as e:
            logger.error(f"Error detecting support/resistance levels: {e}")
            return {'support': [], 'resistance': []}
    
    def analyze_pattern_confluence(self, patterns: List[Dict[str, Any]], 
                                   fvg_zones: List[Dict[str, Any]],
                                   trendlines: Dict[str, Any],
                                   support_resistance: Dict[str, List[float]]) -> Dict[str, Any]:
        """Analyze confluence between different pattern types"""
        try:
            confluence_score = 0
            confluence_factors = []
            
            # Pattern confluence
            if patterns:
                confluence_score += len(patterns) * 0.2
                confluence_factors.extend([p['type'] for p in patterns])
            
            # FVG confluence
            if fvg_zones:
                unfilled_gaps = [g for g in fvg_zones if g['status'] == 'UNFILLED']
                confluence_score += len(unfilled_gaps) * 0.3
                confluence_factors.extend([f"FVG_{g['type']}" for g in unfilled_gaps])
            
            # Trendline confluence
            if trendlines:
                if trendlines.get('price_position') in ['NEAR_RESISTANCE', 'NEAR_SUPPORT']:
                    confluence_score += 0.4
                    confluence_factors.append(f"TRENDLINE_{trendlines['price_position']}")
            
            # Support/Resistance confluence
            if support_resistance:
                total_levels = len(support_resistance.get('support', [])) + len(support_resistance.get('resistance', []))
                confluence_score += total_levels * 0.1
                confluence_factors.append(f"SR_LEVELS_{total_levels}")
            
            # Normalize score
            final_score = min(confluence_score, 1.0)
            
            return {
                'confluence_score': round(final_score, 3),
                'confluence_factors': confluence_factors,
                'pattern_count': len(patterns),
                'fvg_count': len(fvg_zones),
                'has_trendline_confluence': trendlines is not None,
                'sr_level_count': len(support_resistance.get('support', [])) + len(support_resistance.get('resistance', []))
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pattern confluence: {e}")
            return {
                'confluence_score': 0,
                'confluence_factors': [],
                'pattern_count': 0,
                'fvg_count': 0,
                'has_trendline_confluence': False,
                'sr_level_count': 0
            } 