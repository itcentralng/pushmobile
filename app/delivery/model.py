from sqlalchemy import desc, or_
from app import db
from app.customer.model import Customer
from helpers.sms import send_payment_message, send_success_message

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    pickup_name = db.Column(db.String)
    pickup_phone_number = db.Column(db.String)
    delivery_name = db.Column(db.String)
    item = db.Column(db.String)
    item_category = db.Column(db.String)
    item_type = db.Column(db.String)
    unit = db.Column(db.String)
    pickup = db.Column(db.String)
    pickup_bus_stop = db.Column(db.String)
    delivery = db.Column(db.String)
    delivery_phone_number = db.Column(db.String)
    vehicle = db.Column(db.String)
    delivery_bus_stop = db.Column(db.String)
    status = db.Column(db.String, default='pending')
    fees = db.Column(db.Float, default=0.0)
    payment_status = db.Column(db.String, default='pending')
    payment_reference = db.Column(db.String)
    payment_option = db.Column(db.String)
    stage = db.Column(db.String)
    previous = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, pickup_name=None, pickup_phone_number=None, delivery_name=None, item=None, item_category=None, item_type=None, unit=None, vehicle=None, pickup=None, pickup_bus_stop=None, delivery=None, delivery_phone_number=None, delivery_bus_stop=None, payment_option=None, status=None, stage=None, previous=None):
        self.pickup_phone_number = pickup_phone_number or self.pickup_phone_number
        self.pickup_name = pickup_name or self.pickup_name
        self.delivery_name = delivery_name or self.delivery_name
        self.item = item or self.item
        self.item_category = item_category or self.item_category
        self.item_type = item_type or self.item_type
        self.unit = unit or self.unit
        self.vehicle = vehicle or self.vehicle
        self.pickup = pickup or self.pickup
        self.pickup_bus_stop = pickup_bus_stop or self.pickup_bus_stop
        self.delivery = delivery or self.delivery
        self.delivery_phone_number = delivery_phone_number or self.delivery_phone_number
        self.delivery_bus_stop = delivery_bus_stop or self.delivery_bus_stop
        self.payment_option = payment_option or self.payment_option
        self.status = status or self.status
        self.stage = stage or self.stage
        self.previous = previous or self.previous
        self.updated_at = db.func.now()
        db.session.commit()
    
    def delete(self):
        self.is_deleted = True
        self.updated_at = db.func.now()
        db.session.commit()

    def set_fees(self, amount):
        self.fees = amount
        # send an sms to the User with a USSD code to dail for payment
        payment_reference = send_payment_message(Customer.get_by_id(self.customer_id), self, amount)
        self.payment_reference = payment_reference
        self.payment_status = 'invoice'
        db.session.commit()
        if self.payment_reference:
            return True
        return False
    
    def validate_payment(self):
        self.payment_status = 'paid'
        self.status = 'transit'
        send_success_message(Customer.get_by_id(self.customer_id), self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
    
    @classmethod
    def get_by_payment_reference(cls, reference):
        return cls.query.filter_by(payment_reference=reference).first()

    @classmethod
    def get_pending_by_customer_id(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id, status='pending', is_deleted=False).first()
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(is_deleted=False).order_by(desc(cls.id)).all()
    
    @classmethod
    def create(cls, customer_id=None, item=None, item_category=None, item_type=None, unit=None, vehicle=None, pickup=None, pickup_bus_stop=None, delivery=None, delivery_phone_number=None, delivery_bus_stop=None, status=None, stage=None, previous=None):
        pending = cls.get_pending_by_customer_id(customer_id)
        if not pending:
            delivery = cls(customer_id=customer_id, item=item, item_category=item_category, item_type=item_type, unit=unit, vehicle=vehicle, pickup=pickup, pickup_bus_stop=pickup_bus_stop, delivery=delivery, delivery_phone_number=delivery_phone_number, delivery_bus_stop=delivery_bus_stop, status=status, stage=stage, previous=previous)
            delivery.save()
            return delivery
        
class Recipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
    name = db.Column(db.String)
    phone = db.Column(db.String)
    address = db.Column(db.String)
    bus_stop = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, name=None, phone=None, address=None, bus_stop=None):
        self.name = name or self.name
        self.phone = phone or self.phone
        self.address = address or self.address
        self.bus_stop = bus_stop or self.bus_stop
        db.session.commit()
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_customer_id(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id).all()
    
    @classmethod
    def get_incomplete_by_customer_id(cls, customer_id):
        return cls.query.filter(cls.customer_id==customer_id, or_(cls.name==None, cls.address==None, cls.phone==None, cls.bus_stop==None)).first()
    
    @classmethod
    def get_last_by_customer_id(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id).order_by(desc(cls.id)).first()
    
    @classmethod
    def create(cls, customer_id=None, name=None, phone=None, address=None, bus_stop=None):
        recipients = cls.get_by_customer_id(customer_id)
        incomplete = cls.get_incomplete_by_customer_id(customer_id)
        if incomplete:
            incomplete.update(name, phone, address, bus_stop)
            return incomplete
        elif len(recipients) < 10:
            recipient = cls(customer_id=customer_id, name=name, phone=phone, address=address, bus_stop=bus_stop)
            recipient.save()
            return recipient
        else:
            recipients[-1].update(name, phone, address, bus_stop)
            return recipients[-1]