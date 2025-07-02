#!/usr/bin/env python3
"""
Exchange Factory - Creates appropriate exchange adapter based on configuration
Supports multiple exchanges with standardized interface
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from .exchange_interface import ExchangeInterface, ExchangeConfig, ExchangeType
from .exchanges.binance_adapter import BinanceAdapter
from .exchanges.bitunix_adapter import BitunixAdapter

logger = logging.getLogger(__name__)

class ExchangeFactory:
    """Factory class for creating exchange adapters"""
    
    _exchange_registry = {
        ExchangeType.BINANCE: BinanceAdapter,
        ExchangeType.BITUNIX: BitunixAdapter,
    }
    
    @classmethod
    def create_exchange(cls, exchange_type: ExchangeType, config: ExchangeConfig) -> ExchangeInterface:
        """
        Create an exchange adapter instance
        
        Args:
            exchange_type: Type of exchange to create
            config: Exchange configuration
            
        Returns:
            ExchangeInterface: Exchange adapter instance
            
        Raises:
            ValueError: If exchange type is not supported
        """
        if exchange_type not in cls._exchange_registry:
            available_exchanges = list(cls._exchange_registry.keys())
            raise ValueError(f"Exchange type {exchange_type} not supported. Available: {available_exchanges}")
        
        adapter_class = cls._exchange_registry[exchange_type]
        
        try:
            adapter = adapter_class(config)
            logger.info(f"Created {exchange_type.value} exchange adapter")
            return adapter
        except Exception as e:
            logger.error(f"Failed to create {exchange_type.value} adapter: {e}")
            raise
    
    @classmethod
    def create_from_settings(cls, settings: Dict[str, Any]) -> ExchangeInterface:
        """
        Create exchange adapter from settings dictionary
        
        Args:
            settings: Dictionary containing exchange configuration
            
        Returns:
            ExchangeInterface: Exchange adapter instance
        """
        # Extract exchange type
        exchange_name = settings.get('exchange_type', 'binance').lower()
        
        try:
            exchange_type = ExchangeType(exchange_name)
        except ValueError:
            logger.warning(f"Unknown exchange type '{exchange_name}', defaulting to Binance")
            exchange_type = ExchangeType.BINANCE
        
        # Create exchange configuration
        config = ExchangeConfig(
            api_key=settings.get('api_key', ''),
            secret_key=settings.get('secret_key', ''),
            sandbox=settings.get('sandbox', False),
            timeout=settings.get('timeout', 10000),
            enable_rate_limit=settings.get('enable_rate_limit', True),
            extra_params=settings.get('extra_params', {})
        )
        
        return cls.create_exchange(exchange_type, config)
    
    @classmethod
    def get_supported_exchanges(cls) -> list[ExchangeType]:
        """Get list of supported exchange types"""
        return list(cls._exchange_registry.keys())
    
    @classmethod
    def register_exchange(cls, exchange_type: ExchangeType, adapter_class: type) -> None:
        """
        Register a new exchange adapter
        
        Args:
            exchange_type: Exchange type identifier
            adapter_class: Adapter class that implements ExchangeInterface
        """
        if not issubclass(adapter_class, ExchangeInterface):
            raise ValueError(f"Adapter class must implement ExchangeInterface")
        
        cls._exchange_registry[exchange_type] = adapter_class
        logger.info(f"Registered {exchange_type.value} exchange adapter")

# Convenience functions for common exchange creation
def create_binance_exchange(api_key: str = "", secret_key: str = "", sandbox: bool = False) -> ExchangeInterface:
    """Create Binance exchange adapter with simplified parameters"""
    config = ExchangeConfig(
        api_key=api_key,
        secret_key=secret_key,
        sandbox=sandbox
    )
    return ExchangeFactory.create_exchange(ExchangeType.BINANCE, config)

def create_bitunix_exchange(api_key: str, secret_key: str, sandbox: bool = False) -> ExchangeInterface:
    """Create Bitunix exchange adapter with simplified parameters"""
    config = ExchangeConfig(
        api_key=api_key,
        secret_key=secret_key,
        sandbox=sandbox
    )
    return ExchangeFactory.create_exchange(ExchangeType.BITUNIX, config) 