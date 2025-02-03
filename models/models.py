from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
class User(db.Model):
    __tablename__ = 'users'
    id=db.Column(db.Integer,primary_key=True)
    fname=db.Column(db.String(50),nullable=False)
    sname=db.Column(db.String(50),nullable=False)
    email=db.Column(db.String(100),unique=True, nullable=False)
    password=db.Column(db.String(200),nullable=False)
    role_id=db.Column(db.Integer,db.ForeignKey('roles.id'),nullable=False, default=2)
    created_at=db.Column(db.DateTime,server_default=db.func.now())
    # role=db.relationship('Role',backref='users',lazy=True)
    def to_dict(self):
        return {
            'id':self.id,
            'fname':self.fname,
            'sname':self.sname,
            'email':self.email,
            'role_id':self.role_id,
            'created_at':self.created_at,
            # 'role':self.role.name
        }
class Role(db.Model):
    __tablename__ = 'roles'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    created_at=db.Column(db.DateTime,server_default=db.func.now())
    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'created_at':self.created_at
        }
class Destination(db.Model):
    __tablename__ = 'destinations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    safety_rating = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    activities = db.Column(db.String(500), nullable=False)
    image = db.Column(db.String(500), nullable=False)
    # reviews = db.relationship('Review', backref='destination', lazy=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    # wishlists = db.relationship('Wishlist', backref='destination', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'safety_rating': self.safety_rating,
            'location': self.location,
            'activities': self.activities,
            'image': self.image,
            'created_at': self.created_at,
        }

class Guide(db.Model):
    __tablename__ = 'guides'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.String(500), nullable=False)
    languages = db.Column(db.String(200), nullable=False)
    contact_info = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'languages': self.languages,
            'contact_info': self.contact_info,
            'created_at': self.created_at,
        }

# class Review():
#     pass
# class wishlist():
#     pass