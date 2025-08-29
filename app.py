import streamlit as st
import os 
import json
from email_handler import fetch_emails , model
from email_handler.model import Model
from datetime import date
st.set_page_config(page_title="Email Assistant", layout="wide")

# Initialize session state safely
if 'account' not in st.session_state:
    st.session_state.account = None
if 'account_id' not in st.session_state:
    st.session_state.account_id = None

pages = st.sidebar.selectbox("Select Page", ["Account", "Summary", "History","Settings"])

def read_file(file):
    with open(file, "rb") as file:
        return json.load(file)
    
def add_data_to_history(date_key, new_object,file_path=os.path.join(os.getcwd(),'history.json')):
    """
    Adds a new object to a list for a given date key in a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        date_key (str): The date key to add the object to.
        new_object (dict): The new object to add.
    """
    if new_object is None or date_key is None:
        return
    data = read_file(file_path)
    
    if date_key in data:
        data[date_key].append(new_object)
    else:
        data[date_key] = [new_object]
        
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_accounts(file_path):
    data = read_file(file_path)
    accounts = data["accounts"]
    return accounts

accounts = get_accounts(os.path.join(os.getcwd(),"email_handler", "accounts.json"))

if pages == "Account":
    if len(accounts) > 0:
        st.write("### Select an Email Account")
        account_emails = [account['email'] for account in accounts.values()]
        selected_account = st.selectbox("Email Accounts", account_emails)
        if st.button("Use Selected Account"):
            key = [key for key, value in accounts.items() if value['email'] == selected_account][0]
            st.session_state.account = accounts[key]['email']
            st.session_state.account_id = key
            st.success(f"Using account: {selected_account}")
            st.write(f"email: {st.session_state.account}, id: {st.session_state.account_id}")
    else:
        st.warning("No email accounts found. Please add an account.")

elif pages == "Summary":
    if st.session_state.account:
        st.write(f"### Account: {st.session_state.account}")

        # Set defaults in session_state if not already present
        if "seen_status" not in st.session_state:
            st.session_state.seen_status = "Seen"
        if "num_emails" not in st.session_state:
            st.session_state.num_emails = 10
        if "end_date" not in st.session_state:
            st.session_state.end_date = None

        # Columns for inputs
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            st.session_state.seen_status = st.radio(
                "Emails", ["Seen", "Unseen"], horizontal=True, index=0 if st.session_state.seen_status == "Seen" else 1)

        with col2:
            st.session_state.num_emails = st.slider(
                "Number of Emails", 1, 50, st.session_state.num_emails)

        with col3:
            # Use key to persist and show correct default
            new_date = st.date_input("End Date", value=st.session_state.end_date or None)
            st.session_state.end_date = new_date

        # Convert Seen/Unseen to boolean
        fetch_seen = True if st.session_state.seen_status == "Seen" else False
        st.write(f"Option selected: {st.session_state.seen_status}, {fetch_seen}")
        st.write(f"Number of Emails: {st.session_state.num_emails}")
        if st.button("Fetch and Summarize Emails"):
            emails , total_emails , fetch_count = fetch_emails.fetcher.fetch(
                id=st.session_state.account_id,
                max_emails=st.session_state.num_emails,
                end_date=st.session_state.end_date,
                fetch_all=fetch_seen
            )
            model_instance = Model()
            summaries = {}
            st.markdown(f"### Fetched {fetch_count} email(s) out of {total_emails} available.")
            for i, email in enumerate(emails, start=1):
                summary = model_instance.summerize(email.get('Body', ''))
                summaries[i] = {
                    "Subject" : email.get('Subject', 'No Subject'),
                    "From" : email.get('From', 'Unknown Sender'),
                    "Date" : email.get('Date', 'Unknown Date'),
                    "Summery" : summary}
                st.markdown(f"### Subject: {email.get('Subject', 'No Subject')}")
                st.markdown(f"**From:** {email.get('From', 'Unknown Sender')}")
                st.markdown(f"**Date:** {email.get('Date', 'Unknown Date')}")
                st.markdown(f"**Summary:** {summary}")
                st.markdown("___")
                # ({
                #     "Subject" : email.get('Subject', 'No Subject'),
                #     "From" : email.get('From', 'Unknown Sender'),
                #     "Date" : email.get('Date', 'Unknown Date'),
                #     "Summery" : summary})
            add_data_to_history(date_key=str(date.today()), new_object=summaries)
            st.success(f"Fetched and summarized {len(emails)} email(s).")
    else:
        st.warning("### Please select an email account on the Account page.")
elif pages == "History":
    st.write("### Email Summary History")
    history_data = read_file(os.path.join(os.getcwd(),'history.json'))
    if history_data:
        date_key = history_data.keys()
        history_date = st.selectbox("Select Date", date_key, key="history_date")
        if history_date:
            history_data = {history_date: history_data[history_date]}
        for date_key, summaries in history_data.items():
            st.markdown(f"## Date: {date_key}")
            for summary in summaries:
                for idx, details in summary.items():
                    st.markdown(f"### Email {idx}")
                    st.markdown(f"**Subject:** {details.get('Subject', 'No Subject')}")
                    st.markdown(f"**From:** {details.get('From', 'Unknown Sender')}")
                    st.markdown(f"**Date:** {details.get('Date', 'Unknown Date')}")
                    st.markdown(f"**Summary:** {details.get('Summery', 'No Summary')}")
                    st.markdown("___")
    else:
        st.info("No history available.")

# elif pages == "Summary":
#     if st.session_state.account:
#         st.write(f"### Account: {st.session_state.account}")
#         col1, col2, col3 = st.columns([1,1,1])
#         with col1:
#             option = st.radio("Emails", ["Seen", "Unseen"], horizontal=True, key="seen_status")
#             st.write(f"Option selected: {option}")
#         with col2:
#             no_of_emails_wanted = st.slider("Number of Emails", 1, 50, 10, key="num_emails")
#             if st.button("Submit Number"):
#                 st.write(f"Number of Emails: {no_of_emails_wanted}")
#             else:
#                 no_of_emails_wanted = 10
#         # st.write(f"Account ID: {st.session_state.account_id}")
#         with col3:
#             end_data = st.date_input("End Date")
#             if st.button("Submit Data"):
#                 st.write(f"End Date: {end_data}")
#             else:
#                 end_data = None
#             # print(end_data)
#         option = True if option=="Seen" else False
#         if st.button("Fetch and Summarize Emails"):
#             emails = fetch_emails.fetcher.fetch(id=st.session_state.account_id, max_emails=no_of_emails_wanted, end_date=end_data, fetch_all=option)
#             for email in emails:
#                 print(st.session_state.account_id)
#                 st.write(emails)
#     else:
#         st.warning("### Please select an email account on the Account page.")
