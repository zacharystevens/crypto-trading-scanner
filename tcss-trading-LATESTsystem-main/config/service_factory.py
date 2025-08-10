#!/usr/bin/env python3
"""
Service Factory for Dependency Injection
Manages service instances with shared configuration
"""

import logging
from typing import Optional, Dict, Any
from functools import lru_cache

from config.settings import settings, TradingSettings
from services.market_data_service import MarketDataService
from services.technical_analysis_service import TechnicalAnalysisService
from services.caching_service import CachingService
from services.pattern_detection_service import PatternDetectionService
from services.scoring_service import ScoringService

logger = logging.getLogger(__name__)

class ServiceFactory:
    """Factory class for creating and managing service instances"""
    
    def __init__(self, config: Optional[TradingSettings] = None):
        """Initialize service factory with configuration"""
        self.config = config or settings
        self._services: Dict[str, Any] = {}
        
        # Log configuration being used
        logger.info(f"ServiceFactory initialized for {self.config.environment} environment")
        
    @lru_cache(maxsize=1)
    def get_market_data_service(self, exchange_config: Optional[Dict] = None) -> MarketDataService:
        """Get or create MarketDataService instance"""
        if 'market_data' not in self._services:
            logger.info("Creating MarketDataService instance")
            self._services['market_data'] = MarketDataService(
                exchange_config=exchange_config,
                config=self.config
            )
        return self._services['market_data']
    
    @lru_cache(maxsize=1)
    def get_technical_analysis_service(self) -> TechnicalAnalysisService:
        """Get or create TechnicalAnalysisService instance"""
        if 'technical_analysis' not in self._services:
            logger.info("Creating TechnicalAnalysisService instance")
            self._services['technical_analysis'] = TechnicalAnalysisService(config=self.config)
        return self._services['technical_analysis']
    
    @lru_cache(maxsize=1)
    def get_caching_service(self) -> CachingService:
        """Get or create CachingService instance"""
        if 'caching' not in self._services:
            logger.info("Creating CachingService instance")
            self._services['caching'] = CachingService(config=self.config)
        return self._services['caching']
    
    @lru_cache(maxsize=1)
    def get_pattern_detection_service(self) -> PatternDetectionService:
        """Get or create PatternDetectionService instance"""
        if 'pattern_detection' not in self._services:
            logger.info("Creating PatternDetectionService instance")
            self._services['pattern_detection'] = PatternDetectionService(config=self.config)
        return self._services['pattern_detection']
    
    @lru_cache(maxsize=1)
    def get_scoring_service(self) -> ScoringService:
        """Get or create ScoringService instance"""
        if 'scoring' not in self._services:
            logger.info("Creating ScoringService instance")
            self._services['scoring'] = ScoringService(config=self.config)
        return self._services['scoring']
    
    def get_all_services(self) -> Dict[str, Any]:
        """Get all service instances"""
        return {
            'market_data': self.get_market_data_service(),
            'technical_analysis': self.get_technical_analysis_service(),
            'caching': self.get_caching_service(),
            'pattern_detection': self.get_pattern_detection_service(),
            'scoring': self.get_scoring_service()
        }
    
    def reset_services(self):
        """Reset all service instances (useful for testing)"""
        logger.info("Resetting all service instances")
        self._services.clear()
        # Clear the LRU cache
        self.get_market_data_service.cache_clear()
        self.get_technical_analysis_service.cache_clear()
        self.get_caching_service.cache_clear()
        self.get_pattern_detection_service.cache_clear()
        self.get_scoring_service.cache_clear()
    
    def get_service_status(self) -> Dict[str, bool]:
        """Get status of all services"""
        return {
            service_name: service_name in self._services
            for service_name in ['market_data', 'technical_analysis', 'caching', 'pattern_detection', 'scoring']
        }
    
    def configure_logging(self):
        """Configure logging based on settings"""
        log_level = getattr(logging, self.config.log_level.upper())
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format=self.config.log_format,
            handlers=[]
        )
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        formatter = logging.Formatter(self.config.log_format)
        console_handler.setFormatter(formatter)
        logging.getLogger().addHandler(console_handler)
        
        # Add file handler if specified
        if self.config.log_file:
            try:
                file_handler = logging.FileHandler(self.config.log_file)
                file_handler.setLevel(log_level)
                file_handler.setFormatter(formatter)
                logging.getLogger().addHandler(file_handler)
                logger.info(f"Logging to file: {self.config.log_file}")
            except Exception as e:
                logger.warning(f"Could not create log file {self.config.log_file}: {e}")
        
        logger.info(f"Logging configured at {self.config.log_level} level")
        

class TradingSystemContainer:
    """Main container for the trading system with all dependencies"""
    
    def __init__(self, config: Optional[TradingSettings] = None):
        """Initialize the trading system container"""
        self.config = config or settings
        self.service_factory = ServiceFactory(self.config)
        
        # Configure logging
        self.service_factory.configure_logging()
        
        logger.info("TradingSystemContainer initialized")
        logger.info(f"Environment: {self.config.environment}")
        logger.info(f"Configuration loaded with {len(self.config.timeframes)} timeframes")
    
    @property
    def market_data(self) -> MarketDataService:
        """Access to market data service"""
        return self.service_factory.get_market_data_service()
    
    @property
    def technical_analysis(self) -> TechnicalAnalysisService:
        """Access to technical analysis service"""
        return self.service_factory.get_technical_analysis_service()
    
    @property
    def caching(self) -> CachingService:
        """Access to caching service"""
        return self.service_factory.get_caching_service()
    
    @property
    def pattern_detection(self) -> PatternDetectionService:
        """Access to pattern detection service"""
        return self.service_factory.get_pattern_detection_service()
    
    @property
    def scoring(self) -> ScoringService:
        """Access to scoring service"""
        return self.service_factory.get_scoring_service()
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'environment': self.config.environment,
            'services': self.service_factory.get_service_status(),
            'configuration': {
                'timeframes': self.config.timeframes,
                'primary_timeframe': self.config.primary_timeframe,
                'min_volume_usdt': self.config.min_volume_usdt,
                'cache_durations': self.config.get_cache_config()
            }
        }
    
    def reset(self):
        """Reset the entire system (useful for testing)"""
        logger.info("Resetting trading system container")
        self.service_factory.reset_services()


# ============================================================================
# GLOBAL CONTAINER INSTANCE
# ============================================================================
# Global container instance for easy access throughout the application
trading_system = TradingSystemContainer()

# Convenience functions for accessing services
def get_market_data_service() -> MarketDataService:
    """Get the global market data service instance"""
    return trading_system.market_data

def get_technical_analysis_service() -> TechnicalAnalysisService:
    """Get the global technical analysis service instance"""
    return trading_system.technical_analysis

def get_caching_service() -> CachingService:
    """Get the global caching service instance"""
    return trading_system.caching

def get_pattern_detection_service() -> PatternDetectionService:
    """Get the global pattern detection service instance"""
    return trading_system.pattern_detection

def get_scoring_service() -> ScoringService:
    """Get the global scoring service instance"""
    return trading_system.scoring 