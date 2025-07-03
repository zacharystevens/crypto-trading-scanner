#!/usr/bin/env python3
"""
Exchange Interface - Abstract base class for all exchange implementations
Provides standardized interface for different exchange APIs
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import pandas as pd
from dataclasses import dataclass
from enum import Enum

class ExchangeType(Enum):
    """Supported exchange types"""
    BINANCE = "binance"
    BITUNIX = "bitunix"

@dataclass
class ExchangeConfig:
    """Configuration for exchange connection"""
    api_key: str
    secret_key: str
    sandbox: bool = False
    timeout: int = 10000
    enable_rate_limit: bool = True
    extra_params: Dict[str, Any] = None

@dataclass
class Ticker:
    """Standardized ticker data structure"""
    symbol: str
    price: float
    change_24h: float
    volume_24h: float
    high_24h: float
    low_24h: float
    timestamp: int

@dataclass
class OHLCV:
    """Standardized OHLCV data structure"""
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float

class ExchangeInterface(ABC):
    """Abstract interface for exchange implementations"""
    
    def __init__(self, config: ExchangeConfig):
        self.config = config
        self._connected = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection to exchange"""
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection to exchange"""
        pass
    
    @abstractmethod
    async def get_tickers(self, symbols: Optional[List[str]] = None) -> List[Ticker]:
        """Get ticker data for symbols"""
        pass
    
    @abstractmethod
    async def get_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List[OHLCV]:
        """Get OHLCV data for symbol"""
        pass
    
    @abstractmethod
    async def get_markets(self) -> List[Dict[str, Any]]:
        """Get available markets/trading pairs"""
        pass
    
    @abstractmethod
    async def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get detailed information about a symbol"""
        pass
    
    @property
    def is_connected(self) -> bool:
        """Check if exchange is connected"""
        return self._connected
    
    @property
    def exchange_type(self) -> ExchangeType:
        """Get exchange type"""
        return self._exchange_type 