import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
from colorama import Fore, Style, init
from pyfiglet import Figlet
from urllib.parse import urlparse, urljoin
# Initialize colorama
init()

def custom_banner():
    custom_fig = Figlet(font='slant')
    banner = custom_fig.renderText('S0rXD0')
    print(Fore.CYAN + banner + Style.RESET_ALL)
    print(Fore.GREEN + "Author: LocalHost.07" + Style.RESET_ALL)

def create_output_directory(base_dir):
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    return base_dir

def save_page_content(base_dir, domain, page_url, content):
    # Ensure the domain-based directory exists
    domain_dir = os.path.join(base_dir, domain)
    if not os.path.exists(domain_dir):
        os.makedirs(domain_dir)

    # Save the content to a file named by the URL path
    parsed_url = urlparse(page_url)
    file_name = parsed_url.path.replace("/", "_").strip("_") or "index"
    file_path = os.path.join(domain_dir, f"{file_name}.html")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def get_all_links(domain, url, base_url, visited_urls, session):
    try:
        response = session.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        links = [urljoin(base_url, link) for link in links]
        links = [link for link in links if urlparse(link).netloc == domain and link not in visited_urls]
        return links, soup.prettify()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return [], ""

def download_website(url):
    base_url = url
    domain = urlparse(url).netloc
    output_dir = create_output_directory("output")

    session = requests.Session()
    visited_urls = set()
    urls_to_visit = [base_url]
    start_time = time.time()

    with tqdm(total=0, desc="Pages Downloaded", unit="page") as pbar:
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            if current_url not in visited_urls:
                visited_urls.add(current_url)
                new_links, page_content = get_all_links(domain, current_url, base_url, visited_urls, session)
                save_page_content(output_dir, domain, current_url, page_content)
                urls_to_visit.extend(new_links)
                pbar.total = len(visited_urls)
                pbar.update(1)
                elapsed_time = time.time() - start_time
                pbar.set_postfix(elapsed=f"{elapsed_time:.2f}s", refresh=True)

    elapsed_time = time.time() - start_time
    print(Fore.YELLOW + f"\nDownload completed in {elapsed_time:.2f} seconds" + Style.RESET_ALL)

if __name__ == "__main__":
    custom_banner()
    url = input("Enter the website URL: ")
    download_website(url)
