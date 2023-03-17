from db import db

class ProjectModel(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True,nullable=False)
    description = db.Column(db.String(200),unique=False,nullable=False)
    # projects 테이블에서 teams.id 컬럼을 FK로 사용한다.
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), unique=False,nullable=False)
    teams = db.relationship("TeamModel", back_populates="projects")
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=False)
    users = db.relationship("UserModel", back_populates="projects")

    apps = db.relationship("AppModel", back_populates="projects", cascade="all,delete")
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'team_id': self.team_id,
            'user_id': self.user_id
        }