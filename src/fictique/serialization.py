from dataclasses import asdict
from pathlib import Path
from typing import List, Tuple


#####################################################
# yaml dumping of Fiction objects

import yaml

from fictique.model import Fiction, GutenbergBook

fiction_tag = "!Fiction"
fictions_dir = Path("data/royalroad/")
fictions_dir.mkdir(parents=True, exist_ok=True)

def fiction_path(slot: int) -> Path:
    return fictions_dir / f"{slot}.yaml"


# create yaml dumper & loader for Fiction objects
def fiction_representer(dumper, data):
    return dumper.represent_mapping(fiction_tag, data.to_ordered_dict().items())
yaml.add_representer(Fiction, fiction_representer)
def fiction_constructor(loader, node):
    value = loader.construct_mapping(node)
    return Fiction(**value)
yaml.add_constructor(fiction_tag, fiction_constructor)

# ensure multiline strings are dumped in block format
def string_representer(dumper, data):
    if '\n' in data:
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)
yaml.add_representer(str, string_representer)


def load_fiction(slot: int) -> Fiction | None:
    path = fiction_path(slot)
    if not path.exists():
        return None
    with path.open('r') as f:
        return yaml.load(f, yaml.Loader)

def save_fiction(fiction: Fiction) -> bool:
    # only save if sth changed
    if load_fiction(fiction.slot) == fiction: return False
    with fiction_path(fiction.slot).open("w", encoding="utf-8") as f:
        yaml.dump(fiction, f)
    return True

#####################################################
# yaml dumping of gutenberg metadata

def save_as_yaml(book: GutenbergBook, directory: Path, book_id: int) -> Path:
    yaml_filepath = directory / f'{book_id}.yaml'
    with open(yaml_filepath, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(asdict(book), yaml_file, default_flow_style=False, allow_unicode=True)
    return yaml_filepath

#####################################################
# reading/writing rankings

import os
from datetime import datetime


dateformat = '%Y%m%d%H%M%S'
rankings_dir = Path("data/royalroad/rankings/")
rankings_dir.mkdir(parents=True, exist_ok=True)

def ranking_path(key: str) -> Path:
    return rankings_dir / f"{key}.txt"

def ranking_changed(old: List[int], new: List[int]) -> bool:
    """basic list-comparison"""
    if len(old) != len(new): return True
    if len(old) == 0: return False
    for o, n in zip(old, new):
        if o != n: return True
    return False

def read_ranking(key: str) -> Tuple[datetime,List[int]] | None:
    path = ranking_path(key)
    if not path.exists():
        return None
    with path.open("rb") as file:
        file.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
        file_size = file.tell()    # Get the size of the file

        if file_size == 0:         # Check if the file is empty
            return None

        offset = -1

        while True:
            file.seek(offset, os.SEEK_END)
            if file.tell() == 0:  # Reached the start of the file
                break
            if file.read(1) == b'\n':  # Check for newline character
                break
            offset -= 1

        last_line = file.readline().decode()
        date,rankings = last_line.split(":")
        return datetime.strptime(date, dateformat), [int(s) for s in rankings.split(",")]

def update_ranking(key: str, ranking: List[int]) -> bool:
    prev_ranking = read_ranking(key)
    needs_update = prev_ranking is None or ranking_changed(prev_ranking[1], ranking)
    if not needs_update: return False
    nowstr = datetime.now().strftime(dateformat)
    rankingstr = ",".join(str(s) for s in ranking)
    path = ranking_path(key)
    already_present = path.exists()
    with path.open("a", encoding="utf-8") as f:
        if not already_present:
            f.write("date & time   :ranking")
        f.write(f"\n{nowstr}:{rankingstr}")
    return True
