from flask import Blueprint, request
from app.customer.model import Customer
from app.delivery.model import Delivery
from app.route_guard import auth_required

from app.dispatch.model import *
from app.dispatch.schema import *

bp = Blueprint('dispatch', __name__)

@bp.post('/dispatch')
# @auth_required()
def handle_dispatch():
    serviceCode = request.form.get('serviceCode')
    phone_number = request.form.get('phoneNumber')
    session_id = request.form.get('sessionId')
    networkCode = request.form.get('networkCode')
    selection = request.form.get('text')
    customer = Customer.get_by_phone_number(phone_number)
    if not customer:
        customer = Customer.create(phone_number)
    session = Dispatch.get_by_session_id(session_id)
    if session:
        return globals()[session.stage](selection=selection, session_id=session_id, customer=customer)
    return start(selection=selection, session_id=session_id, customer=customer)

@bp.post('/events')
# @auth_required()
def handle_events():
    form = request.form
    # print(form)
    return "Event Received"

def start(**kwargs):
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if pending:
        text = kwargs['selection'].split('*')[-1]
        if text == '1':
            return globals()[pending.stage](selection=kwargs['selection'], session_id=kwargs['session_id'], customer=kwargs['customer'])
        elif text == '2':
            pending.update(status='cancelled')
            return start(**kwargs)
        else:
            response = f"CON You already have a pending order, do you want to continue?.\n"
            response += "1. Yes\n"
            response += "2. No\n"
    else:
        Dispatch.create_or_update(kwargs['session_id'], 'select_service')
        response = f"CON Hello {kwargs['customer'].name}, welcome to the PUSH MOBILE USSD Platform.\n"
        response += "1. Book Pickup & Delivery\n"
        response += "2. Update Profile\n"
        response += "3. View Profile\n"
    return response

def select_service(**kwargs):
    if kwargs['selection'] == '1':
        Delivery.create(kwargs['customer'].id, stage='select_name')
        Dispatch.create_or_update(kwargs['session_id'], 'select_name')
    elif kwargs['selection'] == '2':
        Dispatch.create_or_update(kwargs['session_id'], 'update_profile')
        return update_profile(**kwargs)
    elif kwargs['selection'] == '3':
        Dispatch.create_or_update(kwargs['session_id'], 'view_profile')
        return view_profile(**kwargs)
    return select_name(**kwargs)

def view_profile(**kwargs):
    response = f"END NAME: {kwargs['customer'].name}\n"
    response += f"ADDRESS: {kwargs['customer'].address}\n"
    response += f"NEAREST BUS STOP: {kwargs['customer'].bus_stop}\n"
    return response

def update_profile(**kwargs):
    Dispatch.create_or_update(kwargs['session_id'], 'select_profile_option')
    response = f"CON What do you want to update?\n"
    response += "1. Name\n"
    response += "2. Address\n"
    response += "3. Nearest Bus Stop\n"
    return response

def select_profile_option(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    if text == '1':
        Dispatch.create_or_update(kwargs['session_id'], 'update_customer_name')
        return update_customer_name(**kwargs)
    elif text == '2':
        Dispatch.create_or_update(kwargs['session_id'], 'update_customer_address')
        return update_customer_address(**kwargs)
    Dispatch.create_or_update(kwargs['session_id'], 'update_customer_bus_stop')
    return update_customer_bus_stop(**kwargs)

def update_customer_name(**kwargs):
    response = "CON Please enter your new name:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_update_customer_name')
    return response

def update_customer_address(**kwargs):
    response = "CON Please enter your new address:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_update_customer_address')
    return response

def update_customer_bus_stop(**kwargs):
    response = "CON Please enter your new bus stop:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_update_customer_bus_stop')
    return response

def do_update_customer_name(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    kwargs['customer'].update(name=text)
    response = "END Your name has been updated successfully\n"
    return response

def do_update_customer_address(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    kwargs['customer'].update(address=text)
    response = "END Your address has been updated successfully\n"
    return response

def do_update_customer_bus_stop(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    kwargs['customer'].update(bus_stop=text)
    response = "END Your bus stop has been updated successfully\n"
    return response

def select_name(**kwargs):
    if not kwargs['customer'].name:
        response = 'CON Please enter your name:\n'
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_address')
        return response
    else:
        pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
        pending.update(stage='select_pickup_address')
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_address')
        return select_pickup_address(**kwargs)

def select_pickup_address(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    if not text.isdigit():
        kwargs['customer'].update(name=text)
    if not kwargs['customer'].address:
        response = 'CON Please enter your address:\n'
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_bus_stop')
        return response
    else:
        pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
        pending.update(stage='select_pickup_address', pickup=kwargs['customer'].address)
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_bus_stop')
        return select_pickup_bus_stop(**kwargs)

def select_pickup_bus_stop(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not text.isdigit():
        kwargs['customer'].update(address=text)
        pending.update(pickup=kwargs['customer'].address, stage='select_pickup_bus_stop')
    if not kwargs['customer'].bus_stop:
        response = 'CON Please enter your nearest bus stop or junction:\n'
        Dispatch.create_or_update(kwargs['session_id'], 'select_item_category')
        return response
    else:
        pending.update(pickup_bus_stop=kwargs['customer'].bus_stop, stage='select_pickup_bus_stop')
        Dispatch.create_or_update(kwargs['session_id'], 'select_item_category')
        return select_item_category(**kwargs)

categories = {
    '1':'Clothing', 
    '2':'Computer Accessories', 
    '3':'Documents', 
    '4':'Food',
    '5':'Health Products', 
    '6':'Jewelries', 
    '7':'Phones',
    '8':'Others'
    }

types = {
    '1':'Very Small', 
    '2':'Small', 
    '3':'Big', 
    '4':'Very Big',
    }

vehicles = {
    '1':'Bike', 
    '2':'Car', 
    '3':'Bus', 
    '4':'Truck',
    }

def select_item_category(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.pickup:
        return select_pickup_address(**kwargs)
    if not text.isdigit():
        kwargs['customer'].update(bus_stop=text)
        pending.update(pickup_bus_stop=kwargs['customer'].bus_stop, stage='select_item_category')
    response = 'CON Select category of item:\n'
    for c in categories:
        response += f'{c}. {categories.get(c)}\n'
    pending.update(stage='select_item_category')
    Dispatch.create_or_update(kwargs['session_id'], 'select_item_type')
    return response

def select_item_type(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.pickup_bus_stop:
        return select_pickup_bus_stop(**kwargs)
    pending.update(item_category=categories[text], stage='select_item_type')
    response = 'CON Select type of item:\n'
    for t in types:
        response += f'{t}. {types.get(t)}\n'
    Dispatch.create_or_update(kwargs['session_id'], 'select_item_unit')
    return response

def select_item_unit(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.item_category:
        return select_item_category(**kwargs)
    pending.update(item_type=types[text], stage='select_item_unit')
    response = 'CON Please enter item unit(s) e.g 1:\n'
    Dispatch.create_or_update(kwargs['session_id'], 'select_vehicle_type')
    return response

def select_vehicle_type(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.item_type:
        return select_item_type(**kwargs)
    pending.update(unit=text, stage='select_vehicle_type')
    response = 'CON Select preferred vehicle:\n'
    for v in vehicles:
        response += f'{v}. {vehicles.get(v)}\n'
    Dispatch.create_or_update(kwargs['session_id'], 'select_delivery_phone_number')
    return response

def select_delivery_phone_number(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.unit:
        return select_item_unit(**kwargs)
    pending.update(vehicle=vehicles[text], stage='select_delivery_phone_number')
    response = "CON Please enter recipient's phone number:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'select_delivery_address')
    return response

def select_delivery_address(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.vehicle:
        return select_vehicle_type(**kwargs)
    pending.update(delivery_phone_number=text, stage='select_delivery_address')
    response = "CON Please enter recipient's address:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'select_delivery_bus_stop')
    return response

def select_delivery_bus_stop(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.delivery_phone_number:
        return select_delivery_phone_number(**kwargs)
    pending.update(delivery=text, stage='select_delivery_bus_stop')
    response = "CON Please enter recipient's nearest bus stop or junction:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'preview_order')
    return response

def preview_order(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.delivery:
        return select_delivery_address(**kwargs)
    if not pending.delivery_phone_number:
        return select_delivery_phone_number(**kwargs)
    pending.update(delivery_bus_stop=text, stage='preview_order', status='pending')
    response = f"CON Dear {kwargs['customer'] or 'customer'}\n"
    response += f"We have received your pickup request from {pending.pickup} to {pending.delivery}\n"
    response += "Press 1 to continue or 2 to cancel.\n"
    Dispatch.create_or_update(kwargs['session_id'], 'complete')
    Dispatch.create_or_update(kwargs['session_id'], 'send_final_notification')
    return response

def send_final_notification(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if text == '1':
        pending.update(delivery_bus_stop=text, stage='complete', status='ready')
        response = "END Thank you for your order\n"
        response += "We will contact you in a few minutes\n"
        Dispatch.create_or_update(kwargs['session_id'], 'complete')
    else:
        response = "END Your request has been cancelled\n"
        response += "Goodbye!!!\n"
        pending.update(delivery_bus_stop=text, stage='complete', status='cancelled')
    return response