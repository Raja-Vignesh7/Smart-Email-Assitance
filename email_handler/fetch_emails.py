import imaplib
import email
from email.header import decode_header
import json
from datetime import datetime, timedelta, date
import os
from dotenv import load_dotenv

def load_email_accounts(json_path="email_handler\\accounts.json"):
    try:
        with open(json_path, "r") as file:
            data = json.load(file)
            accounts = data.get("accounts", [])
            if not accounts:
                print("No accounts found in JSON.")
            return accounts
    except Exception as e:
        print(f"Error loading email accounts: {e}")
        return []


class fetcher:
    
    emails = None
    
    def get_emails(acc_id, email_user, email_pass, max_emails=10, end_date=None, fetch_all=False):
        # Initialize details as empty list to store all emails
        all_emails = []
        
        # Connect to Gmail server
        try:
            if email_pass != "None" and email_pass is not None and email_pass.strip():
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(email_user, email_pass)
                mail.select("inbox")
                
                # Build search criteria based on fetch_all
                if fetch_all:
                    search_criteria = "ALL"
                else:
                    search_criteria = "UNSEEN"

                # Add date filter if end_date is provided
                if end_date:
                    try:
                        if isinstance(end_date, str):
                            formatted_date = datetime.strptime(end_date, "%d-%b-%Y")
                        else:
                            formatted_date = end_date

                        next_day = date.today()
                        since_date = formatted_date.strftime('%d-%b-%Y')
                        before_date = (next_day + timedelta(days=1)).strftime('%d-%b-%Y')


                        status_flag = "ALL" if fetch_all else "UNSEEN"
                        search_criteria = f'({status_flag} SINCE "{since_date}" BEFORE "{before_date}")'

                    except Exception as date_error:
                        print(f"Error parsing end_date: {date_error}. Using default search.")
                        search_criteria = "ALL" if fetch_all else "UNSEEN"


                status, messages = mail.search(None, search_criteria)
                email_ids = messages[0].split()

                # Check if there are any emails
                if not email_ids or email_ids == [b'']:
                    mail.logout()
                    return {
                        "id": acc_id,
                        "status": "no_emails",
                        "message": f"No unread emails found{' before ' + str(end_date) if end_date else ''}"
                    }

                # Reverse email_ids to fetch latest emails first
                email_ids = email_ids[::-1]

                # Determine how many emails to fetch
                total_emails = len(email_ids)
                fetch_count = min(total_emails,max_emails)
                emails_to_fetch = email_ids[:fetch_count]
                
                print(f"Account {acc_id}: Found {total_emails} unseen emails, fetching {fetch_count}")
                
                # Fetch emails
                for i, num in enumerate(emails_to_fetch, 1):
                    try:
                        # Show progress for large batches
                        if fetch_count > 20 and i % 10 == 0:
                            print(f"Account {acc_id}: Processing email {i}/{fetch_count}")
                            
                        status, data = mail.fetch(num, "(RFC822)")
                        msg = email.message_from_bytes(data[0][1])

                        # Decode subject
                        subject = "No Subject"
                        if msg["Subject"]:
                            subject_parts = decode_header(msg["Subject"])
                            subject = ""
                            for part, encoding in subject_parts:
                                if isinstance(part, bytes):
                                    subject += part.decode(encoding or "utf-8")
                                else:
                                    subject += part

                        from_ = msg.get("From", "Unknown")
                        to_ = msg.get("To", "Unknown")
                        date_ = msg.get("Date", "Unknown")

                        # Extract email body
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))

                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    try:
                                        body = part.get_payload(decode=True).decode()
                                        break  # Only get the first plain text part
                                    except Exception as decode_error:
                                        body = f"[Error decoding body: {decode_error}]"
                                        break
                        else:
                            # Not multipart - i.e., plain text or HTML only
                            content_type = msg.get_content_type()
                            if content_type == "text/plain":
                                try:
                                    body = msg.get_payload(decode=True).decode()
                                except Exception as decode_error:
                                    body = f"[Error decoding body: {decode_error}]"

                        # Create email details dictionary
                        email_details = {
                            "id": acc_id,
                            "Subject": subject,
                            "From": from_,
                            "To": to_,
                            "Date": date_,
                            "Body": body.strip() if body else "No body content"
                        }
                        
                        all_emails.append(email_details)
                        
                    except Exception as email_error:
                        print(f"Error processing email {num}: {email_error}")
                        continue

                mail.logout()
                
                # Return all emails or a status message if no emails were processed
                if all_emails:
                    return all_emails , total_emails , fetch_count
                else:
                    return {
                        "id": acc_id,
                        "status": "processing_error",
                        "message": "No emails could be processed successfully"
                    }, 0 , 0
                    
            else:
                return {
                    "id": acc_id,
                    "status": "error",
                    "message": "Invalid or missing password key"
                } , 0 , 0 
                
        except imaplib.IMAP4.error as imap_error:
            return {
                "id": acc_id,
                "status": "error",
                "message": f"IMAP error: {imap_error}"
            } , 0,0
        except Exception as e:
            return {
                "id": acc_id,
                "status": "error", 
                "message": f"Connection error: {e}"
            } ,0,0
    
    def fetch(id=-1, max_emails=10, end_date=None, fetch_all=False):
        """
        Fetch emails from accounts
        
        Args:
            id: Account ID (-1 for all accounts, specific ID for single account)
            max_emails: Maximum number of emails to fetch per account (default: 10, ignored if fetch_all=True)
            end_date: Fetch emails until this date (format: 'DD-MMM-YYYY' e.g., '01-Jan-2024')
                     If None, fetches latest emails
            fetch_all: If True, fetches ALL unseen emails regardless of max_emails limit
        
        Returns:
            List of email dictionaries or error messages
        """
        fetcher.emails = load_email_accounts()
        results = []
        
        try:
            if not fetcher.emails:
                return [{
                    "status": "error",
                    "message": "No email accounts found in configuration"
                }]
            
            if id == -1:
                # Fetch from all accounts
                for acc_id, account in fetcher.emails.items():
                    load_dotenv()
                    email_user = account.get('email', '')
                    email_pass = account.get('pass_key', '')
                    email_pass = os.getenv(email_pass, '')
                    
                    if not email_user:
                        email_pass = os.getenv(email_pass, '')
                        results.append({
                            "id": acc_id,
                            "status": "error",
                            "message": "Email address not found in account configuration"
                        })
                        continue
                    
                    details = fetcher.get_emails(acc_id, email_user=email_user, 
                                               email_pass=email_pass, 
                                               max_emails=max_emails, 
                                               end_date=end_date,
                                               fetch_all=fetch_all)
                    
                    # If details is a list (multiple emails), extend results
                    if isinstance(details, list):
                        results.extend(details)
                    else:
                        # If details is a single dict (error or single email), append it
                        results.append(details)
                        
            else:
                # Fetch from specific account
                account = fetcher.emails.get(str(id))
                if account:
                    load_dotenv()
                    email_user = account.get('email', '')
                    email_pass = account.get('pass_key', '')
                    print(email_pass)
                    email_pass = os.getenv(email_pass, '')
                    print(email_pass)
                    if not email_user:
                        return [{
                            "id": id,
                            "status": "error",
                            "message": "Email address not found in account configuration" 
                        }]
                    
                    details , total_emails , fetch_count = fetcher.get_emails(id, email_user, email_pass, 
                                               max_emails=max_emails, 
                                               end_date=end_date,
                                               fetch_all=fetch_all)
                    
                    if isinstance(details, list):
                        return details , total_emails , fetch_count
                    else:
                        return [details] , total_emails , fetch_count
                else:
                    return [{
                        "id": id,
                        "status": "error",
                        "message": f"Account with ID {id} not found"
                    }] , total_emails , fetch_count
            
            return results if results else [{
                "status": "error",
                "message": "No emails could be fetched from any account"
            }] , total_emails , fetch_count
                    
        except Exception as e:
            return [{
                "status": "error",
                "message": f"Fetch operation failed: {e}"
            }] , total_emails , fetch_count


# # Test the fetcher when run directly
# if __name__ == "__main__":
# #     print("Testing email fetcher...")
    
# #     # Test with different parameters
# #     print("\n1. Testing with default parameters (10 emails):")
# #     emails = fetcher.fetch()
# #     print(f"Fetched {len(emails)} email(s)")
    
# #     print("\n2. Testing with max_emails=5:")
# #     emails = fetcher.fetch(max_emails=5)
# #     print(f"Fetched {len(emails)} email(s)")
# #     print(emails)
    
# #     print("\n3. Testing with end_date (before 01-Dec-2024):")
    # emails = fetcher.fetch(id=2 ,max_emails=50,fetch_all=True, end_date="27-Aug-2025")
    # print(f"Fetched {len(emails)} email(s)")
    # print(emails)
