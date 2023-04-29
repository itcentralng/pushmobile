from app import ma
from app.dispatch.model import *

class DispatchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Dispatch
        exclude = ('is_deleted',)