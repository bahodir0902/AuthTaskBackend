from .send_mail_tasks import (
    send_activation_invite_task,
    send_email_change_verification_task,
    send_email_verification_task,
    send_otp_verification_task,
    send_password_verification_task,
)


def send_email_verification(receiver_email, first_name, code):
    return send_email_verification_task.delay(receiver_email, first_name, code)


def send_password_verification(email, first_name, code):
    return send_password_verification_task.delay(email, first_name, code)


def send_email_to_verify_email(receiver_new_email, first_name, code):
    return send_email_change_verification_task.delay(receiver_new_email, first_name, code)


def send_activation_invite(email, first_name, uid, token):
    return send_activation_invite_task.delay(email, first_name, uid, token)


def send_otp_verification(email, first_name, otp_code):
    return send_otp_verification_task.delay(email, first_name, otp_code)
