#!/usr/bin/env python3
"""
ScoringService - Handles opportunity scoring and ranking algorithms
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from config.settings import settings, TradingSettings

logger = logging.getLogger(__name__)

class ScoringService:
    """Service responsible for scoring and ranking trading opportunities"""
    
    def __init__(self, config: Optional[TradingSettings] = None):
        # Use provided config or global settings
        self.config = config or settings
        
        # Scoring weights from configuration
        self.SCORING_WEIGHTS = self.config.scoring_weights
        
        # Score thresholds from configuration
        self.MIN_SCORE_THRESHOLD = self.config.min_score_threshold
        self.STRONG_SIGNAL_THRESHOLD = self.config.strong_signal_threshold
        self.EXCELLENT_SIGNAL_THRESHOLD = self.config.excellent_signal_threshold
    
    def score_opportunity(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Score a trading opportunity based on comprehensive analysis"""
        try:
            if not analysis:
                logger.warning("No analysis data provided for scoring")
                return self._get_default_score()
            
            # Extract analysis components
            fvg_zones = analysis.get('fvg_zones', [])
            trendlines = analysis.get('trendlines', {})
            volume_analysis = analysis.get('volume_analysis', {})
            patterns = analysis.get('patterns', [])
            confluence_quality = analysis.get('confluence_quality', {})
            
            # Calculate individual scores
            fvg_score = self._score_fvg_zones(fvg_zones)
            trendline_score = self._score_trendlines(trendlines)
            volume_score = self._score_volume_analysis(volume_analysis)
            pattern_score = self._score_patterns(patterns)
            confluence_score = self._score_confluence(confluence_quality)
            
            # Calculate weighted final score
            weighted_score = (
                fvg_score * self.SCORING_WEIGHTS['fvg'] +
                trendline_score * self.SCORING_WEIGHTS['trendline'] +
                volume_score * self.SCORING_WEIGHTS['volume'] +
                pattern_score * self.SCORING_WEIGHTS['patterns'] +
                confluence_score * self.SCORING_WEIGHTS['confluence']
            )
            
            # Normalize to 0-100 scale
            final_score = max(0, min(100, weighted_score))
            
            # Determine signal strength
            signal_strength = self._get_signal_strength(final_score)
            
            # Generate recommendation
            recommendation = self._generate_recommendation(final_score, confluence_quality)
            
            # Calculate confidence level
            confidence = self._calculate_confidence(analysis, final_score)
            
            return {
                'score': round(final_score, 1),
                'signal_strength': signal_strength,
                'recommendation': recommendation,
                'confidence': round(confidence, 3),
                'component_scores': {
                    'fvg': round(fvg_score, 1),
                    'trendline': round(trendline_score, 1),
                    'volume': round(volume_score, 1),
                    'patterns': round(pattern_score, 1),
                    'confluence': round(confluence_score, 1)
                },
                'score_breakdown': {
                    'fvg_contribution': round(fvg_score * self.SCORING_WEIGHTS['fvg'], 1),
                    'trendline_contribution': round(trendline_score * self.SCORING_WEIGHTS['trendline'], 1),
                    'volume_contribution': round(volume_score * self.SCORING_WEIGHTS['volume'], 1),
                    'pattern_contribution': round(pattern_score * self.SCORING_WEIGHTS['patterns'], 1),
                    'confluence_contribution': round(confluence_score * self.SCORING_WEIGHTS['confluence'], 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Error scoring opportunity: {e}")
            return self._get_default_score()
    
    def _score_fvg_zones(self, fvg_zones: List[Dict[str, Any]]) -> float:
        """Score Fair Value Gap zones"""
        try:
            if not fvg_zones:
                return 0
            
            total_score = 0
            for gap in fvg_zones:
                gap_score = 0
                
                # Base score from gap strength
                gap_score += gap.get('strength', 0) * 5  # 0-15 -> 0-75
                
                # Volume confirmation bonus
                if gap.get('volume_confirmed', False):
                    gap_score += 15
                
                # Proximity bonus (gap near current price)
                if gap.get('near_price', False):
                    gap_score += 10
                
                # Unfilled gap bonus
                if gap.get('status') == 'UNFILLED':
                    gap_score += 20
                
                # Age penalty (older gaps less relevant)
                age = gap.get('age', 0)
                if age > 20:
                    gap_score *= 0.8
                elif age > 10:
                    gap_score *= 0.9
                
                total_score += gap_score
            
            # Average score across gaps, cap at 100
            avg_score = total_score / len(fvg_zones)
            return min(100, avg_score)
            
        except Exception as e:
            logger.warning(f"Error scoring FVG zones: {e}")
            return 0
    
    def _score_trendlines(self, trendlines: Dict[str, Any]) -> float:
        """Score trendline analysis"""
        try:
            if not trendlines:
                return 0
            
            score = 0
            
            # Support trendline strength
            support = trendlines.get('support', {})
            if support:
                support_strength = support.get('strength', 0)
                support_r_squared = support.get('r_squared', 0)
                score += support_strength * 5 + support_r_squared * 30
            
            # Resistance trendline strength
            resistance = trendlines.get('resistance', {})
            if resistance:
                resistance_strength = resistance.get('strength', 0)
                resistance_r_squared = resistance.get('r_squared', 0)
                score += resistance_strength * 5 + resistance_r_squared * 30
            
            # Trend direction bonus
            trend_direction = trendlines.get('trend_direction', 'SIDEWAYS')
            if trend_direction in ['BULLISH', 'BEARISH']:
                score += 20
            
            # Price position bonus
            price_position = trendlines.get('price_position', 'MIDDLE')
            if price_position in ['NEAR_RESISTANCE', 'NEAR_SUPPORT']:
                score += 15
            
            return min(100, score)
            
        except Exception as e:
            logger.warning(f"Error scoring trendlines: {e}")
            return 0
    
    def _score_volume_analysis(self, volume_analysis: Dict[str, Any]) -> float:
        """Score volume analysis"""
        try:
            if not volume_analysis:
                return 0
            
            score = 0
            
            # Volume ratio scoring
            volume_ratio_20 = volume_analysis.get('volume_ratio_20', 1)
            if volume_ratio_20 > 2:
                score += 40
            elif volume_ratio_20 > 1.5:
                score += 25
            elif volume_ratio_20 > 1.2:
                score += 15
            
            # Volume spike bonus
            if volume_analysis.get('volume_spike', False):
                score += 25
            
            # Volume trend bonus
            volume_trend = volume_analysis.get('volume_trend', 'DECREASING')
            if volume_trend == 'INCREASING':
                score += 15
            
            # Z-score bonus (unusual volume)
            z_score = abs(volume_analysis.get('z_score', 0))
            if z_score > 2:
                score += 15
            elif z_score > 1.5:
                score += 10
            
            return min(100, score)
            
        except Exception as e:
            logger.warning(f"Error scoring volume analysis: {e}")
            return 0
    
    def _score_patterns(self, patterns: List[Dict[str, Any]]) -> float:
        """Score chart patterns"""
        try:
            if not patterns:
                return 0
            
            total_score = 0
            for pattern in patterns:
                pattern_score = 0
                
                # Base score from confidence
                confidence = pattern.get('confidence', 0)
                pattern_score += confidence * 60
                
                # Pattern type bonuses
                pattern_type = pattern.get('type', '')
                if 'DOUBLE' in pattern_type:
                    pattern_score += 20
                elif 'HEAD_AND_SHOULDERS' in pattern_type:
                    pattern_score += 25
                elif 'TRIANGLE' in pattern_type:
                    pattern_score += 15
                elif 'FLAG' in pattern_type:
                    pattern_score += 10
                
                total_score += pattern_score
            
            # Average score across patterns
            avg_score = total_score / len(patterns)
            return min(100, avg_score)
            
        except Exception as e:
            logger.warning(f"Error scoring patterns: {e}")
            return 0
    
    def _score_confluence(self, confluence_quality: Dict[str, Any]) -> float:
        """Score confluence analysis"""
        try:
            if not confluence_quality:
                return 0
            
            score = 0
            
            # Confluence strength
            confluence_strength = confluence_quality.get('confluence_strength', 0)
            score += confluence_strength * 60
            
            # Direction clarity bonus
            direction = confluence_quality.get('direction', 'NEUTRAL')
            if direction in ['BULLISH', 'BEARISH']:
                score += 25
            elif direction == 'MIXED':
                score += 10
            
            # Timeframe count bonus
            timeframe_count = confluence_quality.get('timeframe_count', 0)
            if timeframe_count >= 4:
                score += 15
            elif timeframe_count >= 3:
                score += 10
            elif timeframe_count >= 2:
                score += 5
            
            return min(100, score)
            
        except Exception as e:
            logger.warning(f"Error scoring confluence: {e}")
            return 0
    
    def _get_signal_strength(self, score: float) -> str:
        """Determine signal strength based on score"""
        if score >= self.EXCELLENT_SIGNAL_THRESHOLD:
            return 'EXCELLENT'
        elif score >= self.STRONG_SIGNAL_THRESHOLD:
            return 'STRONG'
        elif score >= self.MIN_SCORE_THRESHOLD:
            return 'MODERATE'
        else:
            return 'WEAK'
    
    def _generate_recommendation(self, score: float, confluence_quality: Dict[str, Any]) -> str:
        """Generate trading recommendation"""
        try:
            direction = confluence_quality.get('direction', 'NEUTRAL') if confluence_quality else 'NEUTRAL'
            
            if score >= self.EXCELLENT_SIGNAL_THRESHOLD:
                if direction == 'BULLISH':
                    return 'STRONG_BUY'
                elif direction == 'BEARISH':
                    return 'STRONG_SELL'
                else:
                    return 'WATCH'
            elif score >= self.STRONG_SIGNAL_THRESHOLD:
                if direction == 'BULLISH':
                    return 'BUY'
                elif direction == 'BEARISH':
                    return 'SELL'
                else:
                    return 'WATCH'
            elif score >= self.MIN_SCORE_THRESHOLD:
                if direction == 'BULLISH':
                    return 'WEAK_BUY'
                elif direction == 'BEARISH':
                    return 'WEAK_SELL'
                else:
                    return 'NEUTRAL'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            logger.warning(f"Error generating recommendation: {e}")
            return 'NEUTRAL'
    
    def _calculate_confidence(self, analysis: Dict[str, Any], score: float) -> float:
        """Calculate confidence level in the analysis"""
        try:
            confidence = 0
            
            # Base confidence from score
            confidence += score / 100 * 0.4
            
            # Data quality factors
            confluence_quality = analysis.get('confluence_quality', {})
            timeframe_count = confluence_quality.get('timeframe_count', 0)
            if timeframe_count >= 3:
                confidence += 0.2
            elif timeframe_count >= 2:
                confidence += 0.1
            
            # Pattern confirmation
            patterns = analysis.get('patterns', [])
            if len(patterns) >= 2:
                confidence += 0.15
            elif len(patterns) >= 1:
                confidence += 0.1
            
            # Volume confirmation
            volume_analysis = analysis.get('volume_analysis', {})
            if volume_analysis.get('volume_spike', False):
                confidence += 0.1
            
            # FVG confirmation
            fvg_zones = analysis.get('fvg_zones', [])
            unfilled_gaps = [g for g in fvg_zones if g.get('status') == 'UNFILLED']
            if len(unfilled_gaps) >= 1:
                confidence += 0.05
            
            return min(1.0, confidence)
            
        except Exception as e:
            logger.warning(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_default_score(self) -> Dict[str, Any]:
        """Return default score for error cases"""
        return {
            'score': 0,
            'signal_strength': 'WEAK',
            'recommendation': 'NEUTRAL',
            'confidence': 0,
            'component_scores': {
                'fvg': 0,
                'trendline': 0,
                'volume': 0,
                'patterns': 0,
                'confluence': 0
            },
            'score_breakdown': {
                'fvg_contribution': 0,
                'trendline_contribution': 0,
                'volume_contribution': 0,
                'pattern_contribution': 0,
                'confluence_contribution': 0
            }
        }
    
    def rank_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank opportunities by score and other factors"""
        try:
            if not opportunities:
                return []
            
            # Sort by score (descending), then by confidence
            ranked = sorted(
                opportunities,
                key=lambda x: (x.get('score', 0), x.get('confidence', 0)),
                reverse=True
            )
            
            # Add ranking information
            for i, opp in enumerate(ranked):
                opp['rank'] = i + 1
                opp['percentile'] = round((len(ranked) - i) / len(ranked) * 100, 1)
            
            return ranked
            
        except Exception as e:
            logger.error(f"Error ranking opportunities: {e}")
            return opportunities 