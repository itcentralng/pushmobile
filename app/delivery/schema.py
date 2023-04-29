from app import ma
from app.delivery.model import *

class DeliverySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Delivery
        exclude = ('is_deleted',)