import streamlit as st
import os 
import json
from email_handler import fetch_emails

st.set_page_config(page_title="Email Assistant", layout="wide")

# Initialize session state safely
if 'account' not in st.session_state:
    st.session_state.account = None
if 'account_id' not in st.session_state:
    st.session_state.account_id = None

pages = st.sidebar.selectbox("Select Page", ["Account", "Summary", "Emails"])

def read_file(file):
    with open(file, "rb") as file:
        return json.load(file)

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
        # st.write(f"Account ID: {st.session_state.account_id}")
    else:
        st.warning("## Please select an email account on the Account page.")
