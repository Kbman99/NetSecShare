from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask.ext.login import UserMixin
import json

from app import db, bcrypt


class User(db.Model, UserMixin):

    ''' A user who has an account on the website. '''

    __tablename__ = 'users'

    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
#    phone = db.Column(db.String)
    email = db.Column(db.String, primary_key=True)
    confirmation = db.Column(db.Boolean)
    _password = db.Column(db.String)
#    permitted_files = db.Column(JsonEncodedDict)
    files = relationship("Association", back_populates="user")

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
        return bcrypt.check_password_hash(self.password, plaintext)

    def get_id(self):
        return self.email

    def get_permissions(self, value):
        return self.permitted_files


class File(db.Model):

    ''' A file which exists '''

    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String)
    file_type = db.Column
    users = relationship("Association", back_populates="file")


class Association(db.Model):

    ''' Many to Many association for permission handling between a user and a file '''

    __tablename__ = 'association'

    user_id = db.Column(db.String, ForeignKey('users.email'), primary_key=True)
    file_id = db.Column(db.String, ForeignKey('files.id'), primary_key=True)
    permission = db.Column(db.Integer)
    file = relationship("File", back_populates="users")
    user = relationship("User", back_populates="files")