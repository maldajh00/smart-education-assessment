def test_courses_list(client, requires_db):
    r = client.get("/api/courses")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)
    if body:
        item = body[0]
        assert {"id", "title", "category", "instructor_name", "description", "student_count"} <= set(item)


def test_instructors_list(client, requires_db):
    r = client.get("/api/instructors")
    assert r.status_code == 200
    body = r.json()
    assert isinstance(body, list)


def test_statistics(client, requires_db):
    r = client.get("/api/statistics")
    assert r.status_code == 200
    body = r.json()
    assert body["version"] == "1.0.0"
    for key in ("total_courses", "total_instructors", "total_students", "total_enrollments"):
        assert isinstance(body[key], int)


def test_course_detail_not_found(client, requires_db):
    r = client.get("/api/courses/999999")
    assert r.status_code == 404


def test_instructor_detail_not_found(client, requires_db):
    r = client.get("/api/instructors/999999")
    assert r.status_code == 404
