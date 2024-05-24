from fpdf import FPDF
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email import encoders
import json
from fpdf import FPDF
from io import BytesIO

def generate_pdf_from_data(data):
    # Create instance of FPDF class
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Add a title
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="Health Data Report", ln=True, align="C")

    # Add content from data
    for category, values in data.items():
        pdf.set_font("Arial", size=12, style='B')
        pdf.cell(200, 10, txt=category.capitalize(), ln=True, align="L")
        pdf.set_font("Arial", size=10)
        if values:
            # Get column names
            column_names = list(values[0].keys())
            # Add column names to table
            pdf.set_font("Arial", size=10, style='B')
            col_width = 200 / len(column_names)
            for col_name in column_names:
                pdf.cell(col_width, 10, col_name, border=1, ln=False, align="C")
            pdf.ln()
            # Add rows to table
            pdf.set_font("Arial", size=10)
            for row in values:
                for col_name in column_names:
                    pdf.cell(col_width, 10, str(row[col_name]), border=1, ln=False, align="C")
                pdf.ln()

    # Output PDF content as byte string
    pdf_bytes = pdf.output(dest='S')

    return pdf_bytes



  

def send_email_with_attachment(sender_email, recipient_email, subject, body_text, attachment_file_name, attachment_data):
    # Create a new SES client
    ses_client = boto3.client('ses')

    # Create a multipart/mixed parent container
    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Create a multipart/alternative child container
    msg_body = MIMEMultipart('alternative')

    # Add the body text
    text_part = MIMEText(body_text, 'plain')
    msg_body.attach(text_part)
    
    attachment_part = MIMEApplication(attachment_data, _subtype='pdf')
    attachment_part.add_header('Content-Disposition', 'attachment', filename=attachment_file_name)
    msg.attach(attachment_part)

    # Attach the multipart/alternative child container to the multipart/mixed
    # parent container
    msg.attach(msg_body)

    # Send the email
    try:
        response = ses_client.send_raw_email(
            Source=sender_email,
            Destinations=[recipient_email],
            RawMessage={'Data': msg.as_string()}
        )
        print("Email sent! Message ID:", response['MessageId'])
    except ClientError as e:
        print("Email sending failed:", e)



def lambda_handler(event, context):
    print("even : ")
    print(event)
    print("context")
    print(context)
    
    body = json.loads(event['Records'][0]['body'].replace("'", "\""))
    print("body")
    print(body)    
    # Example usage
    sender_email = 'pp2959@nyu.edu'
    recipient_email = body.pop('email')
    subject = "Your weekly Health report is ready !"
    body_text = "Please find your weekly health report attached with this mail."
    attachment_file_name = 'health_report.pdf'
    attachment_data = generate_pdf_from_data(body)
    
    send_email_with_attachment(sender_email, recipient_email, subject, body_text, attachment_file_name, attachment_data)

    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }



