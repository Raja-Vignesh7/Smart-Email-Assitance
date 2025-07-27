# Smart Email Assistance

Smart Email Assistance is an application aimed at providing a user-friendly interface for email extraction, summarization, and management. The application leverages backend functionalities to fetch unread emails from Gmail accounts and uses AI-powered summarization to help users quickly understand key information and deadlines in their emails.

## Project Status

This project is currently in active development. The UI interface is being built to offer an intuitive experience for managing emails. 

## Features (Planned / In Development)

- User interface for managing multiple Gmail accounts.
- Fetch unread emails using IMAP with options to filter by date and limit the number of emails.
- AI-powered summarization of email content highlighting important details such as events, placements, internships, deadlines, and office-related updates.
- Adding events to the calendar and setting alarms automatically based on user requests.
- Monitoring of API usage to manage request and token limits.

## Installation and Setup

1. Clone the repository or download the project files.

2. Install required Python packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:

- Create a `.env` file in the project root.
- Add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

4. Configure email accounts:

- Edit the `email_handler/accounts.json` file to add your Gmail accounts and their credentials.
- Example format:
```json
{
  "accounts": {
    "1": {
      "email": "your_email@gmail.com",
      "pass_key": "your_password_or_env_var"
    }
  }
}
```
- For security, you can store passwords as environment variables and reference them in `pass_key`.

## Usage

Currently, the backend modules provide the core functionalities:

### Fetch Emails

Use the `fetcher` class in `email_handler/fetch_emails.py` to fetch unread emails.

Example:
```python
from email_handler.fetch_emails import fetcher

# Fetch up to 10 unread emails from all accounts
emails = fetcher.fetch(max_emails=10)

# Fetch all unread emails from a specific account (id=1)
emails = fetcher.fetch(id=1, fetch_all=True)
```

### Summarize Emails

Use the `Model` class in `email_handler/model.py` to generate summaries of email content.

Example:
```python
from email_handler.model import Model

model = Model()
summary = model.summerize(email_content)
print(summary)
```

## Notes

- The project currently supports Gmail accounts via IMAP.
- Ensure your Gmail accounts allow IMAP access and use app-specific passwords if 2FA is enabled.
- The AI summarization requires a valid Gemini API key.
- The UI interface is under active development and will integrate these backend features.

## License

This project is licensed under the MIT License.

---

For questions, feedback, or contributions, please open an issue or submit a pull request.
