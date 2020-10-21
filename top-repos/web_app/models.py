from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


# database object
db = SQLAlchemy()
# migrate object
migrate = Migrate()

# use these
# db.init_app(app)
# migrate.init_app(app, db)

# model creation
# define a new table
# each of these model CLASSES corresponds with a database TABLE
# can define a new class, inherit the db model
# and define attributes, id, name, etc
# PRIMARY KEY will be auto generated and updated for us
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))

class Repos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    repo = db.Column(db.String(120))