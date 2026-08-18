import smtplib
from email.message import EmailMessage
import mrml
from app.config import settings
from app.services.security import generate_unsubscribe_token
from bs4 import BeautifulSoup

def compile_mjml_to_html(mjml_content: str) -> str:
    """Compiles MJML string to HTML using mrml."""
    if not mjml_content:
        return ""
    try:
        return mrml.to_html(mjml_content)
    except Exception as e:
        print(f"Error compiling MJML: {e}")
        return f"<p>Error compiling email template: {e}</p><br/><div>{mjml_content}</div>"

def extract_plain_text(html_content: str) -> str:
    """Extracts plain text from HTML content for multipart/alternative fallback."""
    if not html_content:
        return ""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator='\n').strip()

def send_campaign_email(
    to_email: str, 
    subject: str, 
    mjml_content: str, 
    subscriber_id: str,
    campaign_id: str,
    first_name: str = None
):
    """
    Constructs a raw MIME email (multipart/alternative) with List-Unsubscribe headers
    and dynamic unsubscribe link. Sends directly via authenticated SMTP.
    """
    # Simple template variable replacement
    if first_name:
        mjml_content = mjml_content.replace('{{first_name}}', first_name)
    else:
        mjml_content = mjml_content.replace('{{first_name}}', 'Subscriber')

    html_body = compile_mjml_to_html(mjml_content)
    plain_text_body = extract_plain_text(html_body)
    
    # Generate one-click unsubscribe links
    token = generate_unsubscribe_token(subscriber_id, campaign_id)
    base_url = settings.APP_DOMAIN.rstrip('/')
    unsubscribe_url = f"{base_url}/api/unsubscribe?sub_id={subscriber_id}&camp_id={campaign_id}&token={token}"
    
    # Extract domain from FROM_EMAIL
    from_domain = settings.FROM_EMAIL.split('@')[-1]
    mailto_url = f"mailto:unsubscribe@{from_domain}?subject=unsubscribe"
    
    # Append a standard unsubscribe footer to the HTML body
    footer = f"""
    <div style="text-align: center; font-size: 12px; color: #666; margin-top: 20px;">
        <p>You are receiving this email because you subscribed to our updates.</p>
        <p><a href="{unsubscribe_url}">Unsubscribe here</a></p>
    </div>
    """
    if "</body>" in html_body:
        html_body = html_body.replace("</body>", f"{footer}</body>")
    else:
        html_body += footer

    # Also append to plain text
    plain_text_body += f"\n\nTo unsubscribe, click here: {unsubscribe_url}"

    # Construct the EmailMessage (multipart/alternative)
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = settings.FROM_EMAIL
    msg['To'] = to_email
    msg['Message-ID'] = f"<{subscriber_id}.{campaign_id}@{from_domain}>"
    
    # RFC 8058 Headers
    msg['List-Unsubscribe'] = f"<{unsubscribe_url}>, <{mailto_url}>"
    msg['List-Unsubscribe-Post'] = "List-Unsubscribe=One-Click"
    
    msg.set_content(plain_text_body)
    msg.add_alternative(html_body, subtype='html')
    
    # Send via SMTP
    try:
        if settings.SMTP_PORT == 465:
            # Implicit SSL/TLS
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # Explicit TLS (STARTTLS)
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        return {"status": "sent", "message_id": msg['Message-ID']}
    except Exception as e:
        raise e
