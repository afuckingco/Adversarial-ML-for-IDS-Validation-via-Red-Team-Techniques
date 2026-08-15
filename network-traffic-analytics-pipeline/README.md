# Network Traffic Analytics Pipeline

This project provides an ETL (Extract, Transform, Load) pipeline for network traffic analytics. 
It generates a dummy processed dataset in Parquet format for demonstration and testing purposes.

## Features

- Generates synthetic network traffic features (packet counts, sizes, unique IPs, JA3 fingerprints, etc.)
- Outputs data in Apache Parquet format for efficient storage and querying
- Includes both normal and adversarial traffic windows for comparative analysis
- Modular and extensible design for real data integration

## Project Structure

```
network-traffic-analytics-pipeline/
├── src/
│   └── etl.py                  # Main ETL script
├── data/
│   └── processed/              # Directory for processed datasets (will be created)
├── notebooks/                  # Jupyter notebooks for analysis
├── docs/                       # Documentation
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd network-traffic-analytics-pipeline

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Run the ETL script to generate or load the processed dataset:

```bash
python src/etl.py
```

The script will:
1. Check for an existing processed dataset at `data/processed/dataset.parquet`
2. If it exists, load and display it
3. If not, generate a dummy dataset with two time windows (normal and adversarial) and save it as Parquet

## Example Output

After running the script, you should see output similar to:

```
Processed dataset not found. Generating dummy data...
Saved dummy processed dataset to /home/afiq/network-traffic-analytics-pipeline/data/processed/dataset.parquet

Dataset info:
<class 'pandas.core.frame.DataFrame'>
RangeIndex: 2 entries, 0 to 1
Data columns (total 9 columns):
 #   Column          Non-Null Count  Dtype         
---  ------          --------------  -----         
 0   window_start    2 non-null      datetime64[ns]
 1   window_end      2 non-null      datetime64[ns]
 2   total_packets   2 non-null      int64         
 3   avg_packet_size 2 non-null      float64       
 4   std_packet_size 2 non-null      float64       
 5   unique_src_ips  2 non-null      int64         
 6   unique_dst_ips  2 non-null      int64         
 7   common_ja3      2 non-null      object        
 8   label           2 non-null      int64         
dtypes: datetime64[ns](2), float64(3), int64(3), object(1)
memory usage: 160.0+ bytes
None

Dataset contents:
            window_start              window_end  total_packets  avg_packet_size  std_packet_size  unique_src_ips  unique_dst_ips      common_ja3  label
0 2026-08-15 12:00:00 2026-08-15 12:05:00         1456        523.456789      102.345678            78            55      chrome_103      0
1 2026-08-15 12:05:00 2026-08-15 12:10:00         7832        198.765432       45.678901           342           112  1234567890123456      1
```

## Dependencies

- pandas>=2.0
- pyarrow>=10.0 (for Parquet support)
- scikit-learn>=1.0 (for potential future ML steps)
- matplotlib>=3.0 and seaborn>=0.10 (for visualization in notebooks)

## Notes

- This is a dummy dataset generator for demonstration and testing. 
- For real-world use, replace the `generate_dummy_processed_data` function with actual data extraction and transformation logic.
- The dataset includes two windows: one labeled as normal (0) and one as adversarial (1).

## License

MIT