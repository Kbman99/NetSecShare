from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask.ext.login import UserMixin
import os
from app import db, bcrypt


class User(db.Model, UserMixin):
    ''' A user who has an account on the website. '''
    __tablename__ = 'users'

    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    email = db.Column(db.String, primary_key=True, unique=True)
    confirmation = db.Column(db.Boolean)
    _password = db.Column(db.String)
    files = relationship("Association", back_populates="user")

    def __init__(self, first_name, last_name, email, password, confirmation):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.confirmation = confirmation
        self.password = password

    @property
    def full_name(self):
        return '{} {}'.format(self.first_name, self.last_name)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def check_password(self, plaintext):
        return bcrypt.check_password_hash(self.password, plaintext.encode('utf-8'))

    def get_id(self):
        return self.email

    def get_files(self):
        return self.files

    def add_files(self, items):
        for file, permission in items:
            self.files.append(Association(permission=permission, file=file, user=self))


class File(db.Model):
    ''' A file which exists '''
    __tablename__ = 'files'

    id = db.Column(db.String, primary_key=True, unique=True)
    file_name = db.Column(db.String, unique=True)
    file_type = db.Column(db.String)
    file_path = db.Column(db.String)
    description = db.Column(db.String)
    thumbnail_path = db.Column(db.String)
    users = relationship("Association", back_populates="file")

    def __init__(self, file_path, description, original_name):
        self.id = os.path.splitext(os.path.basename(file_path))[0]
        self.original_name = original_name
        self.file_type = os.path.splitext(os.path.basename(file_path))[1]
        self.file_name = os.path.basename(file_path)
        self.file_path = file_path
        self.description = description
        self.thumbnail_path = os.path.splitext(file_path)[0] + '_thumbnail.png'
        self.thumbnail_name = os.path.splitext(os.path.basename(file_path))[0] + \
            '_thumbnail.png'

    @property
    def file(self):
        return self.file_name

    def share_file(self, user):
        self.users.append(Association(permission=0, file=self, user=user))


class Association(db.Model):
    ''' Many to Many association for permission handling between a user and a file '''
    __tablename__ = 'association'

    user_id = db.Column(db.String, ForeignKey('users.email'), primary_key=True)
    file_id = db.Column(db.String, ForeignKey('files.id'), primary_key=True)
    permission = db.Column(db.Integer)
    file = relationship("File", back_populates="users")
    user = relationship("User", back_populates="files")
