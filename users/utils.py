import random
from twilio.rest import Client
from django.conf import settings

def send_otp(phone_number):
    # Generate a 6-digit OTP
    otp = random.randint(100000, 999999)

    # Twilio Client Initialization
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    try:
        # Ensure the 'From' number is a valid Twilio number from your account
        from_ = settings.TWILIO_PHONE_NUMBER  # This should be a valid Twilio number
        
        # Ensure the phone number includes the country code, e.g., +91 for India
        to_ = f"+91{phone_number}"

        # Sending the OTP via SMS
        message = client.messages.create(
            body=f'''
            
            PARiS Tours & Travels
            Your OTP is {otp}''',

            from_=from_,
            to=to_
        )
        print(f"Sent message SID: {message.sid}")
        return otp  # Return OTP for further verification
    except Exception as e:
        print(f"Error sending OTP: {e}")
        return None