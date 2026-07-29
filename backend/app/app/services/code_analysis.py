from app.utils.helpers import detect_language
from app.utils.parse_code_entities import parse_code_entities
from app.models.documentation import CodeEntity
from app.models.file import CodeFile
from sqlalchemy.orm import Session
from uuid import UUID


def process_uploaded_file(db: Session, file_content: str, filename: str, project_id: UUID):
    language = detect_language(filename, file_content)

    db_file = CodeFile(
        filename=filename,
        language=language,
        original_content=file_content,
        project_id=project_id
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    entities = parse_code_entities(file_content, language)

    for entity in entities:
        db_entity = CodeEntity(
            name=entity["name"],
            type=entity["type"],
            line_start=entity["line_start"],
            line_end=entity["line_end"],
            file_id=db_file.id,
            original_docs=entity["docstring"]
        )
        db.add(db_entity)

    db.commit()
    return db_file
