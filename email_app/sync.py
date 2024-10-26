import requests
from .models import EmailAccount, EmailMessage

GRAPH_API_URL = 'https://graph.microsoft.com/v1.0/me/messages'

def fetch_outlook_emails(user):
    """
    Fetch emails from the Outlook account linked to the given user.
    """
    try:
        email_account = EmailAccount.objects.get(user=user)
        access_token = email_account.token
        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        # Fetch emails from the Microsoft Graph API
        response = requests.get(GRAPH_API_URL, headers=headers)
        emails = []

        # Check for a successful response
        if response.status_code == 200:
            while True:
                data = response.json()
                emails.extend(data.get('value', []))
                next_link = data.get('@odata.nextLink')
                if next_link:
                    response = requests.get(next_link, headers=headers)
                else:
                    break
            return emails
        else:
            print(f"Failed to fetch emails: {response.status_code} - {response.text}")
            return None

    except EmailAccount.DoesNotExist:
        print(f"No EmailAccount found for user: {user}")
        return None
    except Exception as e:
        print("An error occurred while fetching emails")
        return None


def sync_emails(user):
    """
    Fetch emails from Outlook and index them in Elasticsearch.
    """
    # Fetch the list of emails using the Microsoft Graph API
    emails = fetch_outlook_emails(user)

    if emails is None:
        print("Email sync failed: fetch_outlook_emails returned None")
        return False

    if emails:
        for message in emails:
            # Index each email in Elasticsearch
            try:
                email = EmailMessage(
                    subject=message.get('subject', ''),
                    sender=message.get('from', {}).get('emailAddress', {}).get('address', ''),
                    recipient=message.get('toRecipients', [])[0].get('emailAddress', {}).get('address', '') if message.get('toRecipients') else '',
                    message_body=message.get('body', {}).get('content', ''),
                    timestamp=message.get('receivedDateTime')
                )
                email.save()
            except Exception as e:
                print("An error occurred while saving an email",e)
                continue  # Skip the current email if there's an error

        return True
    else:
        return False