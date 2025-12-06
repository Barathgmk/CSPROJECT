"""
simple_ml.py

Simple machine learning for stock price prediction.
Uses moving averages, trend analysis, and basic regression.

Not for real trading - educational demo only.

Classes:
  - SimpleStockPredictor: ML predictor using moving averages and regression

Key Methods:
  - predict_next_price(): Predict tomorrow's price with confidence
  - classify_signal(): Generate trading signals (BUY/SELL/HOLD)
  - calculate_risk_reward(): Calculate risk/reward ratio for a trade

Indicators Used:
  - Moving Averages (MA5, MA10, MA20): Trend detection
  - Momentum: Rate of price change
  - Volatility: Price standard deviation
  - Linear Regression: Trend fitting
  - Support/Resistance: Key price levels
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
import pandas as pd


class SimpleStockPredictor:
    """
    Simple ML-based stock price predictor.
    
    Uses technical analysis indicators:
    - Moving averages (trend detection)
    - Momentum (rate of change / velocity)
    - Volatility analysis (price variance)
    - Linear trend fitting (direction prediction)
    
    Example:
      predictor = SimpleStockPredictor(lookback_days=20)
      prices = [2.50, 2.55, 2.60, 2.62, 2.58, ...]
      result = predictor.predict_next_price(prices, current_price=2.65)
      print(result["predicted_price"])  # Tomorrow's predicted price
      print(result["confidence"])  # How confident (0-1)
      print(result["trend"])  # "up" or "down"
    """
    
    def __init__(self, lookback_days: int = 20):
        """
        Initialize predictor.
        
        Args:
          lookback_days: Number of historical days to analyze (default 20)
        """
        self.lookback_days = lookback_days
    
    def predict_next_price(
        self,
        prices: List[float],
        current_price: float
    ) -> Dict[str, float]:
        """
        Predict next price using moving averages and linear regression.
        
        Algorithm:
          1. Calculate 5, 10, 20 day moving averages
          2. Calculate momentum (short-term velocity)
          3. Calculate volatility (price variance)
          4. Fit linear regression to get trend direction
          5. Combine all signals for prediction
          6. Calculate confidence based on trend strength
        
        Args:
          prices: List of recent prices (oldest to newest)
          current_price: Most recent closing price
        
        Returns:
          Dict with keys:
            - predicted_price: Tomorrow's expected price
            - confidence: 0-1 (how confident in prediction)
            - trend: "up", "down", or "neutral"
            - momentum: -1 to +1 (velocity of change)
            - volatility: Percentage price fluctuation
            - support: Estimated price floor
            - resistance: Estimated price ceiling
        """
        if not prices or len(prices) < 3:
            return {
                "predicted_price": current_price,
                "confidence": 0.0,
                "trend": "neutral",
                "momentum": 0.0,
                "volatility": 0.0,
                "support": current_price * 0.95,
                "resistance": current_price * 1.05,
            }
        
        prices = list(prices[-self.lookback_days:])  # Use recent data
        
        # 1. Calculate moving averages
        ma5 = np.mean(prices[-5:]) if len(prices) >= 5 else np.mean(prices)
        ma10 = np.mean(prices[-10:]) if len(prices) >= 10 else np.mean(prices)
        ma20 = np.mean(prices) if len(prices) >= 20 else np.mean(prices)
        
        # 2. Detect trend
        if ma5 > ma10 > ma20:
            trend = "up"
            trend_strength = 1.0
        elif ma5 < ma10 < ma20:
            trend = "down"
            trend_strength = -1.0
        else:
            trend = "neutral"
            trend_strength = 0.0
        
        # 3. Calculate momentum (velocity of price change)
        recent_change = (prices[-1] - prices[-5]) / prices[-5] if len(prices) >= 5 else 0
        momentum = np.tanh(recent_change * 10)  # Normalize to -1,1
        
        # 4. Calculate volatility
        returns = np.diff(prices) / prices[:-1] if len(prices) > 1 else [0]
        volatility = float(np.std(returns)) * 100 if len(returns) > 0 else 0
        
        # 5. Linear trend (simple regression)
        x = np.arange(len(prices))
        if len(prices) > 1:
            # Simple linear fit
            coef = np.polyfit(x, prices, 1)
            slope = coef[0]
            next_price = prices[-1] + slope
        else:
            next_price = prices[-1]
        
        # 6. Support and resistance (recent highs/lows)
        recent_high = max(prices[-10:]) if len(prices) >= 10 else max(prices)
        recent_low = min(prices[-10:]) if len(prices) >= 10 else min(prices)
        support = recent_low * 0.98
        resistance = recent_high * 1.02
        
        # 7. Confidence score (0-1)
        # Higher confidence with:
        # - Strong trend (abs trend_strength)
        # - Low volatility
        # - Consistent momentum
        trend_score = abs(trend_strength)
        volatility_score = max(0, 1 - volatility / 5)  # Lower vol = higher confidence
        momentum_score = abs(momentum)
        
        confidence = (trend_score * 0.4 + volatility_score * 0.3 + momentum_score * 0.3)
        confidence = min(1.0, max(0.0, confidence))
        
        # 8. Final predicted price (weighted)
        # Use MA-based prediction and trend-based prediction
        ma_prediction = ma5 * 0.7 + ma10 * 0.3
        trend_prediction = prices[-1] * (1 + trend_strength * 0.02)
        
        final_prediction = (ma_prediction * 0.6 + trend_prediction * 0.4)
        final_prediction = max(0.01, final_prediction)  # Don't predict negative
        
        return {
            "predicted_price": round(final_prediction, 2),
            "confidence": round(confidence, 2),
            "trend": trend,
            "momentum": round(momentum, 2),
            "volatility": round(volatility, 2),
            "support": round(support, 2),
            "resistance": round(resistance, 2),
        }
    
    def classify_signal(self, prediction: Dict[str, float]) -> str:
        """
        Convert prediction to trading signal
        
        Returns: "BUY", "SELL", or "HOLD"
        """
        trend = prediction["trend"]
        confidence = prediction["confidence"]
        momentum = prediction["momentum"]
        
        # BUY: uptrend with good confidence and positive momentum
        if trend == "up" and confidence > 0.5 and momentum > 0.1:
            return "STRONG_BUY"
        elif trend == "up" and confidence > 0.3:
            return "BUY"
        
        # SELL: downtrend with good confidence and negative momentum
        elif trend == "down" and confidence > 0.5 and momentum < -0.1:
            return "STRONG_SELL"
        elif trend == "down" and confidence > 0.3:
            return "SELL"
        
        # HOLD: neutral or low confidence
        else:
            return "HOLD"
    
    def calculate_risk_reward(
        self,
        current_price: float,
        prediction: Dict[str, float],
        risk_percent: float = 0.05
    ) -> Dict[str, float]:
        """
        Calculate potential risk/reward from current price to prediction
        """
        predicted_price = prediction["predicted_price"]
        support = prediction["support"]
        resistance = prediction["resistance"]
        
        # Risk: distance to support
        risk_price = support
        risk_dollars = current_price - risk_price
        risk_pct = (risk_dollars / current_price * 100) if current_price > 0 else 0
        
        # Reward: distance to predicted price (or resistance)
        reward_price = max(predicted_price, current_price * 1.02)
        reward_dollars = reward_price - current_price
        reward_pct = (reward_dollars / current_price * 100) if current_price > 0 else 0
        
        # Risk/Reward ratio
        rr_ratio = (reward_dollars / risk_dollars) if risk_dollars > 0 else 0
        
        return {
            "entry_price": current_price,
            "stop_loss": risk_price,
            "target_price": reward_price,
            "risk_dollars": round(risk_dollars, 2),
            "risk_percent": round(risk_pct, 2),
            "reward_dollars": round(reward_dollars, 2),
            "reward_percent": round(reward_pct, 2),
            "risk_reward_ratio": round(rr_ratio, 2),
        }


def generate_synthetic_prices(
    starting_price: float,
    num_days: int = 20,
    volatility: float = 0.02,
    drift: float = 0.001
) -> List[float]:
    """
    Generate synthetic price data (for testing)
    
    Uses geometric Brownian motion
    """
    prices = [starting_price]
    for _ in range(num_days):
        change = np.random.normal(drift, volatility)
        new_price = prices[-1] * (1 + change)
        new_price = max(new_price, 0.01)  # Don't go negative
        prices.append(new_price)
    
    return prices


def create_sample_predictions() -> Dict[str, Dict]:
    """
    Create sample predictions for multiple stocks (for demo)
    """
    predictor = SimpleStockPredictor()
    
    # Sample tickers with synthetic price history
    samples = {
        "ABCD": {
            "prices": generate_synthetic_prices(3.50, num_days=20, volatility=0.03),
            "current_price": 3.65,
            "mentions": 45,
            "sentiment": 0.72,
        },
        "WXYZ": {
            "prices": generate_synthetic_prices(2.10, num_days=20, volatility=0.04),
            "current_price": 2.15,
            "mentions": 38,
            "sentiment": 0.65,
        },
        "TECH": {
            "prices": generate_synthetic_prices(4.80, num_days=20, volatility=0.02),
            "current_price": 4.95,
            "mentions": 52,
            "sentiment": 0.80,
        },
    }
    
    predictions = {}
    for ticker, data in samples.items():
        pred = predictor.predict_next_price(data["prices"], data["current_price"])
        signal = predictor.classify_signal(pred)
        risk_reward = predictor.calculate_risk_reward(data["current_price"], pred)
        
        predictions[ticker] = {
            "ticker": ticker,
            "current_price": data["current_price"],
            "mentions": data["mentions"],
            "sentiment": data["sentiment"],
            "prediction": pred,
            "signal": signal,
            "risk_reward": risk_reward,
        }
    
    return predictions


# Test function
if __name__ == "__main__":
    predictor = SimpleStockPredictor()
    
    # Generate sample data
    prices = generate_synthetic_prices(3.50, num_days=20)
    
    # Make prediction
    pred = predictor.predict_next_price(prices, 3.65)
    signal = predictor.classify_signal(pred)
    risk_reward = predictor.calculate_risk_reward(3.65, pred)
    
    print("Price History:", [f"${p:.2f}" for p in prices[-5:]])
    print("\nPrediction:")
    print(f"  Next Price: ${pred['predicted_price']:.2f}")
    print(f"  Confidence: {pred['confidence']:.1%}")
    print(f"  Trend: {pred['trend']}")
    print(f"  Momentum: {pred['momentum']:.2f}")
    print(f"\nSignal: {signal}")
    print(f"\nRisk/Reward:")
    print(f"  Stop Loss: ${risk_reward['stop_loss']:.2f}")
    print(f"  Target: ${risk_reward['target_price']:.2f}")
    print(f"  R/R Ratio: {risk_reward['risk_reward_ratio']:.2f}:1")
