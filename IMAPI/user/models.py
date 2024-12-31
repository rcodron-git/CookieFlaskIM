# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin
from sqlalchemy.ext.hybrid import hybrid_property

from IMAPI.database import Column, PkModel, db, reference_col, relationship
from IMAPI.extensions import bcrypt
# models.py
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

#db = SQLAlchemy()

class Role(PkModel):
    """A role for a user."""

    __tablename__ = "roles"
    name = Column(db.String(80), unique=True, nullable=False)
    user_id = reference_col("users", nullable=True)
    user = relationship("User", backref="roles")

    def __init__(self, name, **kwargs):
        """Create instance."""
        super().__init__(name=name, **kwargs)

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<Role({self.name})>"


class User(UserMixin, PkModel):
    """A user of the app."""

    __tablename__ = "users"
    username = Column(db.String(80), unique=True, nullable=False)
    email = Column(db.String(80), unique=True, nullable=False)
    _password = Column("password", db.LargeBinary(128), nullable=True)
    created_at = Column(
        db.DateTime, nullable=False, default=dt.datetime.now(dt.timezone.utc)
    )
    first_name = Column(db.String(30), nullable=True)
    last_name = Column(db.String(30), nullable=True)
    active = Column(db.Boolean(), default=False)
    is_admin = Column(db.Boolean(), default=False)

    @hybrid_property
    def password(self):
        """Hashed password."""
        return self._password

    @password.setter
    def password(self, value):
        """Set password."""
        self._password = bcrypt.generate_password_hash(value)

    def check_password(self, value):
        """Check password."""
        return bcrypt.check_password_hash(self._password, value)

    @property
    def full_name(self):
        """Full user name."""
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        """Represent instance as a unique string."""
        return f"<User({self.username!r})>"



class Catalog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=True)
    category = db.Column(db.String(255), nullable=True)
    subCategory = db.Column(db.String(255), nullable=True)
    productType = db.Column(db.String(255), nullable=True)
    ingramPartNumber = db.Column(db.String(255), nullable=False)
    vendorPartNumber = db.Column(db.String(255), nullable=True)
    upcCode = db.Column(db.String(255), nullable=True)
    vendorName = db.Column(db.String(255), nullable=True)
    endUserRequired = db.Column(db.Boolean, default=False)
    hasDiscounts = db.Column(db.Boolean, default=False)
    sku_type = db.Column(db.String(255), nullable=True)
    discontinued = db.Column(db.Boolean, default=False)
    newProduct = db.Column(db.Boolean, default=False)
    directShip = db.Column(db.Boolean, default=False)
    hasWarranty = db.Column(db.Boolean, default=False)
    extraDescription = db.Column(db.Text, nullable=True)
    replacementSku = db.Column(db.String(255), nullable=True)
    authorizedToPurchase = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Catalog {self.description}>'

    @validates('description')
    def validate_description(self, key, description):
        if len(description) > 500:
            raise ValueError('Description cannot exceed 500 characters.')
        return description

    def save(self):
        self.full_clean()
        db.session.add(self)
        db.session.commit()

    def full_clean(self):
        self.validate_description('description', self.description)
