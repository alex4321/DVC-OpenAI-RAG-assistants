# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/04_downloader_openai_files.ipynb.

# %% auto 0
__all__ = ['process']

# %% ../nbs/04_downloader_openai_files.ipynb 1
import argparse
from io import BytesIO
import sys
from typing import List
import openai
import pandas as pd

# %% ../nbs/04_downloader_openai_files.ipynb 2
def _prepare_splits(df_content: pd.DataFrame, df_splits: pd.DataFrame) -> pd.DataFrame:
    df = df_content.merge(df_splits, left_on="url", right_on="url")
    records = []
    for split, sub_df in df.groupby("split"):
        records.append({
            "split": split,
            "content": "\n\n".join(sub_df["content"])
        })
    return pd.DataFrame.from_records(records)

# %% ../nbs/04_downloader_openai_files.ipynb 4
def _upload_splits(df: pd.DataFrame, openai_client: openai.OpenAI) -> pd.DataFrame:
    file_ids = []
    for split, content in zip(df["split"], df["content"]):
        file = BytesIO(content.encode("utf-8"))
        file.name = f"split-{split}.md"
        file.seek(0)
        openai_file = openai_client.files.create(
            file=file,
            purpose="assistants"
        )
        file_ids.append(openai_file.id)
    return pd.DataFrame({"file_id": file_ids})

# %% ../nbs/04_downloader_openai_files.ipynb 6
def process(file_name_content: str, file_name_splits: str, file_name_openai_api_key: str, file_name_file_ids: str) -> None:
    df = _prepare_splits(
        pd.read_json(file_name_content, orient="records", lines=True),
        pd.read_json(file_name_splits, orient="records", lines=True),
    )
    with open(file_name_openai_api_key, "r") as src:
        openai_api_key = src.read()
    df_response = _upload_splits(df, openai.OpenAI(api_key=openai_api_key))
    df_response.to_json(file_name_file_ids, orient="records", lines=True)

# %% ../nbs/04_downloader_openai_files.ipynb 7
if __name__ == "__main__" and "ipykernel_launcher" not in " ".join(sys.argv) and "nbdev" not in " ".join(sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name_content",
                        type=str,
                        required=True,
                        help="JSONL file with downloaded Markdown")
    parser.add_argument("--file_name_splits",
                        type=str,
                        required=True,
                        help="JSONL file with precalculated splits")
    parser.add_argument("--file_name_openai_api_key",
                        type=str,
                        required=True,
                        help="File with OpenAI api key")
    parser.add_argument("--file_name_file_ids",
                        type=str,
                        required=True,
                        help="JSONL file with OpenAI file ids")
    process(**vars(parser.parse_args()))
