"""
Stock Trend Predictor AI.
Implements a custom Logistic Regression classifier from scratch using NumPy.
Trains on market features using batch gradient descent and Binary Cross-Entropy Loss.
"""

import numpy as np

class LogisticRegression:
    def __init__(self, learning_rate=0.05, iterations=1000):
        """Initializes hyperparameters for logistic regression."""
        self.learning_rate = learning_rate
        self.iterations = iterations
        self.weights = None
        self.bias = 0.0

    def sigmoid(self, z):
        """
        Computes the sigmoid activation function.
        
        Formula:
            sigmoid(z) = 1 / (1 + e^-z)
            
        Math Explanation:
            - Maps any real number z to a value in the interval [0, 1].
            - np.clip prevents float overflow when z is large negative.
        """
        return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

    def compute_loss(self, y, y_pred):
        """
        Computes Binary Cross-Entropy Loss.
        
        Formula:
            Loss = -1/N * sum(y * log(y_pred) + (1 - y) * log(1 - y_pred))
            
        Math Explanation:
            - Measures error of predictions y_pred against actual binary labels y.
            - Uses epsilon clamping to avoid log(0) which would yield undefined.
        """
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1.0 - epsilon)
        return -np.mean(y * np.log(y_pred) + (1.0 - y) * np.log(1.0 - y_pred))

    def fit(self, X, y):
        """
        Trains the logistic regression model using batch gradient descent.
        
        Math Explanation:
            - Linear combination: z = X * w + b
            - Prediction: y_pred = sigmoid(z)
            - Gradients:
                dw = (1/N) * X^T * (y_pred - y)
                db = (1/N) * sum(y_pred - y)
            - Weights & bias are updated in the direction opposing the gradient.
        """
        num_samples, num_features = X.shape
        self.weights = np.zeros(num_features)
        self.bias = 0.0
        
        for _ in range(self.iterations):
            linear_model = np.dot(X, self.weights) + self.bias
            y_pred = self.sigmoid(linear_model)
            
            dw = np.dot(X.T, (y_pred - y)) / num_samples
            db = np.sum(y_pred - y) / num_samples
            
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db

    def predict_probability(self, X):
        """Predicts probability of class 1 (Up) for input X."""
        linear_model = np.dot(X, self.weights) + self.bias
        return self.sigmoid(linear_model)

    def predict_trend(self, features):
        """
        Classifies trend as Up, Down, or Neutral using probability thresholds.
        
        Threshold Rules:
            - P >= 0.60: Up (bullish)
            - P <= 0.40: Down (bearish)
            - 0.40 < P < 0.60: Neutral (range-bound)
            
        Math Explanation:
            - For Up: Confidence is P.
            - For Down: Confidence is 1 - P.
            - For Neutral: Confidence increases as P approaches 0.5.
        """
        p = float(self.predict_probability(features))
        if p >= 0.60:
            return "Up", p * 100.0
        elif p <= 0.40:
            return "Down", (1.0 - p) * 100.0
        else:
            neutral_confidence = (1.0 - 2.0 * abs(p - 0.5)) * 100.0
            return "Neutral", neutral_confidence

def generate_synthetic_training_data(num_samples=200):
    """
    Generates deterministic synthetic training data with a known trend rule.
    
    Features:
        0. Volatility
        1. P/E Ratio
        2. Recent Price Change
        3. Volume Trend
        4. Distance from 52w High
    """
    np.random.seed(42)
    X = np.random.uniform(0.0, 1.0, (num_samples, 5))
    
    # Mathematical rule to assign labels:
    # High price change (+), high volume trend (+), low PE (-), and low volatility (-) predict Up (1).
    linear_part = 2.5 * X[:, 2] + 1.5 * X[:, 3] - 2.0 * X[:, 1] - 1.0 * X[:, 0] - 0.5 * X[:, 4]
    p_true = 1.0 / (1.0 + np.exp(-linear_part))
    y = (p_true > 0.5).astype(int)
    
    return X, y

def get_prediction(stock_features, X_train, y_train):
    """Fits model on training data and predicts trend for given stock features."""
    model = LogisticRegression(learning_rate=0.1, iterations=1500)
    model.fit(X_train, y_train)
    trend, confidence = model.predict_trend(stock_features)
    return trend, round(confidence, 2)
