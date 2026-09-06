from sqlalchemy import event


def test_list_tasks_loads_tags_in_constant_queries(client, db_session):
    for i in range(5):
        res = client.post("/tasks", json={"title": f"할 일 {i}", "tags": [f"태그{i}"]})
        assert res.status_code == 201

    # POST 응답을 만들면서 로딩된 tags가 세션에 남아 있으면 N+1이 가려집니다.
    db_session.expire_all()

    statements: list[str] = []
    engine = db_session.get_bind()

    @event.listens_for(engine, "before_cursor_execute")
    def record(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    try:
        res = client.get("/tasks")
    finally:
        event.remove(engine, "before_cursor_execute", record)

    assert res.status_code == 200
    assert len(res.json()) == 5
    # 태그를 즉시 로딩하면 할 일 개수와 무관하게 쿼리 수가 일정합니다.
    assert len(statements) == 2, statements
