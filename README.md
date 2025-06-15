# Hyplusite Exporter

Download posts from **Hyplusite** ([www.hyperplasma.top](https://www.hyperplasma.top)) or other sites as genteelly as you want.

## Features

- Bulk download of articles/posts from a multi-level CSV directory tree
- Asynchronous, concurrent downloads for speed
- Progress tracking and automatic resume
- Local image downloads for offline viewing  
- Error detection for 503 Service Unavailable
- Detailed error logging
- **Automatic tree-structured HTML index page (`index.html`) with author info and UTC timestamp**

## Requirements

- Python 3.11+
- The following Python packages (with specified versions):
  - playwright>=1.42.0
  - pandas>=2.2.2  
  - tqdm>=4.66.1
  - beautifulsoup4>=4.12.3
  - requests>=2.32.2

Install the dependencies with:

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage 

All posts are now listed in a **multi-level directory tree of CSV files** under the `data/` folder, structured as follows:

```
data/
└── <category>/
    └── <subcategory>/
        └── <sub-subcategory>.csv
```

Each CSV file contains these columns:

| url                               | title         |
| --------------------------------- | ------------- |
| `https://www.hyperplasma.top/xxx` | My Post Title |

**Example:**

```
data/Java/Tutorial/Basic.csv
data/Java/Advanced/Threading.csv 
data/Python/Web/Django/Tutorial.csv
data/Database/MySQL/Basic.csv
...
```

**Each row in a CSV represents a post, and CSV files can be nested in multiple subdirectories.**

Run the downloader (default settings):

```bash
python main.py
```

Or specify your own options:

```bash
python main.py --data-dir data --output-dir outputs/hyplusite --concurrent-downloads 8 --batch-size 20 --page-timeout 20000
```

### Custom Arguments

- `--data-dir`: Root directory containing the multi-level CSV file tree.  
  Default: `data`
- `--output-dir`: Directory to save the downloaded HTML files and the index page.  
  Default: `outputs/hyplusite` 
- `--concurrent-downloads`: Number of posts to download concurrently.  
  Default: `5`
- `--batch-size`: Number of posts to process per batch.  
  Default: `10` 
- `--page-timeout`: Timeout for loading a page, in milliseconds.  
  Default: `30000`

### Downloaded Files Structure

- HTML files mirror the source directory structure:
  ```
  outputs/hyplusite/
  ├── index.html
  └── <category>/
      └── <subcategory>/
          └── <sub-subcategory>/
              ├── my-post-title.html
              └── images/
                  └── <MD5-hashed-image-names>
  ```
- An `index.html` file is generated in the top-level output directory:
  - Contains a tree-structured index linking to all downloaded HTML files
  - Includes author metadata and UTC timestamp
  - Auto-updates timestamp on each run
- External images are downloaded to an `images/` subfolder in the same directory as the HTML file
  - Image filenames are MD5-hashed from their original URLs to prevent conflicts
  - Extensions are properly preserved or defaulted to .jpg if missing

### Resume and Redownload

- The downloader keeps progress in `logs/download_progress.txt` so you can safely resume interrupted downloads.
- **If you want to redownload all posts**, simply delete the `logs` directory or just the `logs/download_progress.txt` file before running the script again.

### Error Logging

- Any errors encountered during download will be logged to `logs/error_log.txt`
- HTTP 503 (Service Unavailable) errors are specifically detected and logged

## Example

```bash
python main.py --data-dir data --output-dir outputs/hyplusite --concurrent-downloads 5
```

## License

[LICENSE](LICENSE)

---

Last updated by [Akira37](https://github.com/hyperplasma) (hyperplasma).
