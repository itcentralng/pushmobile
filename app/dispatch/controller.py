from flask import Blueprint, request
from app.customer.model import Customer
from app.delivery.model import Delivery, Recipient
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
        if selection.split('*')[-1] == '99':
            return globals()[session.previous](selection=selection, session_id=session_id, customer=customer)
        return globals()[session.stage](selection=selection, session_id=session_id, customer=customer)
    return start(selection=selection, session_id=session_id, customer=customer)

@bp.post('/events')
# @auth_required()
def handle_events():
    form = request.form
    # print(form)
    return "Event Received"

def start(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if pending and text != '99':
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
        Dispatch.create_or_update(kwargs['session_id'], 'select_service', previous='start')
        response = f"CON Hello {kwargs['customer'].name}, welcome to the PUSH MOBILE USSD Platform.\n"
        response += "1. Book Pickup & Delivery\n"
        response += "2. Add Recipient\n"
        response += "3. View Recipients\n"
        response += "4. Delete Recipient\n"
        response += "5. Update Profile\n"
        response += "6. View Profile\n"
    return response

def list_of_recipients(customer_id, index=None):
    try:
        recipients = Recipient.get_by_customer_id(customer_id)
        if index:
            return recipients[int(index)-1]
        text = ""
        for index, recipient in enumerate(recipients):
            text += f"{index+1}. {recipient.name} - {recipient.phone} - {recipient.address} - {recipient.bus_stop}\n\n"
        return text
    except:
        pass

def select_service(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    if text == '1':
        if not list_of_recipients(kwargs['customer'].id):
            return "END You must add at least one recipient to begin"
        Delivery.create(kwargs['customer'].id, stage='select_name', previous='start')
        Dispatch.create_or_update(kwargs['session_id'], 'select_name', 'start')
    elif text == '2':
        Dispatch.create_or_update(kwargs['session_id'], 'add_recipient', 'start')
        return add_recipient_name(**kwargs)
    elif text == '3':
        Dispatch.create_or_update(kwargs['session_id'], 'view_recipients', 'start')
        return view_recipients(**kwargs)
    elif text == '4':
        Dispatch.create_or_update(kwargs['session_id'], 'delete_recipient', 'start')
        return delete_recipient(**kwargs)
    elif text == '5':
        Dispatch.create_or_update(kwargs['session_id'], 'update_profile', 'start')
        return update_profile(**kwargs)
    elif text == '6':
        Dispatch.create_or_update(kwargs['session_id'], 'view_profile', 'start')
        return view_profile(**kwargs)
    return select_name(**kwargs)

def add_recipient_name(**kwargs):
    response = "CON Enter recipient name:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_add_recipient_name', 'start')
    return response

def do_add_recipient_name(**kwargs):
    name = kwargs['selection'].split('*')[-1]
    Recipient.create(kwargs['customer'].id, name)
    Dispatch.create_or_update(kwargs['session_id'], 'add_recipient_phone', 'start')
    return add_recipient_phone(**kwargs)

def add_recipient_phone(**kwargs):
    response = "CON Enter recipient phone:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_add_recipient_phone', 'start')
    return response

def do_add_recipient_phone(**kwargs):
    phone = kwargs['selection'].split('*')[-1]
    recipient = Recipient.get_last_by_customer_id(kwargs['customer'].id)
    recipient.update(phone=phone)
    Dispatch.create_or_update(kwargs['session_id'], 'add_recipient_address', 'start')
    return add_recipient_address(**kwargs)

def add_recipient_address(**kwargs):
    response = "CON Enter recipient address:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_add_recipient_address', 'start')
    return response

def do_add_recipient_address(**kwargs):
    address = kwargs['selection'].split('*')[-1]
    recipient = Recipient.get_last_by_customer_id(kwargs['customer'].id)
    recipient.update(address=address)
    Dispatch.create_or_update(kwargs['session_id'], 'add_recipient_bus_stop', 'start')
    return add_recipient_bus_stop(**kwargs)

def add_recipient_bus_stop(**kwargs):
    response = "CON Enter recipient nearest junction or bus stop:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_add_recipient_bus_stop', 'start')
    return response

def do_add_recipient_bus_stop(**kwargs):
    bus_stop = kwargs['selection'].split('*')[-1]
    recipient = Recipient.get_last_by_customer_id(kwargs['customer'].id)
    recipient.update(bus_stop=bus_stop)
    Dispatch.create_or_update(kwargs['session_id'], 'view_recipients', 'start')
    return view_recipients(**kwargs)

def delete_recipient(**kwargs):
    response = "CON Select Recipient to delete:\n"
    response += list_of_recipients(kwargs['customer'].id)
    Dispatch.create_or_update(kwargs['session_id'], 'do_delete_recipient', 'start')
    return response

def do_delete_recipient(**kwargs):
    selected_recipient = kwargs['selection'].split('*')[-1]
    recipient = list_of_recipients(kwargs['customer'].id, selected_recipient)
    recipient.delete()
    response = "END Recipient deleted successfully!"
    return response

def view_recipients(**kwargs):
    response = "END "
    response += list_of_recipients(kwargs['customer'].id)
    return response

def view_profile(**kwargs):
    response = f"END NAME: {kwargs['customer'].name}\n"
    response += f"ADDRESS: {kwargs['customer'].address}\n"
    response += f"NEAREST BUS STOP: {kwargs['customer'].bus_stop}\n"
    return response

def update_profile(**kwargs):
    Dispatch.create_or_update(kwargs['session_id'], 'select_profile_option', 'start')
    response = f"CON What do you want to update?\n"
    response += "1. Name\n"
    response += "2. Address\n"
    response += "3. Nearest Bus Stop\n"
    response += "99. Back\n"
    return response

def select_profile_option(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    if text == '1':
        Dispatch.create_or_update(kwargs['session_id'], 'update_customer_name', 'start')
        return update_customer_name(**kwargs)
    elif text == '2':
        Dispatch.create_or_update(kwargs['session_id'], 'update_customer_address', 'start')
        return update_customer_address(**kwargs)
    Dispatch.create_or_update(kwargs['session_id'], 'update_customer_bus_stop', 'start')
    return update_customer_bus_stop(**kwargs)

def update_customer_name(**kwargs):
    response = "CON 99. Back\n"
    response = "Please enter your new name:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_update_customer_name', 'start')
    return response

def update_customer_address(**kwargs):
    response = "CON 99. Back\n"
    response = "Please enter your new address:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_update_customer_address', 'start')
    return response

def update_customer_bus_stop(**kwargs):
    response = "CON 99. Back\n"
    response = "Please enter your new bus stop:\n"
    Dispatch.create_or_update(kwargs['session_id'], 'do_update_customer_bus_stop', 'start')
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
        response = "CON 99. Back\n"
        response = 'Please enter your name:\n'
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_address', 'start')
        return response
    else:
        pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
        pending.update(stage='select_pickup_address', previous='start')
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_address', 'start')
        return select_pickup_address(**kwargs)

def select_pickup_address(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    if not text.isdigit():
        kwargs['customer'].update(name=text)
    if not kwargs['customer'].address:
        response = 'CON Please enter your address:\n'
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_bus_stop', 'select_name')
        return response
    else:
        pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
        pending.update(stage='select_pickup_address', pickup=kwargs['customer'].address, previous='select_name')
        Dispatch.create_or_update(kwargs['session_id'], 'select_pickup_bus_stop', 'select_name')
        return select_pickup_bus_stop(**kwargs)

def select_pickup_bus_stop(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not text.isdigit():
        kwargs['customer'].update(address=text)
        pending.update(pickup=kwargs['customer'].address, stage='select_pickup_bus_stop', previous='select_pickup_address')
    if not kwargs['customer'].bus_stop:
        response = 'CON Please enter your nearest bus stop or junction:\n'
        Dispatch.create_or_update(kwargs['session_id'], 'select_item_category', 'select_pickup_address')
        return response
    else:
        pending.update(pickup_bus_stop=kwargs['customer'].bus_stop, stage='select_pickup_bus_stop', previous='select_pickup_address')
        Dispatch.create_or_update(kwargs['session_id'], 'select_item_category', 'select_pickup_address')
        return select_item_category(**kwargs)

categories = {
    '1':'Clothing', 
    '2':'Computer Accessories', 
    '3':'Documents', 
    '4':'Food',
    '5':'Health Products', 
    '6':'Jewelries', 
    '7':'Phones',
    '8':'Others',
    '99':'Back'
    }

types = {
    '1':'Very Small', 
    '2':'Small', 
    '3':'Big', 
    '4':'Very Big',
    '99':'Back',
    }

vehicles = {
    '1':'Bike', 
    '2':'Car', 
    '3':'Bus', 
    '4':'Truck',
    '99':'Back',
    }

def select_item_category(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.pickup:
        return select_pickup_address(**kwargs)
    if not text.isdigit():
        kwargs['customer'].update(bus_stop=text)
        pending.update(pickup_bus_stop=kwargs['customer'].bus_stop, stage='select_item_category', previous='start')
    response = 'CON Select category of item:\n'
    for c in categories:
        response += f'{c}. {categories.get(c)}\n'
    pending.update(stage='select_item_category', previous='start')
    Dispatch.create_or_update(kwargs['session_id'], 'select_item_type', previous='start')
    return response

def select_item_type(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.pickup_bus_stop:
        return select_pickup_bus_stop(**kwargs)
    if text != '99':
        pending.update(item_category=categories[text], stage='select_item_type', previous='select_item_category')
    response = 'CON Select type of item:\n'
    for t in types:
        response += f'{t}. {types.get(t)}\n'
    Dispatch.create_or_update(kwargs['session_id'], 'select_item_unit', previous='select_item_category')
    return response

def select_item_unit(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.item_category:
        return select_item_category(**kwargs)
    if text != '99':
        pending.update(item_type=types[text], stage='select_item_unit', previous='select_item_type')
    response = 'CON 99. Back\n'
    response += 'Please enter item unit(s) e.g 1:\n'
    Dispatch.create_or_update(kwargs['session_id'], 'select_vehicle_type', previous='select_item_type')
    return response

def select_vehicle_type(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.item_type:
        return select_item_type(**kwargs)
    if text != '99':
        pending.update(unit=text, stage='select_vehicle_type', previous='select_item_unit')
    response = 'CON Select preferred vehicle:\n'
    for v in vehicles:
        response += f'{v}. {vehicles.get(v)}\n'
    Dispatch.create_or_update(kwargs['session_id'], 'select_recipient', previous='select_item_unit')
    return response

def select_recipient(**kwargs):
    text = kwargs['selection'].split('*')[-1]
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    if not pending.unit:
        return select_item_unit(**kwargs)
    if text != '99':
        pending.update(vehicle=vehicles[text], stage='select_recipient', previous='select_vehicle_type')
    response = "CON 99. Back\n"
    response += list_of_recipients(kwargs['customer'].id)
    Dispatch.create_or_update(kwargs['session_id'], 'preview_order', previous='select_vehicle_type')
    return response

def preview_order(**kwargs):
    selected_recipient = kwargs['selection'].split('*')[-1]
    recipient = list_of_recipients(kwargs['customer'].id, selected_recipient)
    if not recipient:
        return select_recipient(**kwargs)
    pending = Delivery.get_pending_by_customer_id(kwargs['customer'].id)
    pending.update(delivery_phone_number=recipient.phone, delivery=recipient.address, delivery_bus_stop=recipient.bus_stop, stage='preview_order', status='pending', previous='select_recipient')
    if not pending.delivery or not pending.delivery_phone_number or not pending.delivery_bus_stop:
        return select_recipient(**kwargs)
    response = f"CON Dear {kwargs['customer'].name or 'customer'}\n"
    response += f"We have received your pickup request from {pending.pickup} to {pending.delivery}\n"
    response += "Press:\n"
    response += "1. Continue\n"
    response += "2. Cancel\n"
    response += "99. Back.\n"
    Dispatch.create_or_update(kwargs['session_id'], 'send_final_notification', previous='select_recipient')
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