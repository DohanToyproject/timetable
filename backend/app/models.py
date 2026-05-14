from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


AlgorithmType = Literal["greedy", "welsh_powell"]


class GenerateOptions(BaseModel):
    algorithm: AlgorithmType = "welsh_powell"
    days: int = Field(default=5, ge=1, le=7)


class CourseAssignment(BaseModel):
    course_id: str
    course_name: str
    group_id: str
    teacher: str
    room: str
    credit: int
    timeslot: int
    day: int
    period: int


class EntitySlot(BaseModel):
    course_id: str
    course_name: str
    day: int
    period: int
    room: str
    teacher: str


class EntityTimetable(BaseModel):
    entity_id: str
    slots: list[EntitySlot]


class GenerateResponse(BaseModel):
    chromatic_number: int
    num_courses: int
    num_conflicts: int
    algorithm: AlgorithmType
    assignments: list[CourseAssignment]
    student_timetables: list[EntityTimetable]
    teacher_timetables: list[EntityTimetable]
