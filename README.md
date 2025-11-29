# Research Integrity Project

The **Research Integrity Project** is a web application designed to help researchers and institutions verify the integrity of scientific journals and publishers. It provides tools to detect predatory practices, analyze conflicts of interest, and ensure compliance with ethical standards.

## Features

- **Predatory Journal Detection**: Analyze journals against a comprehensive database of known predatory publishers and journals.
- **Conflict of Interest Analysis**: AI-powered analysis of potential conflicts of interest in research papers.
- **ISSN Verification**: Automated verification of Online and Print ISSNs.
- **User Dashboard**: Manage analysis history and reports.
- **Authentication**: Secure login and registration system.

## Tech Stack

- **Backend**: Python 3.13+, FastAPI, SQLAlchemy, SQLite.
- **Frontend**: HTML5, CSS3, JavaScript (served statically by FastAPI).
- **AI/ML**: OpenAI API for text analysis and summarization.
- **Database**: SQLite (`ria.db`).

## Prerequisites

- Python 3.13 or higher.
- `pip` (Python package manager).
- OpenAI API Key (for AI features).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd RIA
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1.  Create a `.env` file in the root directory (copy from `.env.example` if available, or use the template below):

    ```env
    # Core
    SECRET_KEY=your_secret_key_here
    
    # AI Services
    OPENAI_API_KEY=sk-...

    # Social Login (Optional)
    GOOGLE_CLIENT_ID=...
    GOOGLE_CLIENT_SECRET=...
    ```

## Running the Application

1.  **Start the server:**
    ```bash
    uvicorn backend.main:app --reload
    ```

2.  **Access the application:**
    Open your browser and navigate to `http://127.0.0.1:8000`.

## Project Structure

```
RIA/
├── backend/                # Python Backend
│   ├── api/                # API Endpoints (Routes)
│   ├── core/               # Configuration & Security
│   ├── database/           # Database Models & Session
│   ├── engine/             # Core Logic (Scorer, LLM, etc.)
│   ├── schemas/            # Pydantic Models (Data Validation)
│   ├── scripts/            # Utility Scripts (Scraping, Seeding)
│   └── main.py             # Application Entry Point
├── frontend/               # Static Frontend Assets
│   ├── css/                # Stylesheets
│   ├── js/                 # JavaScript Logic
│   └── *.html              # HTML Pages
├── RESOURCES/              # Data Resources (Excel lists, etc.)
├── ria.db                  # SQLite Database
└── requirements.txt        # Python Dependencies
```

## Database & Scripts

- **Database Initialization**: The database tables are automatically created when the application starts.
- **Data Ingestion**:
    - The system uses `backend/scripts/scrape_issn.py` to generate the initial database of journals and publishers from Excel files in `RESOURCES/`.
    - To run the scraper:
      ```bash
      python3 backend/scripts/scrape_issn.py
      ```
