"""
Query repos on GitHub and write a csv containing the traffic values (clones and views) for each repo
"""
from pathlib import Path
from dataclasses import dataclass
import datetime
from typing import cast, Optional, Tuple, List, Dict
import csv
import pprint
from github import Github, Clones, View
import click


OUT_FILENAME = "data/repo_traffic.csv"

REPO_LIST = ("arc_arena", "arcade_examples", "arcade_screensaver_framework")


@dataclass
class Row:
    clone: Optional[Clones.Clones] = None
    view: Optional[View.View] = None


def _query_github() -> Dict[Tuple[datetime.date, str], Row]:
    hub = Github(Path("secret.txt").read_text())
    dat: Dict[Tuple[datetime.date, str], Row] = {}

    for repo in hub.get_user().get_repos():
        # if repo.name not in REPO_LIST:
        #     continue
        print("Repo:", repo.name)
        clones_dat = repo.get_clones_traffic(per="day")
        clones = cast(List[Clones.Clones], clones_dat["clones"])
        for clone in clones:
            # print("clone", clone.uniques, clone.count, clone.timestamp)
            clone_date = clone.timestamp.date()
            dat.setdefault((clone_date, repo.name), Row()).clone = clone

        views_dat = repo.get_views_traffic(per="day")
        views = cast(List[View.View], views_dat["views"])
        for view in views:
            # print("view", view.uniques, view.count, view.timestamp)
            view_date = view.timestamp.date()
            dat.setdefault((view_date, repo.name), Row()).view = view

    return dat


def _write_csv(data) -> None:
    now = datetime.datetime.now().date()
    print('Now:', now)

    print(f"Writing to {OUT_FILENAME}")
    with Path(OUT_FILENAME).open("w", newline="") as out:
        csv_writer = csv.writer(out, dialect="excel")

        pprint.pprint(data)
        items = list(data.keys())
        items.sort()
        headers = ("day", "repo", "clone_count", "clone_uniques", "view_count", "view_uniques")
        csv_writer.writerow(headers)
        for key in items:
            day, repo_name = key
            row = data[key]
            if day == now:
                print("  skipping data that is timestamped today (as could be potentially incomplete)", key, row)
                continue

            clone_count = 0 if row.clone is None else row.clone.count
            clone_uniques = 0 if row.clone is None else row.clone.uniques
            view_count = 0 if row.view is None else row.view.count
            view_uniques = 0 if row.view is None else row.view.uniques
            out_row = (day, repo_name, clone_count, clone_uniques, view_count, view_uniques)
            csv_writer.writerow(out_row)


@click.command()
def main():
    """help goes here"""
    data = _query_github()
    _write_csv(data)


if __name__ == '__main__':
    main()
