from pathlib import Path
import re
import pandas as pd
import datetime
import asyncio
from playwright.async_api import async_playwright
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import hashlib

class Post:
    def __init__(self, url, title, category, subcategory=None):
        self.url = url
        self.title = title
        self.category = category
        self.subcategory = subcategory
        self.safe_title = re.sub(r'[<>:"/\\|?*]', '_', title)
    
    def get_save_path(self, base_dir='outputs'):
        if self.subcategory:
            path = Path(base_dir) / self.category / self.subcategory / f"{self.safe_title}.html"
        else:
            path = Path(base_dir) / self.category / f"{self.safe_title}.html"
        return path

def download_and_replace_images(soup, save_path):
    img_dir = save_path.parent / 'images'
    img_dir.mkdir(parents=True, exist_ok=True)
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and src.startswith('http'):
            try:
                img_data = requests.get(src, timeout=10).content
                ext = src.split('.')[-1].split('?')[0][:5]
                hashname = hashlib.md5(src.encode()).hexdigest()[:10]
                local_img_name = f"{hashname}.{ext}"
                local_img_path = img_dir / local_img_name
                with open(local_img_path, 'wb') as f:
                    f.write(img_data)
                img['src'] = f"images/{local_img_name}"
            except Exception as e:
                print(f"Failed to download image: {src}, error: {e}")
                continue

async def save_webpage_to_html_async(post, browser, output_dir='outputs', page_timeout=30000):
    """Asynchronously save a single webpage to an HTML file, with 503 detection and image download."""
    save_path = post.get_save_path(output_dir)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    if save_path.exists():
        return f"File already exists, skipped: {save_path}"
    try:
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            java_script_enabled=True,
            bypass_csp=True
        )
        page = await context.new_page()
        page.set_default_timeout(page_timeout)
        response = await page.goto(post.url, wait_until='domcontentloaded')
        if response and response.status == 503:
            await context.close()
            msg = f"503 Service Unavailable detected for {post.url}. This may be due to rate limiting or server protection."
            log_error(post, msg)
            return f"Download failed (503): {post.url}"

        try:
            await page.wait_for_selector('article', timeout=5000)
        except:
            pass
        html_content = await page.content()

        # Parse HTML, download images, and replace src with local path
        soup = BeautifulSoup(html_content, 'html.parser')
        download_and_replace_images(soup, save_path)

        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        await context.close()
        return f"Success: {post.title}"
    except Exception as e:
        error_msg = f"Download failed {post.url}: {str(e)}"
        log_error(post, str(e))
        return error_msg

def log_error(post, error_msg):
    """Log errors to a log file."""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / 'error_log.txt'
    with log_path.open('a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {post.title} ({post.url}): {error_msg}\n")

def parse_posts_file(file_path='data/posts.csv'):
    """Parse posts.csv and return a list of Post objects."""
    try:
        df = pd.read_csv(file_path)
        return [Post(
            url=row['url'],
            title=row['title'],
            category=row['category'],
            subcategory=row['subcategory']
        ) for _, row in df.iterrows()]
    except Exception as e:
        print(f"Error parsing CSV file: {str(e)}")
        return []

async def download_batch(posts, semaphore, browser, output_dir, page_timeout):
    """Asynchronously download a batch of webpages."""
    async with semaphore:
        tasks = []
        for post in posts:
            task = asyncio.create_task(
                save_webpage_to_html_async(
                    post, 
                    browser, 
                    output_dir=output_dir,
                    page_timeout=page_timeout
                )
            )
            tasks.append(task)
        return await asyncio.gather(*tasks)

async def download_webpages_async(
    posts_file='data/posts.csv',
    concurrent_downloads=5,
    batch_size=10,
    page_timeout=30000,
    output_dir='outputs'
):
    """Asynchronously download all webpages."""
    posts = parse_posts_file(posts_file)
    total = len(posts)
    if total == 0:
        print("No pages found to download.")
        return
    print(f"Found {total} pages to download.")
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    progress_file = log_dir / 'download_progress.txt'
    if progress_file.exists():
        last_index = int(progress_file.read_text())
        posts = posts[last_index:]
    else:
        last_index = 0
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                ]
            )
            semaphore = asyncio.Semaphore(concurrent_downloads)
            with tqdm(total=len(posts), desc="Download progress") as pbar:
                for i in range(0, len(posts), batch_size):
                    batch = posts[i:i + batch_size]
                    results = await download_batch(
                        batch, 
                        semaphore, 
                        browser, 
                        output_dir,
                        page_timeout
                    )
                    progress_file.write_text(str(last_index + i + len(batch)), encoding='utf-8')
                    pbar.update(len(batch))
                    for result in results:
                        if "503" in result or result.startswith("Download failed"):
                            print(f"\n{result}")
            await browser.close()
    except KeyboardInterrupt:
        print("\nUser interrupted download")
    except Exception as e:
        print(f"\nError occurred: {str(e)}")

async def download_single_page(url, output_dir='outputs', page_timeout=30000):
    """Download a single webpage."""
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            post = Post(url=url, title='hyplus', category='single_pages')
            result = await save_webpage_to_html_async(
                post, 
                browser, 
                output_dir=output_dir,
                page_timeout=page_timeout
            )
            print(result)
            await browser.close()
    except Exception as e:
        print(f"Download failed: {str(e)}")

if __name__ == "__main__":
    url = "https://www.hyperplasma.top/hyplus"
    asyncio.run(download_single_page(url))