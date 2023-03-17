from db import db

class AppModel(db.Model):
    __tablename__ = "apps"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True,nullable=False)
    description = db.Column(db.String(200),unique=False,nullable=False)
    type = db.Column(db.String(80), unique=False,nullable=False)

    # projects 테이블에서 teams.id 컬럼을 FK로 사용한다.
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), unique=False,nullable=False)
    projects = db.relationship("ProjectModel", back_populates="apps")

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=False)
    users = db.relationship("UserModel", back_populates="apps")
    appsurl = db.relationship("AppUrlModel", back_populates="apps")
