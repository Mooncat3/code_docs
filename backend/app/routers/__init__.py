from sqlalchemy import and_, or_
from app.models.project import Project as DBProject
from app.models.file import CodeFile as DBFile
from app.models.documentation import CodeEntity as DBEntity


def get_project(db, project_id, current_user):
    if current_user is not None:
        return db.query(DBProject).filter(
            and_(DBProject.id == project_id,
                 or_(DBProject.is_public, DBProject.owner_id == current_user.id))
        ).first()
    return db.query(DBProject).filter(
        and_(DBProject.id == project_id, DBProject.is_public)
    ).first()


def get_file(db, file_id, current_user):
    if current_user is not None:
        return db.query(DBFile).join(DBProject).filter(
            and_(DBFile.id == file_id,
                 or_(DBProject.is_public, DBProject.owner_id == current_user.id))
        ).first()
    return db.query(DBFile).join(DBProject).filter(
        and_(DBFile.id == file_id, DBProject.is_public)
    ).first()


def get_entity(db, entity_id, current_user):
    if current_user is not None:
        return db.query(DBEntity).join(DBFile).join(DBProject).filter(
            and_(DBEntity.id == entity_id,
                 or_(DBProject.is_public,
                     DBProject.owner_id == current_user.id))
        ).first()
    return db.query(DBEntity).join(DBFile).join(DBProject).filter(
        and_(DBEntity.id == entity_id, DBProject.is_public)
    ).first()
