#!/usr/bin/env python3
"""
Centralized Configuration Management for Trading System
Uses Pydantic BaseSettings for type-safe, environment-based configuration
"""

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from typing import List, Dict, Optional, Any
import os
from pathlib import Path

class TradingSettings(BaseSettings):
    """Main configuration class for the trading system"""
    
    # ============================================================================
    # MARKET DATA CONFIGURATION
    # ============================================================================
    max_coins_limit: int = Field(
        default=20, 
        description="Maximum number of coins to scan (1-100)",
        ge=1, le=100
    )
    min_volume_usdt: float = Field(
        default=1000000, 
        description="Minimum 24h volume in USDT to consider a trading pair",
        ge=0
    )
    min_price: float = Field(
        default=0.0001, 
        description="Minimum price to avoid micro-cap chaos",
        ge=0
    )
    max_price: float = Field(
        default=150000, 
        description="Maximum price filter (accommodates BTC range)",
        ge=0
    )
    excluded_symbols: List[str] = Field(
        default=['USDT', 'BUSD', 'USDC', 'DAI', 'TUSD'], 
        description="Stablecoins and symbols to exclude from analysis"
    )
    
    # ============================================================================
    # TECHNICAL ANALYSIS CONFIGURATION
    # ============================================================================
    
    # Fair Value Gap Settings
    fvg_threshold: float = Field(
        default=0.005, 
        description="Minimum gap threshold (0.5% default)",
        ge=0, le=1
    )
    fvg_proximity: float = Field(
        default=0.02, 
        description="Proximity threshold for FVG alerts (2% default)",
        ge=0, le=1
    )
    fvg_volume_confirm: float = Field(
        default=1.5, 
        description="Volume confirmation threshold for FVG",
        ge=1
    )
    fvg_max_age: int = Field(
        default=50, 
        description="Maximum candles to track unfilled gaps",
        ge=1
    )
    
    # Pattern Recognition Settings
    pattern_tolerance: float = Field(
        default=0.01, 
        description="Tolerance for pattern matching (1% default)",
        ge=0, le=1
    )
    min_pattern_periods: int = Field(
        default=5, 
        description="Minimum periods for pattern formation",
        ge=3
    )
    
    # Multi-timeframe Confluence Settings
    confluence_threshold: float = Field(
        default=0.6, 
        description="Agreement threshold across timeframes (60% default)",
        ge=0, le=1
    )
    min_timeframes_agree: int = Field(
        default=2, 
        description="Minimum timeframes that must agree",
        ge=1
    )
    strong_confluence_threshold: float = Field(
        default=0.8, 
        description="Strong signal threshold (80% default)",
        ge=0, le=1
    )
    
    # Timeframes and Weights
    timeframes: List[str] = Field(
        default=['15m', '1h', '4h', '1d'], 
        description="Active analysis timeframes"
    )
    primary_timeframe: str = Field(
        default='1h', 
        description="Main analysis timeframe"
    )
    timeframe_weights: Dict[str, float] = Field(
        default={
            '1d': 0.35,
            '4h': 0.30,
            '1h': 0.25,
            '15m': 0.10
        },
        description="Importance weighting for each timeframe"
    )
    
    # ============================================================================
    # CACHING CONFIGURATION
    # ============================================================================
    ticker_cache_duration: int = Field(
        default=60, 
        description="Ticker data cache TTL in seconds",
        ge=1
    )
    analysis_cache_duration: int = Field(
        default=900, 
        description="Analysis results cache TTL in seconds (15 minutes)",
        ge=1
    )
    ohlcv_cache_duration: int = Field(
        default=300, 
        description="OHLCV data cache TTL in seconds (5 minutes)",
        ge=1
    )
    curated_cache_duration: int = Field(
        default=900, 
        description="Curated coins cache TTL in seconds (15 minutes)",
        ge=1
    )
    
    # ============================================================================
    # SCORING CONFIGURATION
    # ============================================================================
    scoring_weights: Dict[str, float] = Field(
        default={
            'fvg': 0.25,
            'trendline': 0.20,
            'volume': 0.15,
            'patterns': 0.20,
            'confluence': 0.20
        },
        description="Weights for different scoring factors"
    )
    min_score_threshold: float = Field(
        default=30, 
        description="Minimum score to consider an opportunity",
        ge=0, le=100
    )
    strong_signal_threshold: float = Field(
        default=70, 
        description="Strong signal threshold",
        ge=0, le=100
    )
    excellent_signal_threshold: float = Field(
        default=85, 
        description="Excellent signal threshold",
        ge=0, le=100
    )
    
    # ============================================================================
    # EXCHANGE API CONFIGURATION
    # ============================================================================
    
    # Exchange Selection
    exchange_type: str = Field(
        default="bitunix", 
        description="Exchange to use (binance, bitunix)"
    )
    
    # Bitunix API Configuration
    bitunix_api_key: str = Field(
        default="", 
        description="Bitunix API key"
    )
    bitunix_secret_key: str = Field(
        default="", 
        description="Bitunix secret key"
    )
    bitunix_sandbox: bool = Field(
        default=False, 
        description="Use Bitunix sandbox/testnet"
    )
    
    # Binance API Configuration (for backward compatibility)
    binance_api_key: str = Field(
        default="", 
        description="Binance API key"
    )
    binance_secret_key: str = Field(
        default="", 
        description="Binance secret key"
    )
    binance_sandbox: bool = Field(
        default=False, 
        description="Use Binance sandbox/testnet"
    )
    
    # General API Configuration
    api_timeout: int = Field(
        default=10000, 
        description="API timeout in milliseconds",
        ge=1000
    )
    enable_rate_limit: bool = Field(
        default=True, 
        description="Enable API rate limiting"
    )
    extended_analysis_throttle: int = Field(
        default=45, 
        description="Throttling delay for extended analysis in seconds",
        ge=1
    )
    max_retries: int = Field(
        default=3, 
        description="Maximum API retry attempts",
        ge=1
    )
    
    # ============================================================================
    # FLASK/WEB CONFIGURATION
    # ============================================================================
    flask_host: str = Field(
        default="localhost", 
        description="Flask server host"
    )
    flask_port: int = Field(
        default=5001, 
        description="Flask server port",
        ge=1, le=65535
    )
    flask_debug: bool = Field(
        default=True, 
        description="Enable Flask debug mode"
    )
    
    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================
    log_level: str = Field(
        default="INFO", 
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_file: Optional[str] = Field(
        default=None, 
        description="Log file path (optional)"
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log message format"
    )
    
    # ============================================================================
    # DEMO DATA CONFIGURATION
    # ============================================================================
    demo_mode: bool = Field(
        default=True,
        description="Enable demo mode when exchange connection fails"
    )
    demo_symbols: List[str] = Field(
        default=['BTC/USDT', 'ETH/USDT', 'BNB/USDT'],
        description="Default symbols for demo mode"
    )
    demo_base_prices: Dict[str, float] = Field(
        default={
            'BTC/USDT': 50000,
            'ETH/USDT': 3000,
            'BNB/USDT': 300
        },
        description="Base prices for demo data generation"
    )
    demo_market_movers: Dict[str, List[Dict[str, Any]]] = Field(
        default={
            'gainers': [
                {'symbol': 'BTC/USDT', 'change': 5.2, 'price': 52000, 'volume': 150000000},
                {'symbol': 'ETH/USDT', 'change': 3.8, 'price': 3100, 'volume': 80000000},
                {'symbol': 'BNB/USDT', 'change': 2.1, 'price': 310, 'volume': 25000000}
            ],
            'losers': [
                {'symbol': 'DOGE/USDT', 'change': -3.2, 'price': 0.08, 'volume': 45000000},
                {'symbol': 'ADA/USDT', 'change': -2.8, 'price': 0.45, 'volume': 30000000},
                {'symbol': 'DOT/USDT', 'change': -1.9, 'price': 6.2, 'volume': 20000000}
            ]
        },
        description="Demo market movers data"
    )
    demo_opportunities: List[Dict[str, Any]] = Field(
        default=[
            {
                'symbol': 'BTC/USDT',
                'score': 85.2,
                'signal': 'BUY',
                'timeframe': '1h',
                'price': 52000,
                'fvg_zones': 2,
                'confluence': 'HIGH'
            },
            {
                'symbol': 'ETH/USDT', 
                'score': 78.5,
                'signal': 'WATCH',
                'timeframe': '4h',
                'price': 3100,
                'fvg_zones': 1,
                'confluence': 'MEDIUM'
            }
        ],
        description="Demo trading opportunities"
    )
    
    # ============================================================================
    # ENVIRONMENT CONFIGURATION
    # ============================================================================
    environment: str = Field(
        default="development", 
        description="Environment (development, staging, production)"
    )
    
    # ============================================================================
    # PYDANTIC CONFIGURATION
    # ============================================================================
    class Config:
        env_file = ".env"
        env_prefix = "TRADING_"
        case_sensitive = False
        validate_assignment = True
        arbitrary_types_allowed = True
    
    # ============================================================================
    # VALIDATORS
    # ============================================================================
    @validator('timeframe_weights')
    def validate_timeframe_weights(cls, v):
        """Ensure timeframe weights sum to approximately 1.0"""
        total = sum(v.values())
        if not (0.95 <= total <= 1.05):  # Allow small floating point errors
            raise ValueError(f"Timeframe weights must sum to ~1.0, got {total}")
        return v
    
    @validator('scoring_weights')
    def validate_scoring_weights(cls, v):
        """Ensure scoring weights sum to approximately 1.0"""
        total = sum(v.values())
        if not (0.95 <= total <= 1.05):  # Allow small floating point errors
            raise ValueError(f"Scoring weights must sum to ~1.0, got {total}")
        return v
    
    @validator('primary_timeframe')
    def validate_primary_timeframe(cls, v, values):
        """Ensure primary timeframe is in the timeframes list"""
        timeframes = values.get('timeframes', [])
        if v not in timeframes:
            raise ValueError(f"Primary timeframe '{v}' must be in timeframes list: {timeframes}")
        return v
    
    @validator('log_level')
    def validate_log_level(cls, v):
        """Ensure log level is valid"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @validator('environment')
    def validate_environment(cls, v):
        """Ensure environment is valid"""
        valid_environments = ['development', 'staging', 'production']
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    @validator('exchange_type')
    def validate_exchange_type(cls, v):
        """Ensure exchange type is valid"""
        valid_exchanges = ['binance', 'bitunix']
        if v.lower() not in valid_exchanges:
            raise ValueError(f"Exchange type must be one of: {valid_exchanges}")
        return v.lower()
    
    # ============================================================================
    # HELPER METHODS
    # ============================================================================
    def get_cache_config(self) -> Dict[str, int]:
        """Get all cache-related configuration"""
        return {
            'ticker_cache_duration': self.ticker_cache_duration,
            'analysis_cache_duration': self.analysis_cache_duration,
            'ohlcv_cache_duration': self.ohlcv_cache_duration,
            'curated_cache_duration': self.curated_cache_duration
        }
    
    def get_market_filters(self) -> Dict[str, any]:
        """Get market data filtering configuration"""
        return {
            'min_volume_usdt': self.min_volume_usdt,
            'min_price': self.min_price,
            'max_price': self.max_price,
            'excluded_symbols': self.excluded_symbols
        }
    
    def get_analysis_config(self) -> Dict[str, any]:
        """Get technical analysis configuration"""
        return {
            'fvg_threshold': self.fvg_threshold,
            'fvg_proximity': self.fvg_proximity,
            'fvg_volume_confirm': self.fvg_volume_confirm,
            'fvg_max_age': self.fvg_max_age,
            'pattern_tolerance': self.pattern_tolerance,
            'min_pattern_periods': self.min_pattern_periods,
            'confluence_threshold': self.confluence_threshold,
            'timeframes': self.timeframes,
            'timeframe_weights': self.timeframe_weights
        }
    
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment == 'production'
    
    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.environment == 'development'
    
    def get_exchange_config(self) -> Dict[str, Any]:
        """Get exchange configuration for the selected exchange"""
        if self.exchange_type == 'bitunix':
            return {
                'exchange_type': 'bitunix',
                'api_key': self.bitunix_api_key,
                'secret_key': self.bitunix_secret_key,
                'sandbox': self.bitunix_sandbox,
                'timeout': self.api_timeout,
                'enable_rate_limit': self.enable_rate_limit
            }
        elif self.exchange_type == 'binance':
            return {
                'exchange_type': 'binance',
                'api_key': self.binance_api_key,
                'secret_key': self.binance_secret_key,
                'sandbox': self.binance_sandbox,
                'timeout': self.api_timeout,
                'enable_rate_limit': self.enable_rate_limit
            }
        else:
            raise ValueError(f"Unknown exchange type: {self.exchange_type}")

# ============================================================================
# GLOBAL SETTINGS INSTANCE
# ============================================================================
# Create global settings instance that can be imported throughout the application
settings = TradingSettings()

# Validate settings on import
try:
    # This will trigger validation
    _ = settings.dict()
    print(f"✅ Configuration loaded successfully for {settings.environment} environment")
except Exception as e:
    print(f"❌ Configuration validation failed: {e}")
    raise 