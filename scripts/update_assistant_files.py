# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/07_update_assistant_files.ipynb.

# %% auto 0
__all__ = ['process']

# %% ../nbs/07_update_assistant_files.ipynb 1
import argparse
import sys
from typing import List
import openai
import pandas as pd

# %% ../nbs/07_update_assistant_files.ipynb 2
def _set_assistant_files(assistant_id: str, file_ids: List[str], openai_client: openai.OpenAI) -> None:
    remove_files = set()
    existing_files = set()
    for existing_file in openai_client.beta.assistants.files.list(assistant_id=assistant_id).data:
        if existing_file.id not in file_ids:
            remove_files.add(existing_file.id)
        else:
            existing_files.add(existing_file.id)
    new_files = set(file_ids) - existing_files
    for file_id in remove_files:
        openai_client.beta.assistants.files.delete(
            file_id=file_id,
            assistant_id=assistant_id
        )
    for file_id in new_files:
        openai_client.beta.assistants.files.create(
            file_id=file_id,
            assistant_id=assistant_id
        )
    return file_ids

# %% ../nbs/07_update_assistant_files.ipynb 3
def process(file_name_assistants: str, file_name_file_ids: str, file_name_openai_api_key: str, file_name_mapping: str) -> None:
    df_assistants = pd.read_csv(file_name_assistants)
    df_files = pd.read_json(file_name_file_ids, orient="records", lines=True)
    with open(file_name_openai_api_key, "r", encoding="utf-8") as src:
        openai_api_key = src.read()
    openai_client = openai.OpenAI(api_key=openai_api_key)
    df_assistants["file_ids"] = df_assistants["assistant_id"] \
        .apply(lambda assistant_id: _set_assistant_files(assistant_id, set(df_files["file_id"]), openai_client)) \
        .apply(set).apply(sorted).apply(",".join)
    df_assistants[["assistant_id", "file_ids"]].to_json(file_name_mapping, orient="records", lines=True)

# %% ../nbs/07_update_assistant_files.ipynb 5
if __name__ == "__main__" and "ipykernel_launcher" not in " ".join(sys.argv) and "nbdev" not in " ".join(sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_name_assistants",
                        type=str,
                        required=True,
                        help="A CSV with assistant ids")
    parser.add_argument("--file_name_file_ids",
                        type=str,
                        required=True,
                        help="JSONL file with all the file ids")
    parser.add_argument("--file_name_openai_api_key",
                        type=str,
                        required=True,
                        help="OpenAI api key")
    parser.add_argument("--file_name_mapping",
                        type=str,
                        required=True,
                        help="Output assistant-file ids mapping")
    process(**vars(parser.parse_args()))
