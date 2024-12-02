from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from users.views import SendOtpView, VerifyOtpView

class OTPTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.phone_number = '1234567890'

        # Helper function to add session to a request
        def add_session(request):
            middleware = SessionMiddleware(get_response=lambda r: None)
            middleware.process_request(request)
            request.session.save()
            return request

        # Set up SendOtpView request
        self.send_request = self.factory.post('/api/user/send-otp', {'phone_number': self.phone_number})
        self.send_request = add_session(self.send_request)

        # Call SendOtpView
        send_view = SendOtpView.as_view()
        response = send_view(self.send_request)
        self.assertEqual(response.status_code, 200)
        self.otp = self.send_request.session['otp']  # Save the generated OTP for later use

    def test_verify_otp(self):
        # Set up VerifyOtpView request with the correct OTP
        verify_request = self.factory.post('/api/user/verify-otp', {'otp': str(self.otp)})
        verify_request.session = self.send_request.session  # Share session with the verify request

        # Call VerifyOtpView
        verify_view = VerifyOtpView.as_view()
        response = verify_view(verify_request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['message'], 'OTP verified successfully')

        # Test with an incorrect OTP
        wrong_request = self.factory.post('/api/user/verify-otp', {'otp': '123456'})
        wrong_request.session = self.send_request.session
        wrong_response = verify_view(wrong_request)
        self.assertEqual(wrong_response.status_code, 400)
        self.assertEqual(wrong_response.data['error'], 'Incorrect OTP')
