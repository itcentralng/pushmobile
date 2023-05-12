from app import db
from helpers.sms import send_welcome_message

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    address = db.Column(db.String)
    bus_stop = db.Column(db.String)
    phone_number = db.Column(db.String, unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, name=None, address=None, bus_stop=None):
        self.name = name or self.name
        self.address = address or self.address
        self.bus_stop = bus_stop or self.bus_stop
        self.updated_at = db.func.now()
        db.session.commit()
    
    def delete(self):
        self.is_deleted = True
        self.updated_at = db.func.now()
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.filter_by(id=id, is_deleted=False).first()
    
    @classmethod
    def get_by_phone_number(cls, phone_number):
        return cls.query.filter_by(phone_number=phone_number, is_deleted=False).first()
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(is_deleted=False).all()
    
    @classmethod
    def create(cls, phone_number, name='', address='', bus_stop=''):
        customer = cls(phone_number=phone_number, name=name, address=address, bus_stop=bus_stop)
        customer.save()
        send_welcome_message(customer)
        return customer