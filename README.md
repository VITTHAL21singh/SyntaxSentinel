# SyntexSentinal

A local-first, privacy-conscious application security auditing tool designed to analyze network diagrams, configuration files, and code snippets for vulnerabilities. Built for rapid offline threat modeling, it routes visual context and custom queries to a locally hosted Gemma 4 model, returning strictly formatted JSON audits and persisting results to a local database.

Developed for the Hacktober/0x0 PIR4T3S Hackathon track.

## Tech Stack
*   **Backend:** Python, Flask
*   **Database:** SQLite ORM via Prisma Python
*   **AI Inference:** Ollama (Local offline execution)
*   **Model:** `gemma4:31b-cloud`
*   **Frontend:** Vanilla HTML, CSS, JavaScript (Light-mode UI)

## Prerequisites
*   Python 3.10+
*   Node.js & npm (for Prisma CLI)
*   [Ollama](https://ollama.com/) installed locally

## Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/your-repo.git
   cd your-repo
   ```

2. **Set up the virtual environment**
   ```bash
   python -m venv env
   env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask ollama prisma
   ```

4. **Initialize the Database**
   Push the Prisma schema to create the local SQLite `dev.db` file and generate the client.
   ```bash
   npx prisma db push
   prisma generate
   ```

5. **Pull the AI Model**
   *Note: This model is 5.5 GB. Ensure your target drive (e.g., D: drive) has sufficient space.*
   ```bash
   ollama pull gemma4:31b-cloud
   ```

## Running the Application

1. Ensure the Ollama engine is running in the background.
2. Start the Flask server:
   ```bash
   python app.py
   ```
3. Navigate to `http://localhost:8080` in your browser.
4. To view the local security logs, launch Prisma Studio:
   ```bash
   npx prisma studio
   ```

## Usage
1. Click **Attach Image** to upload a screenshot of a vulnerable code block, AWS IAM policy, or network architecture diagram.
2. Provide specific audit instructions in the **Context** input box (e.g., "Ignore SQL injection, focus on hardcoded secrets").
3. Click **Send** to route the query to Gemma 4. The parsed vulnerability, severity badge, and remediation steps will render on the UI and save to the SQLite database.
