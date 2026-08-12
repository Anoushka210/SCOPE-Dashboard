import os
import pandas as pd

PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')

def create_deployment_dataset(target_rows=150000):
    full_path = os.path.join(PROCESSED_DIR, 'illicit_networks.csv')
    deploy_path = os.path.join(PROCESSED_DIR, 'illicit_networks_deployed.csv')
    
    if not os.path.exists(full_path):
        print(f"Full dataset not found at {full_path}")
        return
        
    df = pd.read_csv(full_path, low_memory=False)
    total_len = len(df)
    print(f"Full illicit networks dataset has {total_len:,} rows.")
    print("Full dataset columns:", df.columns.tolist())
    
    if total_len <= target_rows:
        df.to_csv(deploy_path, index=False)
        print(f"Saved dataset directly to {deploy_path}")
        return
        
    # Use stratified sample while preserving ALL original columns
    sample_df = df.sample(n=target_rows, random_state=42).copy()
    
    # Save trimmed deployment CSV
    sample_df.to_csv(deploy_path, index=False)
    file_size_mb = os.path.getsize(deploy_path) / (1024 * 1024)
    print(f"Created deployment dataset {deploy_path} with {len(sample_df):,} rows ({file_size_mb:.2f} MB).")
    print("Deployed dataset columns:", sample_df.columns.tolist())

if __name__ == '__main__':
    create_deployment_dataset()
