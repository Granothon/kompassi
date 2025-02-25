import os
import re
import subprocess
import sys
from collections import defaultdict
from functools import cache
from typing import Any

from django.core.management.base import BaseCommand
from tabulate import tabulate


def get_kind_and_scope(line: str) -> tuple[str, str]:
    if line.startswith("Merge "):
        return "merge", ""
    if match := re.match(r"^(?P<kind>\w+)\((?P<scope>.+)\):", line):
        # kind(scope): rest of the message ignored
        return match["kind"], match["scope"]
    elif match := re.match(r"^(?P<kind>\w+):", line):
        # kind: rest of the message ignored
        return match["kind"], ""
    else:
        return "", ""


@cache
def get_events() -> list[str]:
    events = [event for event in os.listdir("events") if os.path.isdir(os.path.join("events", event))]

    # some but not all folders under zombies are events
    # also some events have been excised
    events += ["hitpoint2017", "tracrossf2016", "tracon2023paidat"]

    return events


def is_event(scope: str) -> bool:
    return scope in get_events()


class Command(BaseCommand):
    help = "Print commit statistics by kind and scope for the last two months"

    def handle(self, *args: Any, **options: Any):
        if sys.stdin.isatty():
            input_lines = subprocess.check_output(
                ["git", "log", "--format=%s", "--since=2 months"],
                encoding="utf-8",
            ).split("\n")
        else:
            input_lines = sys.stdin.readlines()

        kind_stats: defaultdict[str, int] = defaultdict(int)
        scope_stats: defaultdict[str, int] = defaultdict(int)
        event_stats: defaultdict[str, int] = defaultdict(int)

        for line in input_lines:
            kind, scope = get_kind_and_scope(line)
            if kind:
                kind_stats[kind] += 1
            if scope:
                for scope in scope.split(","):
                    scope = scope.split("/", 1)[0]

                    if is_event(scope):
                        event_stats[scope] += 1
                    else:
                        scope_stats[scope] += 1

        kind_tabular = sorted(((v, k) for (k, v) in kind_stats.items()), reverse=True)
        scope_tabular = sorted(((v, k) for (k, v) in scope_stats.items()), reverse=True)
        events_tabular = sorted(((v, k) for (k, v) in event_stats.items()), reverse=True)

        print(tabulate(kind_tabular, headers=["# commits", "Kind"]))
        print()
        print(tabulate(scope_tabular, headers=["# commits", "Scope"]))
        print()
        print(tabulate(events_tabular, headers=["# commits", "Event"]))
