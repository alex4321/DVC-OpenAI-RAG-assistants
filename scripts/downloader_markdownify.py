# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_downloader_markdownify.ipynb.

# %% auto 0
__all__ = ['process']

# %% ../nbs/02_downloader_markdownify.ipynb 1
import argparse
import sys
from markdownify import markdownify as md
import pandas as pd

# %% ../nbs/02_downloader_markdownify.ipynb 2
def process(file_name_html: str, file_name_markdown: str) -> None:
    df = pd.read_json(file_name_html, orient="records", lines=True)
    df["content"] = "# " + df["title"].fillna("") + "\n\n" + df["content"]
    df["content"] = "\n" + df["content"].apply(
        lambda text: md(text, heading_style="ATX")
    )
    df["content"] = df.apply(
        lambda row: row["content"].replace("\n#", f"\n{row['publish_date']}\n#"),
        axis=1,
    )
    df["content"] = df["content"].str.strip()
    df.to_json(file_name_markdown, orient="records", lines=True)

# %% ../nbs/02_downloader_markdownify.ipynb 4
if __name__ == "__main__" and "ipykernel_launcher" not in " ".join(sys.argv) and "nbdev" not in " ".join(sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name_html",
                        type=str,
                        required=True,
                        help="JSONL file with downloaded HTML")
    parser.add_argument("--file_name_markdown",
                        type=str,
                        required=True,
                        help="JSONL file with converted Markdown")
    process(**vars(parser.parse_args()))
