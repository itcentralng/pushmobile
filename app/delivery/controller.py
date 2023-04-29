from flask import Blueprint
from app.route_guard import auth_required

from app.delivery.model import *
from app.delivery.schema import *

bp = Blueprint('delivery', __name__)

@bp.post('/delivery')
@auth_required()
def create_delivery():
    delivery = Delivery.create()
    return DeliverySchema().dump(delivery), 201

@bp.get('/delivery/<int:id>')
@auth_required()
def get_delivery(id):
    delivery = Delivery.get_by_id(id)
    if delivery is None:
        return {'message': 'Delivery not found'}, 404
    return DeliverySchema().dump(delivery), 200

@bp.patch('/delivery/<int:id>')
@auth_required()
def update_delivery(id):
    delivery = Delivery.get_by_id(id)
    if delivery is None:
        return {'message': 'Delivery not found'}, 404
    delivery.update()
    return DeliverySchema().dump(delivery), 200

@bp.delete('/delivery/<int:id>')
@auth_required()
def delete_delivery(id):
    delivery = Delivery.get_by_id(id)
    if delivery is None:
        return {'message': 'Delivery not found'}, 404
    delivery.delete()
    return {'message': 'Delivery deleted successfully'}, 200

@bp.get('/deliverys')
@auth_required()
def get_deliverys():
    deliverys = Delivery.get_all()
    return DeliverySchema(many=True).dump(deliverys), 200