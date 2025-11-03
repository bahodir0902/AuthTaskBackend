# flake8: noqa

import logging

from celery import shared_task
from decouple import config
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)
OTP_LEN = config("OTP_LEN", cast=int, default=6)
FROM_EMAIL = settings.EMAIL_HOST_USER


@shared_task(bind=True, max_retries=3)
def send_email_verification_task(self, receiver_email, first_name, code):
    """
    Celery task to send email verification
    """
    try:
        subject = "Подтверждение электронной почты"
        text_content = f"""
        Здравствуйте, {first_name}!

        Спасибо за регистрацию! Для подтверждения вашего аккаунта, пожалуйста, верифицируйте адрес электронной почты.

        Ваш {OTP_LEN}-значный код подтверждения: {code}

        Введите этот код на нашем сайте, чтобы завершить процесс верификации.

        Если вы не запрашивали это письмо, просто проигнорируйте его.

        С уважением,
        Команда вашей компании
        """

        from_email = FROM_EMAIL
        to = [receiver_email]
        html_content = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 20px;">
    <div style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.08);">

      <!-- Header -->
      <div style="background:linear-gradient(135deg, #667eea 0%, #764ba2 100%);padding:50px 40px;text-align:center;">
        <div style="width:90px;height:90px;background:rgba(255,255,255,0.25);border-radius:50%;margin:0 auto 24px;display:inline-flex;align-items:center;justify-content:center;backdrop-filter:blur(10px);border:3px solid rgba(255,255,255,0.3);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style="display:block;">
            <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" fill="#ffffff"/>
          </svg>
        </div>
        <h1 style="margin:0;font-size:32px;font-weight:700;color:#ffffff;letter-spacing:-0.8px;">Подтвердите почту</h1>
        <p style="margin:12px 0 0;font-size:16px;color:rgba(255,255,255,0.95);font-weight:400;">Завершите регистрацию</p>
      </div>

      <!-- Content -->
      <div style="padding:48px 40px;">
        <p style="margin:0 0 16px;font-size:18px;line-height:1.6;color:#0f172a;font-weight:600;">
          Привет, {first_name}! 👋
        </p>
        <p style="margin:0 0 32px;font-size:16px;line-height:1.7;color:#475569;">
          Благодарим за регистрацию! Введите код ниже, чтобы подтвердить свой email и получить доступ ко всем функциям платформы.
        </p>

        <!-- Code Box -->
        <div style="background:linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);border:3px solid #667eea;border-radius:16px;padding:36px;text-align:center;margin:0 0 32px;position:relative;">
          <div style="font-size:13px;font-weight:700;color:#667eea;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">Ваш код</div>
          <div style="font-size:52px;font-weight:800;color:#667eea;letter-spacing:12px;font-family:'Courier New',monospace;">{code}</div>
          <div style="margin-top:16px;font-size:13px;color:#64748b;">Код действителен 5 минут</div>
        </div>

        <!-- Info Box -->
        <div style="background:#fef9c3;border-left:4px solid #eab308;border-radius:12px;padding:20px 24px;margin:0 0 32px;">
          <p style="margin:0;font-size:14px;line-height:1.7;color:#713f12;">
            <strong style="color:#854d0e;display:block;margin-bottom:4px;">⚠️ Безопасность превыше всего</strong>
            Никогда не передавайте этот код третьим лицам. Наша команда никогда не попросит вас сообщить код верификации.
          </p>
        </div>

        <p style="margin:0;font-size:14px;line-height:1.6;color:#64748b;text-align:center;">
          Не регистрировались на нашей платформе? Просто проигнорируйте это письмо.
        </p>
      </div>

      <!-- Footer -->
      <div style="background:#f8fafc;padding:32px 40px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="margin:0 0 12px;font-size:13px;color:#64748b;">
          Нужна помощь? <a href="mailto:support@yourcompany.com" style="color:#667eea;text-decoration:none;font-weight:600;">Свяжитесь с нами</a>
        </p>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          С уважением,<br><strong style="color:#475569;">Команда вашей компании</strong>
        </p>
        <p style="margin:16px 0 0;font-size:12px;color:#cbd5e1;">
          © 2025 Ваша компания. Все права защищены.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email verification sent successfully to {receiver_email}")
        return f"Email sent to {receiver_email}"

    except Exception as exc:
        logger.error(f"Failed to send email verification to {receiver_email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_password_verification_task(self, email, first_name, code):
    """
    Celery task to send password reset verification
    """
    try:
        subject = "Сброс пароля"
        to = [email]
        from_email = FROM_EMAIL

        text_content = f"""
        Здравствуйте, {first_name}!

        Мы получили запрос на сброс пароля для вашего аккаунта.

        Ваш {OTP_LEN}-значный код сброса пароля: {code}

        Введите этот код на нашем сайте, чтобы установить новый пароль.

        Если вы не запрашивали сброс пароля, вы можете спокойно проигнорировать это письмо и никакие изменения не будут внесены.

        В целях безопасности не сообщайте этот код никому. Если вам нужна помощь, пожалуйста, свяжитесь с нашей службой поддержки.

        С уважением,
        Команда вашей компании
        """

        html_content = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 20px;">
    <div style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.08);">

      <!-- Header -->
      <div style="background:linear-gradient(135deg, #f59e0b 0%, #ef4444 100%);padding:50px 40px;text-align:center;">
        <div style="width:90px;height:90px;background:rgba(255,255,255,0.25);border-radius:50%;margin:0 auto 24px;display:inline-flex;align-items:center;justify-content:center;backdrop-filter:blur(10px);border:3px solid rgba(255,255,255,0.3);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style="display:block;">
            <path d="M18 8h-1V6c0-2.76-2.24-5-5-5S7 3.24 7 6v2H6c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V10c0-1.1-.9-2-2-2zm-6 9c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-9H8.9V6c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z" fill="#ffffff"/>
          </svg>
        </div>
        <h1 style="margin:0;font-size:32px;font-weight:700;color:#ffffff;letter-spacing:-0.8px;">Сброс пароля</h1>
        <p style="margin:12px 0 0;font-size:16px;color:rgba(255,255,255,0.95);font-weight:400;">Восстановите доступ</p>
      </div>

      <!-- Content -->
      <div style="padding:48px 40px;">
        <p style="margin:0 0 16px;font-size:18px;line-height:1.6;color:#0f172a;font-weight:600;">
          Привет, {first_name}! 👋
        </p>
        <p style="margin:0 0 32px;font-size:16px;line-height:1.7;color:#475569;">
          Получен запрос на сброс пароля для вашего аккаунта. Используйте код ниже, чтобы установить новый пароль и восстановить доступ.
        </p>

        <!-- Code Box -->
        <div style="background:linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);border:3px solid #f59e0b;border-radius:16px;padding:36px;text-align:center;margin:0 0 32px;position:relative;">
          <div style="font-size:13px;font-weight:700;color:#f59e0b;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">Код сброса</div>
          <div style="font-size:52px;font-weight:800;color:#f59e0b;letter-spacing:12px;font-family:'Courier New',monospace;">{code}</div>
          <div style="margin-top:16px;font-size:13px;color:#92400e;">Код действителен 5 минут</div>
        </div>

        <!-- Warning Box -->
        <div style="background:#fee2e2;border-left:4px solid #ef4444;border-radius:12px;padding:20px 24px;margin:0 0 32px;">
          <p style="margin:0;font-size:14px;line-height:1.7;color:#7f1d1d;">
            <strong style="color:#991b1b;display:block;margin-bottom:4px;">🔒 Важно для безопасности</strong>
            Храните код в секрете. Если вы не запрашивали сброс пароля, немедленно свяжитесь с нашей службой поддержки.
          </p>
        </div>

        <p style="margin:0;font-size:14px;line-height:1.6;color:#64748b;text-align:center;">
          Не запрашивали сброс? Проигнорируйте письмо — ваш пароль останется без изменений.
        </p>
      </div>

      <!-- Footer -->
      <div style="background:#f8fafc;padding:32px 40px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="margin:0 0 12px;font-size:13px;color:#64748b;">
          Нужна помощь? <a href="mailto:support@yourcompany.com" style="color:#f59e0b;text-decoration:none;font-weight:600;">Свяжитесь с нами</a>
        </p>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          С уважением,<br><strong style="color:#475569;">Команда вашей компании</strong>
        </p>
        <p style="margin:16px 0 0;font-size:12px;color:#cbd5e1;">
          © 2025 Ваша компания. Все права защищены.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

        email_msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        logger.info(f"Password reset email sent successfully to {email}")
        return f"Password reset email sent to {email}"

    except Exception as exc:
        logger.error(f"Failed to send password reset email to {email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_email_change_verification_task(self, receiver_new_email, first_name, code):
    """
    Celery task to send email change verification
    """
    try:
        subject = "Подтверждение нового адреса электронной почты"
        from_email = FROM_EMAIL
        to = [receiver_new_email]

        text_content = f"""
        Здравствуйте, {first_name}!

        Вы запросили изменение адреса электронной почты, связанного с вашим аккаунтом.

        Чтобы подтвердить новый адрес электронной почты, введите следующий {OTP_LEN}-значный код верификации:

        {code}

        Если вы не запрашивали это изменение, просто проигнорируйте это письмо.

        С уважением,
        Команда вашей компании
        """

        html_content = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 20px;">
    <div style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.08);">

      <!-- Header -->
      <div style="background:linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);padding:50px 40px;text-align:center;">
        <div style="width:90px;height:90px;background:rgba(255,255,255,0.25);border-radius:50%;margin:0 auto 24px;display:inline-flex;align-items:center;justify-content:center;backdrop-filter:blur(10px);border:3px solid rgba(255,255,255,0.3);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style="display:block;">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10h5v-2h-5c-4.34 0-8-3.66-8-8s3.66-8 8-8 8 3.66 8 8v1.43c0 .79-.71 1.57-1.5 1.57s-1.5-.78-1.5-1.57V12c0-2.76-2.24-5-5-5s-5 2.24-5 5 2.24 5 5 5c1.38 0 2.64-.56 3.54-1.47.65.89 1.77 1.47 2.96 1.47 1.97 0 3.5-1.6 3.5-3.57V12c0-5.52-4.48-10-10-10zm0 13c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z" fill="#ffffff"/>
          </svg>
        </div>
        <h1 style="margin:0;font-size:32px;font-weight:700;color:#ffffff;letter-spacing:-0.8px;">Смена email</h1>
        <p style="margin:12px 0 0;font-size:16px;color:rgba(255,255,255,0.95);font-weight:400;">Подтвердите новый адрес</p>
      </div>

      <!-- Content -->
      <div style="padding:48px 40px;">
        <p style="margin:0 0 16px;font-size:18px;line-height:1.6;color:#0f172a;font-weight:600;">
          Привет, {first_name}! 👋
        </p>
        <p style="margin:0 0 32px;font-size:16px;line-height:1.7;color:#475569;">
          Вы запросили изменение email. Введите код ниже, чтобы подтвердить новый адрес и завершить процесс смены контактных данных.
        </p>

        <!-- Code Box -->
        <div style="background:linear-gradient(135deg, #cffafe 0%, #a5f3fc 100%);border:3px solid #06b6d4;border-radius:16px;padding:36px;text-align:center;margin:0 0 32px;position:relative;">
          <div style="font-size:13px;font-weight:700;color:#06b6d4;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">Код подтверждения</div>
          <div style="font-size:52px;font-weight:800;color:#06b6d4;letter-spacing:12px;font-family:'Courier New',monospace;">{code}</div>
          <div style="margin-top:16px;font-size:13px;color:#155e75;">Код действителен 5 минут</div>
        </div>

        <!-- Info Box -->
        <div style="background:#dbeafe;border-left:4px solid #3b82f6;border-radius:12px;padding:20px 24px;margin:0 0 32px;">
          <p style="margin:0;font-size:14px;line-height:1.7;color:#1e3a8a;">
            <strong style="color:#1e40af;display:block;margin-bottom:4px;">💡 Обратите внимание</strong>
            После подтверждения все уведомления будут отправляться на новый адрес электронной почты.
          </p>
        </div>

        <p style="margin:0;font-size:14px;line-height:1.6;color:#64748b;text-align:center;">
          Не запрашивали смену email? Проигнорируйте это письмо — изменения не вступят в силу.
        </p>
      </div>

      <!-- Footer -->
      <div style="background:#f8fafc;padding:32px 40px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="margin:0 0 12px;font-size:13px;color:#64748b;">
          Нужна помощь? <a href="mailto:support@yourcompany.com" style="color:#06b6d4;text-decoration:none;font-weight:600;">Свяжитесь с нами</a>
        </p>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          С уважением,<br><strong style="color:#475569;">Команда вашей компании</strong>
        </p>
        <p style="margin:16px 0 0;font-size:12px;color:#cbd5e1;">
          © 2025 Ваша компания. Все права защищены.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

        email = EmailMultiAlternatives(subject, text_content, from_email, to)
        email.attach_alternative(html_content, "text/html")
        email.send()

        logger.info(f"Email change verification sent successfully to {receiver_new_email}")
        return f"Email change verification sent to {receiver_new_email}"

    except Exception as exc:
        logger.error(
            f"Failed to send email change verification to {receiver_new_email}: {str(exc)}"
        )
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_activation_invite_task(self, email, first_name, uid, token):
    """
    Celery task to send activation invite using EmailMultiAlternatives
    """
    try:
        subject = "Приглашение присоединиться к платформе"
        from_email = FROM_EMAIL
        # frontend_url = config("FRONTEND_URL", default='127.0.0.1:5173')
        # activation_link = f"{frontend_url.rstrip('/')}/activate?uid={uid}&token={token}"
        domain_url = config("DOMAIN_URL", default="127.0.0.1:8000")
        activation_link = (
            f"{domain_url.rstrip('/')}/api/accounts/auth/activate?uid={uid}&token={token}"
        )
        to = [email]

        text_content = f"""Здравствуйте, {first_name}!

Вас пригласили присоединиться к нашей платформе.

Чтобы начать, активируйте свой аккаунт:
{activation_link}

Если вы не ожидали это приглашение, можете спокойно проигнорировать это письмо.

— Команда вашей компании
"""

        html_content = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 20px;">
    <div style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.08);">

      <!-- Header -->
      <div style="background:linear-gradient(135deg, #10b981 0%, #059669 100%);padding:50px 40px;text-align:center;">
        <div style="width:90px;height:90px;background:rgba(255,255,255,0.25);border-radius:50%;margin:0 auto 24px;display:inline-flex;align-items:center;justify-content:center;backdrop-filter:blur(10px);border:3px solid rgba(255,255,255,0.3);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style="display:block;">
            <path d="M9 11.75c-.69 0-1.25.56-1.25 1.25s.56 1.25 1.25 1.25 1.25-.56 1.25-1.25-.56-1.25-1.25-1.25zm6 0c-.69 0-1.25.56-1.25 1.25s.56 1.25 1.25 1.25 1.25-.56 1.25-1.25-.56-1.25-1.25-1.25zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8 0-.29.02-.58.05-.86 2.36-1.05 4.23-2.98 5.21-5.37C11.07 8.33 14.05 10 17.42 10c.78 0 1.53-.09 2.25-.26.21.71.33 1.47.33 2.26 0 4.41-3.59 8-8 8z" fill="#ffffff"/>
          </svg>
        </div>
        <h1 style="margin:0;font-size:32px;font-weight:700;color:#ffffff;letter-spacing:-0.8px;">Добро пожаловать!</h1>
        <p style="margin:12px 0 0;font-size:16px;color:rgba(255,255,255,0.95);font-weight:400;">Активируйте аккаунт</p>
      </div>

      <!-- Content -->
      <div style="padding:48px 40px;">
        <p style="margin:0 0 16px;font-size:18px;line-height:1.6;color:#0f172a;font-weight:600;">
          Привет, {first_name}! 👋
        </p>
        <p style="margin:0 0 32px;font-size:16px;line-height:1.7;color:#475569;">
          Вас пригласили присоединиться к нашей платформе! Нажмите на кнопку ниже, чтобы активировать аккаунт и начать использовать все возможности.
        </p>

        <!-- CTA Button -->
        <div style="text-align:center;margin:0 0 32px;">
          <a href="{activation_link}" style="display:inline-block;background:linear-gradient(135deg, #10b981 0%, #059669 100%);color:#ffffff;text-decoration:none;font-size:17px;font-weight:600;padding:18px 48px;border-radius:12px;box-shadow:0 4px 16px rgba(16,185,129,0.3);transition:all 0.3s;">
            Активировать аккаунт
          </a>
        </div>

        <!-- Link Box -->
        <div style="background:#f0fdf4;border:2px solid #86efac;border-radius:12px;padding:20px 24px;margin:0 0 32px;">
          <p style="margin:0 0 12px;font-size:13px;line-height:1.6;color:#166534;text-align:center;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;">
            Или скопируйте ссылку
          </p>
          <p style="margin:0;font-size:13px;line-height:1.6;color:#15803d;text-align:center;word-break:break-all;font-family:monospace;">
            {activation_link}
          </p>
        </div>

        <p style="margin:0;font-size:14px;line-height:1.6;color:#64748b;text-align:center;">
          Не ожидали приглашение? Проигнорируйте письмо — аккаунт не будет создан.
        </p>
      </div>

      <!-- Footer -->
      <div style="background:#f8fafc;padding:32px 40px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="margin:0 0 12px;font-size:13px;color:#64748b;">
          Нужна помощь? <a href="mailto:support@yourcompany.com" style="color:#10b981;text-decoration:none;font-weight:600;">Свяжитесь с нами</a>
        </p>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          С уважением,<br><strong style="color:#475569;">Команда вашей компании</strong>
        </p>
        <p style="margin:16px 0 0;font-size:12px;color:#cbd5e1;">
        © 2025 Ваша компания. Все права защищены.
                </p>
              </div>
            </div>
          </div>
        </body>
        </html>"""

        email_msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        logger.info(f"Activation invite sent successfully to {email}")
        return f"Activation invite sent to {email}"

    except Exception as exc:
        logger.error(f"Failed to send activation invite to {email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))


@shared_task(bind=True, max_retries=3)
def send_otp_verification_task(self, email, first_name, otp_code):
    """
    Celery task to send 2FA OTP verification code using EmailMultiAlternatives
    """
    try:
        subject = "Код подтверждения входа"
        from_email = FROM_EMAIL
        to = [email]

        text_content = f"""Здравствуйте, {first_name}!

Ваш код подтверждения: {otp_code}

Введите этот код, чтобы завершить вход в систему. Код действителен в течение 5 минут.

Если вы не запрашивали этот код, проигнорируйте это письмо и рассмотрите возможность смены пароля.

— Команда вашей компании
"""

        html_content = f"""<!doctype html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background:#f8fafc;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:40px 20px;">
    <div style="background:#ffffff;border-radius:20px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,0.08);">

      <!-- Header -->
      <div style="background:linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%);padding:50px 40px;text-align:center;">
        <div style="width:90px;height:90px;background:rgba(255,255,255,0.25);border-radius:50%;margin:0 auto 24px;display:inline-flex;align-items:center;justify-content:center;backdrop-filter:blur(10px);border:3px solid rgba(255,255,255,0.3);">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style="display:block;">
            <path d="M12 1L3 5v6c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V5l-9-4zm0 10.99h7c-.53 4.12-3.28 7.79-7 8.94V12H5V6.3l7-3.11v8.8z" fill="#ffffff"/>
          </svg>
        </div>
        <h1 style="margin:0;font-size:32px;font-weight:700;color:#ffffff;letter-spacing:-0.8px;">Вход в аккаунт</h1>
        <p style="margin:12px 0 0;font-size:16px;color:rgba(255,255,255,0.95);font-weight:400;">Код двухфакторной аутентификации</p>
      </div>

      <!-- Content -->
      <div style="padding:48px 40px;">
        <p style="margin:0 0 16px;font-size:18px;line-height:1.6;color:#0f172a;font-weight:600;">
          Привет, {first_name}! 👋
        </p>
        <p style="margin:0 0 32px;font-size:16px;line-height:1.7;color:#475569;">
          Для завершения входа в систему введите код подтверждения ниже. Это дополнительная мера безопасности для защиты вашего аккаунта.
        </p>

        <!-- Code Box -->
        <div style="background:linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%);border:3px solid #8b5cf6;border-radius:16px;padding:36px;text-align:center;margin:0 0 32px;position:relative;">
          <div style="font-size:13px;font-weight:700;color:#8b5cf6;letter-spacing:2px;text-transform:uppercase;margin-bottom:16px;">Код входа</div>
          <div style="font-size:52px;font-weight:800;color:#8b5cf6;letter-spacing:12px;font-family:'Courier New',monospace;">{otp_code}</div>
          <div style="margin-top:16px;font-size:13px;color:#6b21a8;">Код действителен 5 минут</div>
        </div>

        <!-- Security Warning -->
        <div style="background:#fef2f2;border-left:4px solid #ef4444;border-radius:12px;padding:20px 24px;margin:0 0 32px;">
          <p style="margin:0;font-size:14px;line-height:1.7;color:#7f1d1d;">
            <strong style="color:#991b1b;display:block;margin-bottom:4px;">🛡️ Безопасность</strong>
            Если вы не пытались войти в систему, немедленно смените пароль и свяжитесь с нашей службой поддержки.
          </p>
        </div>

        <p style="margin:0;font-size:14px;line-height:1.6;color:#64748b;text-align:center;">
          Не запрашивали код? Проигнорируйте письмо и убедитесь, что ваш аккаунт защищен.
        </p>
      </div>

      <!-- Footer -->
      <div style="background:#f8fafc;padding:32px 40px;text-align:center;border-top:1px solid #e2e8f0;">
        <p style="margin:0 0 12px;font-size:13px;color:#64748b;">
          Нужна помощь? <a href="mailto:support@yourcompany.com" style="color:#8b5cf6;text-decoration:none;font-weight:600;">Свяжитесь с нами</a>
        </p>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          С уважением,<br><strong style="color:#475569;">Команда вашей компании</strong>
        </p>
        <p style="margin:16px 0 0;font-size:12px;color:#cbd5e1;">
          © 2025 Ваша компания. Все права защищены.
        </p>
      </div>
    </div>
  </div>
</body>
</html>"""

        email_msg = EmailMultiAlternatives(subject, text_content, from_email, to)
        email_msg.attach_alternative(html_content, "text/html")
        email_msg.send()

        logger.info(f"OTP verification sent successfully to {email}")
        return f"OTP verification sent to {email}"

    except Exception as exc:
        logger.error(f"Failed to send OTP verification to {email}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (2**self.request.retries))
