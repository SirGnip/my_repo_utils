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


DETAILS_FILENAME = "data/repo_traffic.csv"
SUMMARY_FILENAME = "data/master_repo_traffic_summary.csv"

REPO_LIST = ("arc_arena", "arcade_examples", "arcade_screensaver_framework")


@dataclass
class Row:
    clone: Optional[Clones.Clones] = None
    view: Optional[View.View] = None


@dataclass
class SummaryRow:
    clone_count: int = 0
    clone_unique: int = 0
    view_count: int = 0
    view_unique: int = 0


def _query_github() -> Tuple[Dict[str, SummaryRow], Dict[Tuple[datetime.date, str], Row]]:
    hub = Github(Path("secret.txt").read_text())
    #               date         , repo
    details: Dict[Tuple[datetime.date, str], Row] = {}
    #               repo
    summaries: Dict[str, SummaryRow] = {}

    for repo in hub.get_user().get_repos():
        # if repo.name not in REPO_LIST:
        #     continue
        print("Repo:", repo.name)
        clones_dat = repo.get_clones_traffic(per="day")
        clones = cast(List[Clones.Clones], clones_dat["clones"])
        for clone in clones:
            # print("clone", clone.uniques, clone.count, clone.timestamp)
            clone_date = clone.timestamp.date()
            details.setdefault((clone_date, repo.name), Row()).clone = clone

        views_dat = repo.get_views_traffic(per="day")
        views = cast(List[View.View], views_dat["views"])

        for view in views:
            # print("view", view.uniques, view.count, view.timestamp)
            view_date = view.timestamp.date()
            details.setdefault((view_date, repo.name), Row()).view = view

        summaries[repo.name] = SummaryRow(
            clones_dat["count"],
            clones_dat["uniques"],
            views_dat["count"],
            views_dat["uniques"],
        )

    return summaries, details


def _write_details_csv(details) -> None:
    print(f"\n===== Writing to {DETAILS_FILENAME}")
    now = datetime.datetime.now().date()
    print('Now:', now)

    with Path(DETAILS_FILENAME).open("w", newline="") as out:
        csv_writer = csv.writer(out, dialect="excel")

        pprint.pprint(details)
        items = list(details.keys())
        items.sort()
        headers = ("day", "repo", "clone_count", "clone_uniques", "view_count", "view_uniques")
        csv_writer.writerow(headers)
        for key in items:
            day, repo_name = key
            row = details[key]
            if day == now:
                print("  skipping data that is timestamped today (as could be potentially incomplete)", key, row)
                continue

            clone_count = 0 if row.clone is None else row.clone.count
            clone_uniques = 0 if row.clone is None else row.clone.uniques
            view_count = 0 if row.view is None else row.view.count
            view_uniques = 0 if row.view is None else row.view.uniques
            out_row = (day, repo_name, clone_count, clone_uniques, view_count, view_uniques)
            csv_writer.writerow(out_row)


def _write_summary_csv(summaries):
    print(f"\n===== Writing to {SUMMARY_FILENAME}")
    now = datetime.datetime.now().date()
    print('Now:', now)

    with Path(SUMMARY_FILENAME).open("a", newline="") as out:
        csv_writer = csv.writer(out, dialect="excel")

        keys = list(summaries.keys())
        keys.sort()
        # headers = ("day", "repo", "clone_count", "clone_uniques", "view_count", "view_uniques")
        # csv_writer.writerow(headers)

        for repo_name in keys:
            row = summaries[repo_name]
            print("Summary:", repo_name, row)
            out_row = (now, repo_name, row.clone_count, row.clone_unique, row.view_count, row.view_unique)
            csv_writer.writerow(out_row)


@click.command()
def main():
    """Query GitHub and save the traffic data to csv files"""
    summaries, details = _query_github()
    _write_details_csv(details)
    _write_summary_csv(summaries)


if __name__ == '__main__':
    main()
