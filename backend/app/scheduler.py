from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import networkx as nx
import pandas as pd


REQUIRED_COLUMNS = {
    "course_id",
    "course_name",
    "group_id",
    "teacher",
    "room",
    "credit",
    "students",
}


@dataclass
class Course:
    course_id: str
    course_name: str
    group_id: str
    teacher: str
    room: str
    credit: int
    students: set[str]


class TimetableError(ValueError):
    pass


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {c: c.strip().lower() for c in df.columns}
    return df.rename(columns=renamed)


def _parse_students(raw: str | float | int | None) -> set[str]:
    if raw is None:
        return set()
    text = str(raw).strip()
    if not text or text.lower() == "nan":
        return set()
    return {token.strip() for token in text.split(",") if token.strip()}


def parse_courses(df: pd.DataFrame) -> list[Course]:
    df = _normalize_columns(df)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise TimetableError(f"Missing required columns: {sorted(missing)}")

    courses: list[Course] = []
    for _, row in df.iterrows():
        credit_value = int(row["credit"]) if pd.notna(row["credit"]) else 1
        courses.append(
            Course(
                course_id=str(row["course_id"]),
                course_name=str(row["course_name"]),
                group_id=str(row["group_id"]),
                teacher=str(row["teacher"]),
                room=str(row["room"]),
                credit=credit_value,
                students=_parse_students(row["students"]),
            )
        )

    if not courses:
        raise TimetableError("No course rows found.")
    return courses


def _has_conflict(a: Course, b: Course) -> bool:
    if a.teacher == b.teacher:
        return True
    if a.room == b.room:
        return True
    if a.group_id == b.group_id:
        return True
    if a.students & b.students:
        return True
    return False


def build_conflict_graph(courses: Iterable[Course]) -> nx.Graph:
    courses = list(courses)
    graph = nx.Graph()

    for course in courses:
        graph.add_node(course.course_id, course=course)

    for i in range(len(courses)):
        for j in range(i + 1, len(courses)):
            a = courses[i]
            b = courses[j]
            if _has_conflict(a, b):
                graph.add_edge(a.course_id, b.course_id)

    return graph


def _color_welsh_powell(graph: nx.Graph) -> dict[str, int]:
    order = sorted(graph.nodes(), key=lambda n: graph.degree[n], reverse=True)
    color_map: dict[str, int] = {}
    current_color = 0

    for node in order:
        if node in color_map:
            continue

        color_map[node] = current_color
        for candidate in order:
            if candidate in color_map:
                continue
            neighbors = graph.neighbors(candidate)
            if all(color_map.get(nei) != current_color for nei in neighbors):
                color_map[candidate] = current_color

        current_color += 1

    return color_map


def color_graph(graph: nx.Graph, algorithm: str = "welsh_powell") -> dict[str, int]:
    if algorithm == "greedy":
        return nx.coloring.greedy_color(graph, strategy="largest_first")
    if algorithm == "welsh_powell":
        return _color_welsh_powell(graph)
    raise TimetableError(f"Unknown algorithm: {algorithm}")


def assign_day_period(color_map: dict[str, int], days: int = 5) -> dict[str, tuple[int, int, int]]:
    assignments: dict[str, tuple[int, int, int]] = {}
    for course_id, timeslot in color_map.items():
        day = timeslot % days
        period = timeslot // days
        assignments[course_id] = (timeslot, day + 1, period + 1)
    return assignments
