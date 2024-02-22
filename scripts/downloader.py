# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_downloader.ipynb.

# %% auto 0
__all__ = ['PageData', 'process']

# %% ../nbs/01_downloader.ipynb 1
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
import sys
from typing import Union, List
from bs4 import BeautifulSoup
from goose3 import Goose
import pandas as pd
from pydantic import BaseModel
import requests

# %% ../nbs/01_downloader.ipynb 2
class PageData(BaseModel):
    url: str
    title: str
    content: str
    publish_date: str


def _load_page_html(url: str) -> str:
    response = requests.get(url)
    assert response.status_code == 200
    return response.content


def _remove_scripts_and_styles(html: str) -> str:
    soup = BeautifulSoup(html, 'lxml')
    for script in soup.find_all('script'):
        script.decompose()
    for style in soup.find_all('style'):
        style.decompose()
    return str(soup)


def _parse_page(url: str, goose: Goose) -> Union[PageData, None]:
    try:
        html = _load_page_html(url)
        html = _remove_scripts_and_styles(html)
        extraction = goose.extract(raw_html=html)
        return PageData(
            url=url,
            title=extraction.title,
            content=extraction.top_node_raw_html,
            publish_date=str(extraction.publish_date),
        )
    except:
        return None
    

def _parse_pages(urls: List[str], goose: Goose, thread_pool_size: int) -> List[PageData]:
    pool = ThreadPoolExecutor(max_workers=thread_pool_size)
    results = list(pool.map(
        _parse_page,
        urls,
        [goose] * len(urls)
    ))
    results = [item for item in results if item is not None]
    return results

# %% ../nbs/01_downloader.ipynb 3
def process(file_name_urls: str, file_name_content: str, thread_pool_size: int) -> None:
    print("Reading URLs")
    with open(file_name_urls, "r", encoding="utf-8") as src:
        urls = src.read().strip().split("\n")
    print("Reading downloaded content")
    if os.path.exists(file_name_content):
        df_content = pd.read_json(file_name_content, orient="records", lines=True)
    else:
        df_content = pd.DataFrame({"url": [], "title": [], "content": [], "publish_date": []})
    print("Removing unnecessary content")
    df_content = df_content.loc[df_content["url"].isin(urls)]
    print("Downloading new content")
    new_content = _parse_pages(
        [url for url in urls if url not in set(df_content["url"])],
        Goose(),
        thread_pool_size,
    )
    df_new_content = pd.DataFrame.from_records([
        item.model_dump()
        for item in new_content
    ])
    print("Saving new content")
    df_content = pd.concat([df_content, df_new_content]).reset_index(drop=True)
    df_content.to_json(file_name_content, orient="records", lines=True)

# %% ../nbs/01_downloader.ipynb 5
if __name__ == "__main__" and "ipykernel_launcher" not in " ".join(sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name_urls",
                        type=str,
                        required=True,
                        help="List with content URLs")
    parser.add_argument("--file_name_content",
                        type=str,
                        required=True,
                        help="List with downloaded HTML")
    parser.add_argument("--thread_pool_size",
                        type=int,
                        required=True,
                        help="Downloader thread pool size")
    process(**vars(parser.parse_args()))
