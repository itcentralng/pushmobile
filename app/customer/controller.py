from flask import Blueprint
from app.route_guard import auth_required

from app.customer.model import *
from app.customer.schema import *

bp = Blueprint('customer', __name__)

@bp.post('/customer')
@auth_required('admin')
def create_customer():
    customer = Customer.create()
    return CustomerSchema().dump(customer), 201

@bp.get('/customer/<int:id>')
@auth_required('admin')
def get_customer(id):
    customer = Customer.get_by_id(id)
    if customer is None:
        return {'message': 'Customer not found'}, 404
    return CustomerSchema().dump(customer), 200

@bp.patch('/customer/<int:id>')
@auth_required('admin')
def update_customer(id):
    customer = Customer.get_by_id(id)
    if customer is None:
        return {'message': 'Customer not found'}, 404
    customer.update()
    return CustomerSchema().dump(customer), 200

@bp.delete('/customer/<int:id>')
@auth_required('admin')
def delete_customer(id):
    customer = Customer.get_by_id(id)
    if customer is None:
        return {'message': 'Customer not found'}, 404
    customer.delete()
    return {'message': 'Customer deleted successfully'}, 200

@bp.get('/customers')
@auth_required('admin')
def get_customers():
    customers = Customer.get_all()
    return CustomerSchema(many=True).dump(customers), 200