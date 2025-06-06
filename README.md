
# PARiS Tours & Travels - Backend (Django + DRF)

This is the backend of the **PARiS Tours & Travels** application, built with Django and Django REST Framework (DRF), providing APIs and backend functionalities for the travel service.

---

## 🌐 Project Structure

```
paris/
├── admin_user/           # Admin-related functionality
├── flights/              # Flight booking and management
├── messege/              # Messaging and chat system (WebSocket)
├── node_modules/         # Node modules for JS dependencies
├── packages/             # Holiday packages
├── paris/                # Main project settings and URLs
├── payments/             # Payment integrations (e.g., Stripe)
├── profileapp/           # User profile management
├── resorts/              # Resort bookings
├── users/                # Custom user model and auth
├── visas/                # Visa application and status
├── .env                  # Environment variables
├── db.sqlite3            # SQLite database (development)
├── manage.py             # Django entry point
├── README.md             # Project documentation
├── requirements.txt      # Python dependencies
```

---

## ⚙️ Features

- **JWT Authentication** with SimpleJWT
- **Google OAuth2** Login with `django-allauth`
- **Real-time Chat** using Django Channels + Redis
- **Session Caching** via Redis
- **Stripe Payments** integration
- **SMS** via Twilio
- **CORS** and CSRF protection for secure API communication

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/jasirck/PARiS-BackEnd.git
cd PARiS-BackEnd
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Set up `.env` File
Create a `.env` file in the root directory and add:

```
SECRET_KEY=your_secret_key
DEBUG=True
DB_NAME=your_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth
TWILIO_PHONE_NUMBER=your_twilio_phone
TWILIO_WHATSAPP_NUMBER=your_whatsapp_number

STRIPE_TEST_SECRET_KEY=your_stripe_secret
STRIPE_TEST_PUBLISHABLE_KEY=your_stripe_key

cloud_name=your_cloudinary_name
api_key=your_cloudinary_key
api_secret=your_cloudinary_secret

FACEBOOK_APP_SECRET=your_fb_app_secret
```

### 5. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

---

## 🔌 Run with Daphne (ASGI for WebSockets)
```bash
daphne -b 0.0.0.0 -p 8000 paris.asgi:application
```


---

## ✉️ Contact

For inquiries or support, please contact **Muhammed Jasir CK**  
Email: `muhammedjasirck07@gmail.com`
 
Python Full Stack Developer  
📫 [LinkedIn](www.linkedin.com/in/muhammed-jasir-ck-561912307) | [GitHub](https://github.com/jasirck/)

