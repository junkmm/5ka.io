from db import db

class TeamModel(db.Model):
    __tablename__ = "teams"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True,nullable=False)
    k8s_cluster_name_for_argo = db.Column(db.String(255), unique=False,nullable=False)
    users = db.relationship("UserModel", back_populates="teams")
    projects = db.relationship("ProjectModel", back_populates="teams", lazy="dynamic", cascade="all,delete")