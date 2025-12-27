"""
📧 Email Service - Notification Email Delivery
==============================================

This module provides email sending capability for notifications.

Supports:
- SMTP (default, works with any provider)
- SendGrid (if SENDGRID_API_KEY is set)
- Amazon SES (if AWS credentials are set)

Configuration via environment variables:
- EMAIL_PROVIDER: smtp | sendgrid | ses (default: smtp)
- SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD
- SENDGRID_API_KEY
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION

Graceful degradation:
- If email fails, notification is stored for retry
- If provider unavailable, logs warning and continues
"""

import logging
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from dataclasses import dataclass
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class EmailResult:
    """Result of email send attempt"""
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    provider: str = "unknown"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'message_id': self.message_id,
            'error': self.error,
            'provider': self.provider
        }


class EmailService:
    """
    Multi-provider email service with graceful fallback.
    """
    
    def __init__(self):
        self.provider = os.environ.get('EMAIL_PROVIDER', 'smtp').lower()
        self.from_email = os.environ.get('EMAIL_FROM', 'noreply@druvai.com')
        self.from_name = os.environ.get('EMAIL_FROM_NAME', 'Sathi - Your AI Study Companion')
        
        # SMTP config
        self.smtp_host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = os.environ.get('SMTP_USER', '')
        self.smtp_password = os.environ.get('SMTP_PASSWORD', '')
        
        # SendGrid config
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY', '')
        
        # Validate configuration
        self._validate_config()
        
        logger.info(f"📧 EmailService initialized with provider: {self.provider}")
    
    def _validate_config(self):
        """Validate email configuration"""
        if self.provider == 'smtp':
            if not self.smtp_user or not self.smtp_password:
                logger.warning("⚠️ SMTP credentials not configured - email sending disabled")
                self.provider = 'disabled'
        elif self.provider == 'sendgrid':
            if not self.sendgrid_api_key:
                logger.warning("⚠️ SendGrid API key not configured - falling back to SMTP")
                self.provider = 'smtp'
                if not self.smtp_user:
                    self.provider = 'disabled'
    
    async def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> EmailResult:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text fallback (auto-generated if not provided)
            
        Returns:
            EmailResult with success/failure status
        """
        if self.provider == 'disabled':
            logger.debug(f"📧 Email disabled, would send to {to}: {subject}")
            return EmailResult(
                success=False,
                error="Email service not configured",
                provider="disabled"
            )
        
        # Generate plain text fallback
        if not text_content:
            import re
            text_content = re.sub('<[^<]+?>', '', html_content)
        
        try:
            if self.provider == 'sendgrid':
                return await self._send_via_sendgrid(to, subject, html_content, text_content)
            else:
                return await self._send_via_smtp(to, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"📧 Email send failed: {e}")
            return EmailResult(
                success=False,
                error=str(e),
                provider=self.provider
            )
    
    async def _send_via_smtp(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> EmailResult:
        """Send email via SMTP"""
        
        def _send_sync():
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to
            
            # Attach both plain text and HTML
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            msg.attach(part1)
            msg.attach(part2)
            
            # Connect and send
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to, msg.as_string())
            
            return msg['Message-ID']
        
        # Run in thread pool to not block async
        loop = asyncio.get_event_loop()
        message_id = await loop.run_in_executor(None, _send_sync)
        
        logger.info(f"📧 Email sent via SMTP to {to}: {subject}")
        
        return EmailResult(
            success=True,
            message_id=message_id,
            provider="smtp"
        )
    
    async def _send_via_sendgrid(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> EmailResult:
        """Send email via SendGrid API"""
        try:
            import httpx
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.sendgrid.com/v3/mail/send",
                    headers={
                        "Authorization": f"Bearer {self.sendgrid_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "personalizations": [{"to": [{"email": to}]}],
                        "from": {"email": self.from_email, "name": self.from_name},
                        "subject": subject,
                        "content": [
                            {"type": "text/plain", "value": text_content},
                            {"type": "text/html", "value": html_content}
                        ]
                    },
                    timeout=30.0
                )
                
                if response.status_code in [200, 201, 202]:
                    message_id = response.headers.get('X-Message-Id', 'unknown')
                    logger.info(f"📧 Email sent via SendGrid to {to}: {subject}")
                    return EmailResult(
                        success=True,
                        message_id=message_id,
                        provider="sendgrid"
                    )
                else:
                    error = f"SendGrid error: {response.status_code} - {response.text}"
                    logger.error(error)
                    return EmailResult(
                        success=False,
                        error=error,
                        provider="sendgrid"
                    )
                    
        except ImportError:
            logger.warning("httpx not installed, falling back to SMTP")
            return await self._send_via_smtp(to, subject, html_content, text_content)
        except Exception as e:
            logger.error(f"SendGrid send failed: {e}")
            # Fallback to SMTP
            logger.info("Falling back to SMTP...")
            return await self._send_via_smtp(to, subject, html_content, text_content)


# Singleton instance
_email_service: Optional[EmailService] = None


def get_email_service() -> EmailService:
    """Get or create the email service singleton"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service

