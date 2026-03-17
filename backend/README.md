# Safe & Sound - Backend

This is the FastAPI backend for the Safe & Sound application.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd MissedCall/backend
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Variables:**
    Copy `.env.template` to `.env` and fill in all the required credentials (Supabase, Twilio, Anthropic, Exotel, Redis).
    ```bash
    cp .env.template .env
    ```

5.  **Run the server:**
    ```bash
    uvicorn main:app --reload
    ```
