import argparse
from pathlib import Path
import sys
from downloader import download_webpages_async
import asyncio

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Bulk webpage downloader',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='data',
        help='Directory containing category/subcategory CSV files'
    )
    parser.add_argument(
        '--concurrent-downloads',
        type=int,
        default=5,
        help='Number of concurrent downloads'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='Number of pages to process per batch'
    )
    parser.add_argument(
        '--page-timeout',
        type=int,
        default=50000,
        help='Page load timeout (milliseconds)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='outputs',
        help='Directory to save downloaded files'
    )
    
    args = parser.parse_args()
    
    # Validation
    if args.concurrent_downloads < 1:
        parser.error("concurrent-downloads must be greater than 0")
    if args.batch_size < 1:
        parser.error("batch-size must be greater than 0")
    if args.page_timeout < 1000:
        parser.error("page-timeout must be at least 1000 ms")
    
    data_dir = Path(args.data_dir)
    if not data_dir.exists() or not data_dir.is_dir():
        parser.error(f"Data directory not found: {args.data_dir}")
    
    Path('logs').mkdir(exist_ok=True)
    # Ensure parent directories are created for output_dir
    Path(args.output_dir).mkdir(exist_ok=True, parents=True)
    
    return args

def main():
    """Main entry point."""
    args = parse_args()
    print("Hyplusite Exporter Configuration:")
    print(f"- Data directory: {args.data_dir}")
    print(f"- Output directory: {args.output_dir}")
    print(f"- Concurrent downloads: {args.concurrent_downloads}")
    print(f"- Batch size: {args.batch_size}")
    print(f"- Page timeout: {args.page_timeout} ms")
    try:
        asyncio.run(download_webpages_async(
            data_dir=args.data_dir,
            concurrent_downloads=args.concurrent_downloads,
            batch_size=args.batch_size,
            page_timeout=args.page_timeout,
            output_dir=args.output_dir
        ))
    except KeyboardInterrupt:
        print("\nUser interrupted execution")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during execution: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()