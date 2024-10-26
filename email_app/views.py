from django.shortcuts import redirect
from allauth.socialaccount.models import SocialToken, SocialAccount
from django.contrib.auth.decorators import login_required
from .models import EmailAccount, EmailMessage
from django.http import JsonResponse
from .sync import sync_emails
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from elasticsearch_dsl import Search
import requests

@login_required
def connect_outlook(request):
    try:
        # Get the user’s social token from Microsoft (OAuth)
        social_account = SocialAccount.objects.get(user=request.user)
        token = SocialToken.objects.get(account=social_account)

        email_account, created = EmailAccount.objects.get_or_create(
            user = request.user,
            defaults={
                'email': social_account.extra_data.get('mail'),
                'token': token.token
            }
        )
        if not created:
            print('Email account is already linked. Synchronizing emails...')
        else:
            print('Email account is linked successfully. Synchronizing emails...')

        return redirect('sync_user_emails')

    except SocialAccount.DoesNotExist:
        # Redirect to OAuth login if no social account is found
        return redirect('/accounts/microsoft/login/')
    except SocialToken.DoesNotExist:
        # Redirect to OAuth login iemailf no token is found
        return redirect('/accounts/microsoft/login/')
    except Exception as e:
        return JsonResponse({'error':str(e)}, status=500)



def sync_outlook_emails(user):
    # Get the OAuth token for the user
    email_account = EmailAccount.objects.get(user=user)
    access_token = email_account.token

    url = 'https://graph.microsoft.com/v1.0/me/messages'
    headers = {'Authorization': f'Bearer {access_token}'}
    
    response = requests.get(url, headers=headers)
    messages = response.json()['value']
    print(messages)
    for message in messages:
        email = EmailMessage(
            subject=message['subject'],
            sender=message['from']['emailAddress']['address'],
            recipient=message['toRecipients'][0]['emailAddress']['address'],
            message_body=message['body']['content'],
            timestamp=message['receivedDateTime']
        )
        email.save()

@api_view(['POST'])
def create_account(request):
    """
    API endpoint to create a local account and link with Outlook.
    """
    # Extract the required information from the request
    username = request.data.get('username')
    password = request.data.get('password')
    email = request.data.get('email')

    # Create a new user (local account)
    user, created = User.objects.geemailt_or_create(username=username, email=email)
    if created:
        user.set_password(password)
        user.save()

    # Get the OAuth token from django-allauth (assumes Outlook OAuth flow was already completed)
    social_account = SocialAccount.objects.get(user=user)
    token = SocialToken.objects.get(account=social_account)

    # Save the OAuth token and email in the EmailAccount model
    EmailAccount.objects.create(
        user=user,
        email=email,
        token=token.token
    )

    return Response({"message": "Account created and linked with Outlook successfully!"})


@api_view(['GET'])
def get_user_emails(request):
    """
    API endpoint to retrieve synchronized emails from Elasticsearch for the current user.
    """
    user = request.user

    # Search for the user's emails in the Elasticsearch index
    search = Search(index="emails").query("match", recipient=user.email)
    response = search.execute()

    # Format the response with the required fields
    emails = []
    for hit in response:
        emails.append({
            "subject": hit.subject,
            "sender": hit.sender,
            "recipient": hit.recipient,
            "message_body": hit.message_body,
            "timestamp": hit.timestamp
        })

    return Response({"emails": emails})


@api_view(['GET', 'POST'])
def sync_user_emails(request):
    """
    API endpoint to trigger email synchronization for the current user.
    """
    user = request.user
    success = sync_emails(user)
    
    if success:
        return JsonResponse({'message': 'Emails synchronized successfully'})
    else:
        return JsonResponse({'error': 'Failed to sync emails'}, status=400)


