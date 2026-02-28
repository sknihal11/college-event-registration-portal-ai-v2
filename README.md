\# EventFlow AI - College Event Registration Portal



A Django-based AI-powered college event registration and management system.



\## Features

\- User authentication (signup/login/logout)

\- Event creation and registration

\- AI recommendations (based on past registrations)

\- QR pass generation

\- Staff/Admin QR verification (duplicate scan blocking)

\- Attendance tracking

\- Analytics dashboard

\- CSV export (admin)



\## Local Setup (Windows)

```powershell

git clone https://github.com/sknihal11/college-event-registration-portal-ai-v2.git

cd college-event-registration-portal-ai-v2

python -m venv venv

venv\\Scripts\\activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

pip install django pillow scikit-learn matplotlib qrcode(OPTIONAL-RUN ONLY IF YOU GET MODULE NOT PRESENT ERROR,REQUIREMENTS.TXT HAS ALL THE REQUIRED MODULES)

URLs



App: http://127.0.0.1:8000/



Admin: http://127.0.0.1:8000/admin/

