from app import db

class Delivery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))
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
    stage = db.Column(db.String)
    previous = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now())
    is_deleted = db.Column(db.Boolean, default=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self, item=None, item_category=None, item_type=None, unit=None, vehicle=None, pickup=None, pickup_bus_stop=None, delivery=None, delivery_phone_number=None, delivery_bus_stop=None, status=None, stage=None, previous=None):
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
        self.status = status or self.status
        self.stage = stage or self.stage
        self.previous = previous or self.previous
        self.updated_at = db.func.now()
        db.session.commit()
    
    def delete(self):
        self.is_deleted = True
        self.updated_at = db.func.now()
        db.session.commit()

    @classmethod
    def get_pending_by_customer_id(cls, customer_id):
        return cls.query.filter_by(customer_id=customer_id, status='pending', is_deleted=False).first()
    
    @classmethod
    def get_all(cls):
        return cls.query.filter_by(is_deleted=False).all()
    
    @classmethod
    def create(cls, customer_id=None, item=None, item_category=None, item_type=None, unit=None, vehicle=None, pickup=None, pickup_bus_stop=None, delivery=None, delivery_phone_number=None, delivery_bus_stop=None, status=None, stage=None, previous=None):
        pending = cls.get_pending_by_customer_id(customer_id)
        if not pending:
            delivery = cls(customer_id=customer_id, item=item, item_category=item_category, item_type=item_type, unit=unit, vehicle=vehicle, pickup=pickup, pickup_bus_stop=pickup_bus_stop, delivery=delivery, delivery_phone_number=delivery_phone_number, delivery_bus_stop=delivery_bus_stop, status=status, stage=stage, previous=previous)
            delivery.save()
            return delivery