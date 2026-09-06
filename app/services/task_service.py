from sqlalchemy.orm import Session, selectinload

from app.models import Tag, Task


def list_tasks(db: Session) -> list[Task]:
    # 태그를 즉시 로딩합니다. 응답을 직렬화하면서 task.tags에 접근할 때
    # 할 일 개수만큼 태그 조회 쿼리가 추가로 실행되는 것(N+1)을 막습니다.
    tasks = db.query(Task).options(selectinload(Task.tags)).all()
    return tasks


def get_task(db: Session, task_id: int) -> Task | None:
    return db.query(Task).filter(Task.id == task_id).first()


def create_task(db: Session, title: str, tag_names: list[str]) -> Task:
    tags: list[Tag] = []
    for name in tag_names:
        tag = db.query(Tag).filter(Tag.name == name).first()
        if tag is None:
            tag = Tag(name=name)
            db.add(tag)
        tags.append(tag)

    task = Task(title=title, tags=tags)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
