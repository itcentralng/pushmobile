from app import ma
from app.customer.model import *

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        exclude = ('is_deleted',)