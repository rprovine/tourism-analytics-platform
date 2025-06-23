import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
import warnings
from app.core.config import settings
import logging

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class DemandForecaster:
    def __init__(self):
        self.models = {
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'linear_regression': LinearRegression()
        }
        self.scalers = {}
        self.label_encoders = {}
        self.feature_columns = []
        self.is_trained = False
        self.model_performance = {}
        
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for training/prediction
        """
        df_processed = df.copy()
        
        # Convert date to datetime if it's not already
        if 'date' in df_processed.columns:
            df_processed['date'] = pd.to_datetime(df_processed['date'])
            
            # Extract time-based features
            df_processed['year'] = df_processed['date'].dt.year
            df_processed['month'] = df_processed['date'].dt.month
            df_processed['day'] = df_processed['date'].dt.day
            df_processed['day_of_week'] = df_processed['date'].dt.dayofweek
            df_processed['day_of_year'] = df_processed['date'].dt.dayofyear
            df_processed['week_of_year'] = df_processed['date'].dt.isocalendar().week
            df_processed['quarter'] = df_processed['date'].dt.quarter
            
            # Seasonal features
            df_processed['is_summer'] = df_processed['month'].isin([6, 7, 8]).astype(int)
            df_processed['is_winter'] = df_processed['month'].isin([12, 1, 2]).astype(int)
            df_processed['is_spring'] = df_processed['month'].isin([3, 4, 5]).astype(int)
            df_processed['is_fall'] = df_processed['month'].isin([9, 10, 11]).astype(int)
        
        # Lag features (previous periods)
        if 'visitor_count' in df_processed.columns:
            df_processed = df_processed.sort_values('date')
            df_processed['visitor_count_lag_1'] = df_processed['visitor_count'].shift(1)
            df_processed['visitor_count_lag_7'] = df_processed['visitor_count'].shift(7)
            df_processed['visitor_count_lag_30'] = df_processed['visitor_count'].shift(30)
            
            # Rolling averages
            df_processed['visitor_count_ma_7'] = df_processed['visitor_count'].rolling(window=7).mean()
            df_processed['visitor_count_ma_30'] = df_processed['visitor_count'].rolling(window=30).mean()
        
        # Fill missing values
        numeric_columns = df_processed.select_dtypes(include=[np.number]).columns
        df_processed[numeric_columns] = df_processed[numeric_columns].fillna(0)
        
        # Encode categorical variables
        categorical_columns = ['source_market', 'weather_condition', 'special_event']
        for col in categorical_columns:
            if col in df_processed.columns:
                if col not in self.label_encoders:
                    self.label_encoders[col] = LabelEncoder()
                    # Fit on all unique values including NaN
                    unique_values = df_processed[col].fillna('unknown').unique()
                    self.label_encoders[col].fit(unique_values)
                
                df_processed[col] = df_processed[col].fillna('unknown')
                df_processed[col] = self.label_encoders[col].transform(df_processed[col])
        
        return df_processed
    
    def train(self, training_data: List[Dict]) -> Dict:
        """
        Train forecasting models with historical data
        """
        try:
            # Convert to DataFrame
            df = pd.DataFrame(training_data)
            
            if df.empty:
                raise ValueError("No training data provided")
            
            # Prepare features
            df_processed = self.prepare_features(df)
            
            # Define target and feature columns
            target_col = 'visitor_count'
            exclude_cols = ['id', 'business_id', 'date', 'created_at', 'updated_at', target_col]
            self.feature_columns = [col for col in df_processed.columns if col not in exclude_cols]
            
            # Remove rows with NaN in target
            df_processed = df_processed.dropna(subset=[target_col])
            
            if df_processed.empty:
                raise ValueError("No valid training data after preprocessing")
            
            X = df_processed[self.feature_columns]
            y = df_processed[target_col]
            
            # Scale features
            self.scalers['features'] = StandardScaler()
            X_scaled = self.scalers['features'].fit_transform(X)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y, test_size=0.2, random_state=42
            )
            
            # Train models
            self.model_performance = {}
            
            for model_name, model in self.models.items():
                # Train model
                model.fit(X_train, y_train)
                
                # Evaluate model
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                mae = mean_absolute_error(y_test, y_pred)
                mse = mean_squared_error(y_test, y_pred)
                rmse = np.sqrt(mse)
                r2 = r2_score(y_test, y_pred)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='neg_mean_absolute_error')
                cv_mae = -cv_scores.mean()
                
                self.model_performance[model_name] = {
                    'mae': mae,
                    'mse': mse,
                    'rmse': rmse,
                    'r2': r2,
                    'cv_mae': cv_mae
                }
            
            self.is_trained = True
            
            # Save models
            self._save_models()
            
            return {
                'status': 'success',
                'models_trained': len(self.models),
                'performance': self.model_performance,
                'best_model': min(self.model_performance.items(), key=lambda x: x[1]['mae'])[0],
                'training_samples': len(df_processed)
            }
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def predict(self, input_data: List[Dict], model_name: str = 'random_forest') -> Dict:
        """
        Make predictions using trained model
        """
        try:
            if not self.is_trained:
                self._load_models()
            
            if not self.is_trained:
                raise ValueError("Models not trained. Please train first.")
            
            # Convert to DataFrame
            df = pd.DataFrame(input_data)
            
            # Prepare features
            df_processed = self.prepare_features(df)
            
            # Get features
            X = df_processed[self.feature_columns]
            X_scaled = self.scalers['features'].transform(X)
            
            # Make predictions
            model = self.models[model_name]
            predictions = model.predict(X_scaled)
            
            # Calculate confidence intervals (approximate)
            if hasattr(model, 'estimators_'):  # For ensemble methods
                individual_preds = np.array([tree.predict(X_scaled) for tree in model.estimators_])
                std_pred = np.std(individual_preds, axis=0)
                confidence_lower = predictions - 1.96 * std_pred
                confidence_upper = predictions + 1.96 * std_pred
            else:
                # Simple approximation for linear models
                residual_std = np.sqrt(self.model_performance[model_name]['mse'])
                confidence_lower = predictions - 1.96 * residual_std
                confidence_upper = predictions + 1.96 * residual_std
            
            results = []
            for i, (_, row) in enumerate(df.iterrows()):
                results.append({
                    'date': row.get('date'),
                    'business_id': row.get('business_id'),
                    'predicted_visitors': max(0, round(predictions[i], 0)),
                    'confidence_lower': max(0, round(confidence_lower[i], 0)),
                    'confidence_upper': max(0, round(confidence_upper[i], 0)),
                    'model_used': model_name
                })
            
            return {
                'status': 'success',
                'predictions': results,
                'model_performance': self.model_performance.get(model_name, {})
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def forecast_future(self, business_id: str, days_ahead: int = 30, 
                       base_data: Optional[Dict] = None) -> Dict:
        """
        Forecast future demand for specified number of days
        """
        try:
            # Generate future dates
            start_date = datetime.now().date()
            future_dates = [start_date + timedelta(days=i) for i in range(1, days_ahead + 1)]
            
            # Create input data for future dates
            future_data = []
            for future_date in future_dates:
                data_point = {
                    'business_id': business_id,
                    'date': future_date,
                    'is_weekend': future_date.weekday() >= 5,
                    'is_holiday': self._is_holiday(future_date),
                    # Add default values or use base_data if provided
                    'temperature': base_data.get('average_temperature', 20.0) if base_data else 20.0,
                    'weather_condition': base_data.get('weather_condition', 'clear') if base_data else 'clear',
                    'marketing_spend': base_data.get('marketing_spend', 0.0) if base_data else 0.0,
                }
                future_data.append(data_point)
            
            # Make predictions
            return self.predict(future_data)
            
        except Exception as e:
            logger.error(f"Future forecasting failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _is_holiday(self, date_obj: date) -> bool:
        """
        Simple holiday detection (can be enhanced with actual holiday data)
        """
        # Simple heuristic - major holidays
        month, day = date_obj.month, date_obj.day
        
        holidays = [
            (1, 1),   # New Year
            (12, 25), # Christmas
            (7, 4),   # Independence Day (US)
            (11, 11), # Veterans Day
        ]
        
        return (month, day) in holidays
    
    def _save_models(self):
        """
        Save trained models to disk
        """
        try:
            model_dir = settings.FORECASTING_MODEL_PATH
            os.makedirs(model_dir, exist_ok=True)
            
            # Save models
            for name, model in self.models.items():
                joblib.dump(model, os.path.join(model_dir, f'{name}.pkl'))
            
            # Save scalers and encoders
            joblib.dump(self.scalers, os.path.join(model_dir, 'scalers.pkl'))
            joblib.dump(self.label_encoders, os.path.join(model_dir, 'encoders.pkl'))
            joblib.dump(self.feature_columns, os.path.join(model_dir, 'features.pkl'))
            joblib.dump(self.model_performance, os.path.join(model_dir, 'performance.pkl'))
            
        except Exception as e:
            logger.error(f"Failed to save models: {e}")
    
    def _load_models(self):
        """
        Load trained models from disk
        """
        try:
            model_dir = settings.FORECASTING_MODEL_PATH
            
            if not os.path.exists(model_dir):
                return False
            
            # Load models
            for name in self.models.keys():
                model_path = os.path.join(model_dir, f'{name}.pkl')
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
            
            # Load scalers and encoders
            scaler_path = os.path.join(model_dir, 'scalers.pkl')
            if os.path.exists(scaler_path):
                self.scalers = joblib.load(scaler_path)
            
            encoder_path = os.path.join(model_dir, 'encoders.pkl')
            if os.path.exists(encoder_path):
                self.label_encoders = joblib.load(encoder_path)
            
            features_path = os.path.join(model_dir, 'features.pkl')
            if os.path.exists(features_path):
                self.feature_columns = joblib.load(features_path)
            
            performance_path = os.path.join(model_dir, 'performance.pkl')
            if os.path.exists(performance_path):
                self.model_performance = joblib.load(performance_path)
            
            self.is_trained = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    def get_feature_importance(self, model_name: str = 'random_forest') -> Dict:
        """
        Get feature importance for tree-based models
        """
        try:
            if not self.is_trained:
                return {'status': 'error', 'message': 'Models not trained'}
            
            model = self.models[model_name]
            
            if hasattr(model, 'feature_importances_'):
                importance_dict = dict(zip(self.feature_columns, model.feature_importances_))
                # Sort by importance
                sorted_importance = sorted(importance_dict.items(), key=lambda x: x[1], reverse=True)
                
                return {
                    'status': 'success',
                    'feature_importance': sorted_importance[:15]  # Top 15 features
                }
            else:
                return {
                    'status': 'error',
                    'message': f'Model {model_name} does not support feature importance'
                }
                
        except Exception as e:
            logger.error(f"Feature importance calculation failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


# Global instance
demand_forecaster = DemandForecaster()