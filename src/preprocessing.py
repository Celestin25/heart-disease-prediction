import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
import joblib

def load_data(filepath='saved_models/heart_disease_model.pkl'):
    df = pd.read_csv(filepath)
    return df

def identify_categorical_variables(df):
    categorical_vars = df.select_dtypes(include=['object', 'category']).columns.tolist()
    return categorical_vars

def create_preprocessing_pipeline(numeric_features, categorical_features):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])

    return preprocessor

def preprocess_data(df, target_column, save_path=None):
    y = df[target_column]
    X = df.drop(target_column, axis=1)

    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = identify_categorical_variables(X)

    preprocessing_pipeline = create_preprocessing_pipeline(numeric_features, categorical_features)
    X_processed = preprocessing_pipeline.fit_transform(X)
    
    if save_path:
        joblib.dump(preprocessing_pipeline, save_path)

    return X_processed, y

