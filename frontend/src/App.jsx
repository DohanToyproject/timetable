import { useMemo, useState } from "react";

const API_BASE = "http://localhost:8000";

export default function App() {
  const [file, setFile] = useState(null);
  const [algorithm, setAlgorithm] = useState("welsh_powell");
  const [days, setDays] = useState(5);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState("");
  const [selectedTeacher, setSelectedTeacher] = useState("");

  const grouped = useMemo(() => {
    if (!result?.assignments) return {};
    return result.assignments.reduce((acc, item) => {
      const key = `Day ${item.day} / Period ${item.period}`;
      if (!acc[key]) acc[key] = [];
      acc[key].push(item);
      return acc;
    }, {});
  }, [result]);

  async function onSubmit(e) {
    e.preventDefault();
    if (!file) {
      setError("Excel 파일을 선택하세요.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const form = new FormData();
      form.append("file", file);
      form.append("algorithm", algorithm);
      form.append("days", String(days));

      const res = await fetch(`${API_BASE}/api/generate`, {
        method: "POST",
        body: form,
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "요청 실패");
      }

      setResult(await res.json());
      setSelectedStudent("");
      setSelectedTeacher("");
    } catch (err) {
      setError(err.message);
      setResult(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <h1>그래프 채색 시간표 생성기</h1>

      <form className="panel" onSubmit={onSubmit}>
        <label>
          Excel 파일
          <input type="file" accept=".xlsx,.xls,.csv" onChange={(e) => setFile(e.target.files?.[0] || null)} />
        </label>

        <label>
          알고리즘
          <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
            <option value="welsh_powell">Welsh-Powell</option>
            <option value="greedy">Greedy (Largest First)</option>
          </select>
        </label>

        <label>
          주간 일수
          <input
            type="number"
            min="1"
            max="7"
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
          />
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "생성 중..." : "시간표 생성"}
        </button>

        {error && <p className="error">{error}</p>}
      </form>

      {result && (
        <section className="panel">
          <h2>결과</h2>
          <p>채색수(시간대 수): {result.chromatic_number}</p>
          <p>과목 수: {result.num_courses}</p>
          <p>충돌 간선 수: {result.num_conflicts}</p>

          {Object.entries(grouped).map(([slot, rows]) => (
            <article key={slot} className="slot">
              <h3>{slot}</h3>
              <table>
                <thead>
                  <tr>
                    <th>과목ID</th>
                    <th>과목명</th>
                    <th>그룹</th>
                    <th>교사</th>
                    <th>교실</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.map((r) => (
                    <tr key={r.course_id}>
                      <td>{r.course_id}</td>
                      <td>{r.course_name}</td>
                      <td>{r.group_id}</td>
                      <td>{r.teacher}</td>
                      <td>{r.room}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </article>
          ))}

          <h2>학생별 시간표</h2>
          <label>
            학생 선택
            <select value={selectedStudent} onChange={(e) => setSelectedStudent(e.target.value)}>
              <option value="">학생을 선택하세요</option>
              {result.student_timetables.map((t) => (
                <option key={t.entity_id} value={t.entity_id}>
                  {t.entity_id}
                </option>
              ))}
            </select>
          </label>
          {selectedStudent && (
            <table>
              <thead>
                <tr>
                  <th>요일</th>
                  <th>교시</th>
                  <th>과목</th>
                  <th>교사</th>
                  <th>교실</th>
                </tr>
              </thead>
              <tbody>
                {result.student_timetables
                  .find((t) => t.entity_id === selectedStudent)
                  ?.slots.map((s) => (
                    <tr key={`${s.course_id}-${s.day}-${s.period}`}>
                      <td>{s.day}</td>
                      <td>{s.period}</td>
                      <td>{s.course_name}</td>
                      <td>{s.teacher}</td>
                      <td>{s.room}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}

          <h2>교사별 시간표</h2>
          <label>
            교사 선택
            <select value={selectedTeacher} onChange={(e) => setSelectedTeacher(e.target.value)}>
              <option value="">교사를 선택하세요</option>
              {result.teacher_timetables.map((t) => (
                <option key={t.entity_id} value={t.entity_id}>
                  {t.entity_id}
                </option>
              ))}
            </select>
          </label>
          {selectedTeacher && (
            <table>
              <thead>
                <tr>
                  <th>요일</th>
                  <th>교시</th>
                  <th>과목</th>
                  <th>교실</th>
                </tr>
              </thead>
              <tbody>
                {result.teacher_timetables
                  .find((t) => t.entity_id === selectedTeacher)
                  ?.slots.map((s) => (
                    <tr key={`${s.course_id}-${s.day}-${s.period}`}>
                      <td>{s.day}</td>
                      <td>{s.period}</td>
                      <td>{s.course_name}</td>
                      <td>{s.room}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
          )}
        </section>
      )}
    </main>
  );
}
