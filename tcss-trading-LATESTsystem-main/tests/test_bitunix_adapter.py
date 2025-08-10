#!/usr/bin/env python3
"""
Tests for Bitunix Exchange Adapter
Comprehensive test suite for the new Bitunix API integration
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from services.exchanges.bitunix_adapter import BitunixAdapter
from services.exchange_interface import ExchangeConfig, ExchangeType, Ticker, OHLCV

class TestBitunixAdapter:
    """Test suite for BitunixAdapter"""
    
    @pytest.fixture
    def config(self):
        """Create test configuration"""
        return ExchangeConfig(
            api_key="test_api_key",
            secret_key="test_secret_key",
            sandbox=True,
            timeout=5000
        )
    
    @pytest.fixture
    def adapter(self, config):
        """Create BitunixAdapter instance"""
        return BitunixAdapter(config)
    
    def test_adapter_initialization(self, adapter):
        """Test adapter initialization"""
        assert adapter._exchange_type == ExchangeType.BITUNIX
        assert not adapter.is_connected
        assert adapter.public_client is None
        assert adapter.private_client is None
    
    @pytest.mark.asyncio
    async def test_connection_success(self, adapter):
        """Test successful connection"""
        with patch.object(adapter, '_create_bitunix_config') as mock_config, \
             patch.object(adapter, '_test_connection') as mock_test:
            
            mock_config.return_value = Mock()
            mock_test.return_value = None
            
            # Mock the OpenApiHttpFuturePublic creation
            with patch('services.exchanges.bitunix_adapter.OpenApiHttpFuturePublic') as mock_public:
                mock_public.return_value = Mock()
                
                result = await adapter.connect()
                
                assert result is True
                assert adapter.is_connected
                assert adapter.public_client is not None
    
    @pytest.mark.asyncio
    async def test_connection_failure(self, adapter):
        """Test connection failure"""
        with patch.object(adapter, '_create_bitunix_config') as mock_config:
            mock_config.side_effect = Exception("Connection failed")
            
            result = await adapter.connect()
            
            assert result is False
            assert not adapter.is_connected
    
    @pytest.mark.asyncio
    async def test_get_tickers_success(self, adapter):
        """Test successful ticker fetching"""
        # Setup
        adapter._connected = True
        adapter.public_client = Mock()
        
        mock_response = [
            {
                'symbol': 'BTCUSDT',
                'close': '50000',
                'priceChangePercent': '2.5',
                'volume': '1000000',
                'high': '51000',
                'low': '49000',
                'timestamp': 1640995200000
            }
        ]
        adapter.public_client.get_tickers.return_value = mock_response
        
        # Execute
        tickers = await adapter.get_tickers(['BTC/USDT'])
        
        # Verify
        assert len(tickers) == 1
        ticker = tickers[0]
        assert ticker.symbol == 'BTC/USDT'
        assert ticker.price == 50000.0
        assert ticker.change_24h == 2.5
    
    @pytest.mark.asyncio
    async def test_get_tickers_not_connected(self, adapter):
        """Test ticker fetching when not connected"""
        adapter._connected = False
        
        with pytest.raises(ConnectionError):
            await adapter.get_tickers(['BTC/USDT'])
    
    @pytest.mark.asyncio
    async def test_get_ohlcv_success(self, adapter):
        """Test successful OHLCV fetching"""
        # Setup
        adapter._connected = True
        adapter.public_client = Mock()
        
        mock_response = {
            'data': [
                [1640995200000, '49000', '51000', '48000', '50000', '1000'],
                [1640998800000, '50000', '52000', '49500', '51000', '1100']
            ]
        }
        adapter.public_client.get_kline.return_value = mock_response
        
        # Execute
        ohlcv_data = await adapter.get_ohlcv('BTC/USDT', '1h', 2)
        
        # Verify
        assert len(ohlcv_data) == 2
        candle = ohlcv_data[0]
        assert candle.timestamp == 1640995200000
        assert candle.open == 49000.0
        assert candle.close == 50000.0
    
    @pytest.mark.asyncio
    async def test_get_markets_success(self, adapter):
        """Test successful markets fetching"""
        # Setup
        adapter._connected = True
        adapter.public_client = Mock()
        
        mock_response = [
            {
                'symbol': 'BTCUSDT',
                'baseCoin': 'BTC',
                'quoteCoin': 'USDT',
                'status': 'TRADING',
                'minOrderQty': '0.001',
                'maxOrderQty': '1000',
                'pricePrecision': '2',
                'quantityPrecision': '8'
            }
        ]
        adapter.public_client.get_trading_pairs.return_value = mock_response
        
        # Execute
        markets = await adapter.get_markets()
        
        # Verify
        assert len(markets) == 1
        market = markets[0]
        assert market['symbol'] == 'BTC/USDT'
        assert market['base'] == 'BTC'
        assert market['quote'] == 'USDT'
        assert market['active'] is True
    
    def test_format_symbol_conversion(self, adapter):
        """Test symbol format conversion methods"""
        # Standard to Bitunix
        assert adapter._format_symbol_to_bitunix('BTC/USDT') == 'BTCUSDT'
        assert adapter._format_symbol_to_bitunix('BTCUSDT') == 'BTCUSDT'
        
        # Bitunix to standard
        assert adapter._format_symbol_to_standard('BTCUSDT') == 'BTC/USDT'
        assert adapter._format_symbol_to_standard('ETHUSDT') == 'ETH/USDT'
        assert adapter._format_symbol_to_standard('') == ''

@pytest.mark.integration
class TestBitunixIntegration:
    """Integration tests for Bitunix adapter (requires real API keys)"""
    
    @pytest.mark.asyncio
    async def test_real_connection(self):
        """Test real connection to Bitunix (requires API keys)"""
        import os
        
        api_key = os.getenv('TRADING_BITUNIX_API_KEY')
        secret_key = os.getenv('TRADING_BITUNIX_SECRET_KEY')
        
        if not api_key or not secret_key:
            pytest.skip("API keys not available for integration test")
        
        config = ExchangeConfig(
            api_key=api_key,
            secret_key=secret_key,
            sandbox=True
        )
        
        adapter = BitunixAdapter(config)
        
        try:
            connected = await adapter.connect()
            assert connected is True
            
            # Test basic data fetching
            tickers = await adapter.get_tickers(['BTC/USDT'])
            assert len(tickers) > 0
            
        finally:
            await adapter.disconnect()

if __name__ == "__main__":
    pytest.main([__file__]) 