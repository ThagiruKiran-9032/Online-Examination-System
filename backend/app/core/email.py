import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.core.config import settings

def send_email(to_email: str, subject: str, html_content: str, text_content: Optional[str] = None):
    """
    Sends an email using configured SMTP settings.
    If SMTP credentials are not set or SMTP_ENABLED is False, logs the email dispatch gracefully.
    """
    if not settings.SMTP_ENABLED or not settings.SMTP_USER or not settings.SMTP_PASSWORD or settings.SMTP_PASSWORD == "your_app_password":
        print(f"[SMTP Mock Log] Email to: {to_email} | Subject: '{subject}' (SMTP_PASSWORD not set or is placeholder)")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
        msg["To"] = to_email

        if text_content:
            msg.attach(MIMEText(text_content, "plain"))
        msg.attach(MIMEText(html_content, "html"))

        if settings.SMTP_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
        else:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)

        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.EMAILS_FROM_EMAIL, [to_email], msg.as_string())
        server.quit()
        print(f"[SMTP Success] Email successfully sent to {to_email}")
        return True
    except Exception as e:
        print(f"[SMTP Error] Failed to send email to {to_email}: {e}")
        return False


def send_welcome_email(to_email: str, full_name: str):
    subject = "Welcome to Online Examination System!"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h2 style="color: #2563eb; margin-top: 0;">Welcome to Online Examination System!</h2>
        <p>Hello <strong>{full_name}</strong>,</p>
        <p>Your student account has been successfully created. You can now log in, view available examinations, register for tests, and check your performance results.</p>
        <div style="margin: 25px 0;">
          <a href="#" style="background: #2563eb; color: #ffffff; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">Access Exam Portal</a>
        </div>
        <p style="color: #64748b; font-size: 13px;">If you did not request this account, please ignore this email.</p>
      </div>
    </body>
    </html>
    """
    send_email(to_email, subject, html_content)


def send_exam_registration_email(to_email: str, full_name: str, exam_title: str, category: str):
    subject = f"Exam Registration Confirmed: {exam_title}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h2 style="color: #16a34a; margin-top: 0;">Registration Confirmed!</h2>
        <p>Hello <strong>{full_name}</strong>,</p>
        <p>You have successfully registered for the following examination:</p>
        <div style="background: #f1f5f9; padding: 16px; border-radius: 8px; margin: 20px 0;">
          <h4 style="margin: 0 0 8px 0; color: #0f172a;">{exam_title}</h4>
          <p style="margin: 0; color: #475569; font-size: 14px;"><strong>Category:</strong> {category}</p>
        </div>
        <p>Please ensure you are prepared before initiating your attempt on your dashboard.</p>
        <p style="color: #64748b; font-size: 13px;">Good luck with your examination!</p>
      </div>
    </body>
    </html>
    """
    send_email(to_email, subject, html_content)


def send_exam_result_email(
    to_email: str,
    full_name: str,
    exam_title: str,
    score: float,
    total_possible: float,
    passing_marks: float,
    passed: bool
):
    status_text = "PASSED" if passed else "FAILED"
    status_color = "#16a34a" if passed else "#dc2626"
    percentage = (score / total_possible * 100) if total_possible > 0 else 0

    subject = f"Exam Scorecard: {exam_title} [{status_text}]"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h2 style="color: #2563eb; margin-top: 0;">Examination Scorecard</h2>
        <p>Hello <strong>{full_name}</strong>,</p>
        <p>Your attempt for <strong>{exam_title}</strong> has been evaluated. Below is your official scorecard:</p>
        
        <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center;">
          <div style="font-size: 14px; color: #64748b; text-transform: uppercase; font-weight: bold;">Result Status</div>
          <div style="font-size: 28px; font-weight: bold; color: {status_color}; margin: 8px 0;">{status_text}</div>
          <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 15px 0;">
          <div style="display: flex; justify-content: space-around; text-align: center;">
            <div>
              <div style="font-size: 12px; color: #64748b;">Your Score</div>
              <div style="font-size: 20px; font-weight: bold; color: #0f172a;">{score} / {total_possible}</div>
            </div>
            <div>
              <div style="font-size: 12px; color: #64748b;">Percentage</div>
              <div style="font-size: 20px; font-weight: bold; color: #0f172a;">{percentage:.1f}%</div>
            </div>
            <div>
              <div style="font-size: 12px; color: #64748b;">Passing Score</div>
              <div style="font-size: 20px; font-weight: bold; color: #0f172a;">{passing_marks}</div>
            </div>
          </div>
        </div>

        <p>Log in to your portal to review question breakdown and performance leaderboards.</p>
      </div>
    </body>
    </html>
    """
    send_email(to_email, subject, html_content)


def send_password_reset_email(to_email: str, reset_token: str):
    subject = "Password Reset Request - Online Examination System"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h2 style="color: #dc2626; margin-top: 0;">Password Reset Request</h2>
        <p>We received a request to reset your password. Use the verification token code below to reset your account password:</p>
        <div style="background: #f1f5f9; padding: 16px; border-radius: 8px; margin: 20px 0; text-align: center;">
          <span style="font-size: 24px; font-weight: bold; letter-spacing: 4px; color: #2563eb;">{reset_token}</span>
        </div>
        <p style="font-size: 13px; color: #64748b;">This verification code is valid for 15 minutes. If you did not request a password reset, please ignore this email.</p>
      </div>
    </body>
    </html>
    """
    send_email(to_email, subject, html_content)


def send_registration_otp_email(to_email: str, otp: str):
    subject = "Verify Your Email Address - Online Examination System"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #f8fafc; padding: 20px; color: #1e293b;">
      <div style="max-width: 600px; margin: 0 auto; background: #ffffff; padding: 30px; border-radius: 12px; border: 1px solid #e2e8f0;">
        <h2 style="color: #2563eb; margin-top: 0;">Verify Your Email Address</h2>
        <p>Thank you for signing up! Enter the 6-digit verification code below in your registration window to complete your account setup:</p>
        <div style="background: #f1f5f9; padding: 20px; border-radius: 10px; margin: 25px 0; text-align: center;">
          <span style="font-size: 32px; font-weight: bold; letter-spacing: 8px; color: #2563eb;">{otp}</span>
        </div>
        <p style="font-size: 13px; color: #64748b;">This verification code is valid for 10 minutes. If you did not initiate this request, please disregard this email.</p>
      </div>
    </body>
    </html>
    """
    send_email(to_email, subject, html_content)
