import os
from dotenv import load_dotenv
import json
load_dotenv()

class Keys:
    
    def __init__(self):
        self.FILE_PATH = os.path.join(os.path.dirname(__file__), '.env')
        if not os.path.exists(self.FILE_PATH):
            with open(self.FILE_PATH, 'w') as f:
                pass
    def save_key(self, key_name, key_value):
        with open(self.FILE_PATH, 'a') as f:
            f.write(f"\n{key_name}={key_value}")

    def get_key(self, key_name):
        with open(self.FILE_PATH, 'r') as f:
            for line in f:
                if line.startswith(key_name):
                    return line.split('=')[1].strip()
        raise KeyError(f"{key_name} not found in .env file.")
    
    def change_key(self, key_name, new_value):
        with open(self.FILE_PATH, 'r') as f:
            lines = f.readlines()
        with open(self.FILE_PATH, 'w') as f:
            key_exist = False
            for line in lines:
                if line.startswith(key_name):
                    f.write(f"{key_name}={new_value}\n")
                    key_exist = True
                else:
                    f.write(line)
        if not key_exist:
            raise KeyError(f"{key_name} not found in .env file.")
        return f"{key_name} changed successfully."

class Account:
    def __init__(self):
        self.ACCOUNTS_PATH = os.path.join(os.path.dirname(__file__), 'email_handler/accounts.json')
        if not os.path.exists(self.ACCOUNTS_PATH):
            with open(self.ACCOUNTS_PATH, 'w') as f:
                pass
            
    def  add_account(self,email, PASS_KEY):
        with open(self.ACCOUNTS_PATH,'r') as f:
            accounts = json.load(f)
        if email in accounts:
            raise ValueError("Email already exists.")

        id = len(accounts['accounts'])+1
        accounts['accounts'][id] = {
            'email': email,
            'pass_key': f"ACCOUNT_{id}"
        }
        key_mnager = Keys()
        key_mnager.save_key(f"ACCOUNT_{id}", PASS_KEY)
        with open(self.ACCOUNTS_PATH, 'w') as f:
            json.dump(accounts, f, indent=4)
        return f"Account added with ID: {id}"
    
    def change_pass_key(self, email, new_pass_key):
        with open(self.ACCOUNTS_PATH, 'r') as f:
            accounts = json.load(f)
        for account in accounts['accounts'].values():
            if account['email'] == email:
                account['pass_key'] = new_pass_key
                with open(self.ACCOUNTS_PATH, 'w') as f:
                    json.dump(accounts, f, indent=4)
                return f"Pass key for {email} changed successfully."
        raise ValueError("Email not found.")
    
    def get_accounts(self):
        with open(self.ACCOUNTS_PATH, 'r') as f:
            accounts = json.load(f)
        return accounts



# if __name__ == "__main__":
#     account_manager = Account()
#     accounts = account_manager.get_accounts()
#     print(accounts)
#     print(account_manager.add_account("123@gmail.com","PASS_KEY_3"))