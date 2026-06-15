from __future__ import annotations

import argparse

from sqlalchemy.exc import IntegrityError

from backend.app.models import AnnotationTask, Condition, Image
from experiments.common import add_config_arg, open_session, parse_config


def create_tasks_for_images(db, conditions: list[str]) -> int:
    created = 0
    images = db.query(Image).order_by(Image.id.asc()).all()
    for image in images:
        for condition_name in conditions:
            task = AnnotationTask(image_id=image.id, condition=Condition(condition_name))
            db.add(task)
            try:
                db.commit()
                created += 1
            except IntegrityError:
                db.rollback()
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Create annotation tasks for all configured conditions")
    add_config_arg(parser)
    args = parser.parse_args()
    config = parse_config(args)
    db = open_session(config)
    try:
        created = create_tasks_for_images(db, config.conditions)
    finally:
        db.close()
    print(f"Created {created} annotation tasks")


if __name__ == "__main__":
    main()

