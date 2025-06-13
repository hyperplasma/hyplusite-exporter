# Hyplusite Exporter

Download posts from **Hyplusite** ([www.hyperplasma.top](https://www.hyperplasma.top)) as genteelly as you want.

## Features

- Bulk download of articles/posts from a CSV list
- Asynchronous, concurrent downloads for speed
- Progress tracking and automatic resume

## Requirements

- Python 3.11+
- The following Python packages:
    - **playwright**>=1.42.0  
    - pandas>=2.2.2  
    - tqdm>=4.66.1  

Install the dependencies with:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

All posts are listed in a CSV file  `data/posts.csv` with the following columns:

| url | title | category | subcategory |
|-----|-------|----------|-------------|
| https://www.hyperplasma.top/xxx | My Post Title | tech | python |

Run the downloader:

```bash
python main.py
```

Or specify your own options:

```bash
python main.py --posts-file data/posts.csv --output-dir downloads --concurrent-downloads 8 --batch-size 20 --page-timeout 20000
```

### Custom Arguments

- `--posts-file`: Path to the CSV file listing the posts to download.  
  Default: `data/posts.csv`
- `--output-dir`: Directory to save the downloaded HTML files.  
  Default: `outputs`
- `--concurrent-downloads`: Number of posts to download concurrently.  
  Default: `5`
- `--batch-size`: Number of posts to process per batch.  
  Default: `10`
- `--page-timeout`: Timeout for loading a page, in milliseconds.  
  Default: `30000`

### Resume and Redownload

- The downloader keeps progress in `logs/download_progress.txt` so you can safely resume interrupted downloads.
- **If you want to redownload all posts**, simply delete the `logs` directory or just the `logs/download_progress.txt` file before running the script again.

### Error Logging

- Any errors encountered during download will be logged to `logs/error_log.txt`.

## Example

```bash
python main.py --posts-file data/posts.csv --output-dir my_html --concurrent-downloads 10
```

## License

[LICENSE](LICENSE)

Hyperplasma