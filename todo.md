
TODO:
NONE

PAYMENTS:
  check manually via admin. Send payment invoices via email.

HOSTING:
  Django - Self-hosted
  Email - Brevo

STACK:
  Django
  Nginx
  Brevo SMTP

Deployment needs:
  redis
  //worker
  celery -A core worker --pool=solo --loglevel=info
  //scheduler
  celery -A core beat --loglevel=info

for rate limiting with ip - if your application is running behind a reverse proxy such as nginx or HAProxy, you will need to take steps to ensure you have access to the correct client IP address, rather than the address of the proxy.

Prod checklist:
1) Set DEBUG to FALSE
2) redis on
3) collect static
4) makemigrations + migrate
5) nginx
6) celery worker daemon
7) manage.py runserver