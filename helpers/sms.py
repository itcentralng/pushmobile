import os

import africastalking
from helpers.payment import generate_ussd_code

class SMS:
    def __init__(self):
        # Set your app credentials
        self.username = os.environ.get("SMS_USERNAME")
        self.api_key = os.environ.get("SMS_API_KEY")
        
        # Initialize the SDK
        africastalking.initialize(self.username, self.api_key)
        
        # Get the SMS service
        self.sms = africastalking.SMS
    
    def send(self, recipient, message):
        # Set your shortCode or senderId
        # sender = os.environ.get("SMS_ID")
        try:
            # print(recipient, message, sender)
            # Thats it, hit send and we'll take care of the rest.
            response = self.sms.send(message, [recipient])
            print (response)
        except Exception as e:
            print ('Encountered an error while sending: %s' % str(e))
    
    def send_bulk(self, recipients, message):
        try:
            # Thats it, hit send and we'll take care of the rest.
            response = self.sms.send(message, recipients)
            print (response)
        except Exception as e:
            print ('Encountered an error while sending: %s' % str(e))

def send_payment_message(customer, delivery, amount):
    sms = SMS()
    ussd = generate_ussd_code(customer.name.split()[0], amount, delivery.payment_option) #"*737*1*5555#"
    if ussd.get('data').get('ussd_code'):
        message = f"Hello {customer.name.split()[0]}, we are processing your order with ID:{delivery.id} & Fees: NGN {amount}.\n{ussd.get('data').get('display_text')}"
        sms.send(customer.phone_number, message)
        return ussd.get('data').get('reference')

def send_success_message(customer, delivery):
    sms = SMS()
    message = f"Hello {customer.name.split()[0]}, we've recieved your payment of {delivery.fees} for order with ID: {delivery.id}.\nOur agent is on the way."
    sms.send(customer.phone_number, message)

def send_welcome_message(customer):
    sms = SMS()
    message = f"Hello there, Welcome to PushMobile. For subsequent usage here's our USSD Code: {os.environ.get('USSD')}"
    sms.send(customer.phone_number, message)