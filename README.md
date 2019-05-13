# tournament

Tournament is Django app that allows sport competition organization, registration and tracking results. This is a recruitment task, I developed it on company's gitlab and pushed final version to my github - that's why it has a few commits.

## Features
### User - organizer/competitor
- User registration with confirmation email,
- User profile edition,
- Password change,
- Forgot password reminder

### Competition - event
- Event creation and modification,
- Event registration with confirmation email

###Features that are not finished

- Match result tree creation (works only under certain conditions),
- Adding match result (works only under certain conditions)

### Pre requisites
- Django 2.1.7
- Python 3.6.7
- Pillow 5.4.1
- PostgreSQL 10.6
- psycopg2-binary 2.7.7
- pytz 2018.9
- sorl-thumbnail 12.5.0

#### Setup

- Install Python 3.6.7
- Install PostgreSQL 10.6
- Create Database - PostgreSQL (required - database(name), user(name), password(name))
- ```$ mkdir project```
- ```$ cd project```
- Create new virtual environment
- Clone repository
- ```pip install -r requirements.txt```

Change file ```settings.py```:
- Change database settings
```
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'database(name)',
        'USER': 'user(name)',
        'PASSWORD': 'user(password)',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}
```
- Change Email settings (use gmail account):
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'email'
EMAIL_HOST_PASSWORD = 'email_password'
```
- ```$ cd comptab```
- Run command: ```python manage.py migrate```
- Run command: ```python manage.py runserver```
- Open web browser at address ```http://127.0.0.1:8000/```
