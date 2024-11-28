

from flask import Flask, request, jsonify
from flask_cors import CORS
import dns.resolver
import smtplib
import socket

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def generate_email_variants(first_name, last_name, domain):
    # Generate common email patterns
    email_patterns = [
        f"{first_name}{last_name[0]}@{domain}",
        f"{first_name}@{domain}",
        f"{first_name}{last_name}@{domain}",
        f"{first_name}.{last_name}@{domain}",
        f"{first_name}_{last_name}@{domain}",
        f"{first_name[0]}.{last_name}@{domain}",
        f"{first_name}.{last_name[0]}@{domain}",
        f"{last_name}{first_name}@{domain}",
    ]
    return email_patterns

def validate_email(email):
    try:
        domain = email.split('@')[1]
        records = dns.resolver.resolve(domain, 'MX')
        mx_record = str(records[0].exchange)

        # Establish SMTP connection
        server = smtplib.SMTP(mx_record, timeout=10)  # Set a timeout for the connection
        server.set_debuglevel(0)  # Disable debug output
        server.helo()
        server.mail('madsan123456@gmail.com')
        code, message = server.rcpt(email)
        server.quit()

        return code == 250
    except (smtplib.SMTPConnectError, socket.timeout) as e:
        print(f"Failed to connect to SMTP server for {email}: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error while validating {email}: {e}")
        return False


@app.route('/find-email', methods=['POST'])
def find_email():
    print("getting into python!")
    data = request.json

    # Extract input fields
    first_name = data.get('first_name', '').strip().lower()
    last_name = data.get('last_name', '').strip().lower()
    domain = data.get('domain', '').strip().lower()

    if not first_name or not last_name or not domain:
        return jsonify({"error": "Please provide first_name, last_name, and domain"}), 400

    # Generate email variants
    email_variants = generate_email_variants(first_name, last_name, domain)

    # Validate emails
    for email in email_variants:
        if validate_email(email):
            return jsonify({"valid_email": email}), 200

    # If no valid email is found
    return jsonify({"message": "Sorry, not able to find a valid email ID."}), 404

if __name__ == '__main__':
    app.run(debug=True)
