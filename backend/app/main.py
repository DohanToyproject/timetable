from __future__ import annotations

from io import BytesIO

import pandas as pd
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from .models import CourseAssignment, EntitySlot, EntityTimetable, GenerateResponse
from .scheduler import (
    TimetableError,
    assign_day_period,
    build_conflict_graph,
    color_graph,
    parse_courses,
)

app = FastAPI(title="Graph Coloring Timetable API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


def _build_teacher_timetables(assignments: list[CourseAssignment]) -> list[EntityTimetable]:
    teacher_map: dict[str, list[EntitySlot]] = {}

    for a in assignments:
        slot = EntitySlot(
            course_id=a.course_id,
            course_name=a.course_name,
            day=a.day,
            period=a.period,
            room=a.room,
            teacher=a.teacher,
        )

        teacher_map.setdefault(a.teacher, []).append(slot)

    # student list is derived from source course metadata, so rebuild from course assignments later in endpoint
    return [EntityTimetable(entity_id=t, slots=sorted(v, key=lambda x: (x.day, x.period))) for t, v in sorted(teacher_map.items())]


@app.post("/api/generate", response_model=GenerateResponse)
async def generate_timetable(
    file: UploadFile = File(...),
    algorithm: str = Form("welsh_powell"),
    days: int = Form(5),
) -> GenerateResponse:
    try:
        data = await file.read()
        filename = (file.filename or "").lower()
        if filename.endswith(".csv"):
            df = pd.read_csv(BytesIO(data))
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            df = pd.read_excel(BytesIO(data))
        else:
            raise TimetableError("Unsupported file format. Use .xlsx, .xls, or .csv.")
        courses = parse_courses(df)
        graph = build_conflict_graph(courses)
        color_map = color_graph(graph, algorithm=algorithm)
        slot_map = assign_day_period(color_map, days=days)

        assignments: list[CourseAssignment] = []
        by_id = {c.course_id: c for c in courses}

        for course_id, (timeslot, day, period) in sorted(slot_map.items(), key=lambda x: x[1][0]):
            c = by_id[course_id]
            assignments.append(
                CourseAssignment(
                    course_id=c.course_id,
                    course_name=c.course_name,
                    group_id=c.group_id,
                    teacher=c.teacher,
                    room=c.room,
                    credit=c.credit,
                    timeslot=timeslot,
                    day=day,
                    period=period,
                )
            )

        teacher_timetables = _build_teacher_timetables(assignments)
        student_slots: dict[str, list[EntitySlot]] = {}
        for a in assignments:
            c = by_id[a.course_id]
            for student_id in sorted(c.students):
                student_slots.setdefault(student_id, []).append(
                    EntitySlot(
                        course_id=a.course_id,
                        course_name=a.course_name,
                        day=a.day,
                        period=a.period,
                        room=a.room,
                        teacher=a.teacher,
                    )
                )
        student_timetables = [
            EntityTimetable(entity_id=sid, slots=sorted(slots, key=lambda x: (x.day, x.period)))
            for sid, slots in sorted(student_slots.items())
        ]

        chromatic_number = max(color_map.values()) + 1 if color_map else 0

        return GenerateResponse(
            chromatic_number=chromatic_number,
            num_courses=graph.number_of_nodes(),
            num_conflicts=graph.number_of_edges(),
            algorithm=algorithm,
            assignments=assignments,
            student_timetables=student_timetables,
            teacher_timetables=teacher_timetables,
        )
    except TimetableError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"Failed to generate timetable: {e}") from e
