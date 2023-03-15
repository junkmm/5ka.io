from db import db

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    email  = db.Column(db.String(80), nullable=False)
    # users 테이블에서 teams.id 컬럼을 FK로 사용한다.
    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False, unique=False)

    # users 테이블에서 teams 모델을 참조한다.
    teams = db.relationship("TeamModel", back_populates="users")
    projects = db.relationship("ProjectModel", back_populates="users", lazy="dynamic")