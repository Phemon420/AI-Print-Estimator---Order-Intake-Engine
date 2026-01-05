# Project Setup and Documentation

## Setup Instructions

Follow these steps to get the project up and running:

1.  **Start the Tunnel**
    Start the cloudflared tunnel to expose your local service.
    ```bash
    choco install cloudflared
    cloudflared tunnel --url http://127.0.0.1:8002/
    ```

2.  **Run Docker Containers**
    Start the necessary services using Docker Compose.
    ```bash
    docker compose up -d
    ```

3.  **Create Virtual Environment**
    Navigate to the backend folder and create a Python virtual environment.
    ```bash
    cd ./backend
    python -m venv venv
    ```

4.  **Activate Virtual Environment**
    Activate the newly created virtual environment.
    *   **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```

5.  **Install Dependencies**
    Install the required Python packages.
    ```bash
    pip install -r requirements.txt
    ```

6.  **Create Alembic commit**
    create an commit inside alembic.
    ```bash
    alembic revision -m "manual migration"
    ```

7.  **Update the db with alembic**
    run the updation command
    ```bash
    alembic upgrade head
    ```

8.  **Run the Server**
    Start the Uvicorn server with hot reload enabled.
    ```bash
    uvicorn main:app --reload
    ```

9.  **Import n8n Workflows**
    Open your n8n instance and import all the JSON files located in the root folder of this repository.

---

## Telegram Bot Configuration

Follow these steps to create and configure your Telegram Bot:

1.  Open Telegram and search for **BotFather** (@BotFather).
2.  Start a chat with BotFather and send the command `/newbot`.
3.  Follow the prompts to choose a name and a username for your bot.
4.  Once created, BotFather will provide you with an **Access Token** (API Token).
5.  Copy this token. You will need it to configure your application and n8n nodes.

---

## API Documentation

Here are the data models for the available API endpoints.

### 1. Order Input
This endpoint is used to receive order inputs.

**Data Model:** `order_input`

```python
from pydantic import BaseModel
from typing import Optional, Union

class order_input(BaseModel): 
    telegram_id: Optional[Union[str, int]] = None 
    email_id: Optional[str] = None 
    input_text: str
```

### 2. Escalation / Status Update
This endpoint is used to update the status of an order.

**Data Model:** `status_update`

```python
from pydantic import BaseModel

class status_update(BaseModel): 
    order_id: str 
    status_level: str 
```

---

## Environment Variables

1.  Locate the `.env` file (or `.env.example`) in the project root or backend directory.
2.  Fill in the environment variables with the correct values.
3.  Ensure your Telegram Bot Token and other API keys are correctly set.

---

## Google Developer Console & n8n OAuth Setup

To use Gmail services within n8n, you need to configure OAuth credentials in the Google Developer Console.

1.  **Google Cloud Console**
    *   Go to the [Google Cloud Console](https://console.cloud.google.com/).
    *   Create a new project or select an existing one.

2.  **Enable APIs**
    *   Navigate to **APIs & Services** > **Library**.
    *   Search for **Gmail API** and enable it.

3.  **Configure OAuth Consent Screen**
    *   Go to **APIs & Services** > **OAuth consent screen**.
    *   Select **External** (unless you are a G Suite user testing internally).
    *   Fill in the required app information (App name, User support email, Developer contact information).
    *   Add Scopes: Search for and add scopes related to Gmail (e.g., `https://www.googleapis.com/auth/gmail.send`, `https://www.googleapis.com/auth/gmail.readonly`).
    *   Add Test Users: Add the email address you will be using to authenticate.

4.  **Create Credentials**
    *   Go to **APIs & Services** > **Credentials**.
    *   Click **Create Credentials** > **OAuth client ID**.
    *   **Application Type:** Select **Web application**.
    *   **Name:** Give it a descriptive name (e.g., "n8n OAuth").
    *   **Authorized Redirect URIs:** You need to get this URL from n8n.
        *   In n8n, open the Gmail node or Credentials setup.
        *   Create a new **Google OAuth2 API** credential.
        *   Copy the **OAuth Redirect URL** provided by n8n.
        *   Paste this URL into the "Authorized redirect URIs" field in Google Console.
    *   Click **Create**.

5.  **Configure n8n**
    *   Copy the **Client ID** and **Client Secret** from the Google Console.
    *   Paste them into the corresponding fields in the n8n credential configuration.
    *   Click **Connect my account** (or the sign-in button) in n8n to authenticate and authorize the app.
