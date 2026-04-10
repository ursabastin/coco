from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os.path
import pickle
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailIntegration:
    def __init__(self, credentials_path='credentials.json', token_path='token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self.authenticated = False
    
    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None
        
        # Load saved credentials
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    return "Error: credentials.json not found. Download from Google Cloud Console."
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save credentials
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.service = build('gmail', 'v1', credentials=creds)
        self.authenticated = True
        return "Gmail authenticated successfully"
    
    def check_unread_count(self):
        """Get count of unread emails"""
        if not self.authenticated:
            return "Not authenticated"
        
        try:
            results = self.service.users().messages().list(
                userId='me', q='is:unread').execute()
            messages = results.get('messages', [])
            return f"You have {len(messages)} unread emails"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def get_latest_emails(self, count=5):
        """Get latest emails"""
        if not self.authenticated:
            return "Not authenticated"
        
        try:
            results = self.service.users().messages().list(
                userId='me', maxResults=count).execute()
            messages = results.get('messages', [])
            
            email_summaries = []
            for msg in messages:
                msg_data = self.service.users().messages().get(
                    userId='me', id=msg['id']).execute()
                
                # Extract subject and sender
                headers = msg_data['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                
                email_summaries.append(f"From {sender}: {subject}")
            
            return email_summaries
        except Exception as e:
            return f"Error: {str(e)}"
