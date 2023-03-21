from db import db

class AppUrlModel(db.Model):
    __tablename__ = "appsurl"

    id = db.Column(db.Integer, primary_key=True)
    gitlab_source = db.Column(db.String(200), unique=False,nullable=False)
    gitlab_helm = db.Column(db.String(200), unique=False,nullable=False)
    jenkins = db.Column(db.String(200),unique=False,nullable=False)
    argocd = db.Column(db.String(200),unique=False,nullable=False)
    kibana = db.Column(db.String(200),unique=False,nullable=False)
    grafana = db.Column(db.String(200),unique=False,nullable=False)
    app_id = db.Column(db.Integer, db.ForeignKey("apps.id"), unique=False,nullable=False)
    apps = db.relationship("AppModel", back_populates="appsurl")