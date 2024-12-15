# talk-to-db

## Repository Overview
The repository **talk-to-db** contains code for the streamlit web application that performs SQL database operations using natural language, powered by the Gemini 1.5 Pro flash model.

## Prerequisites
- Python 3.8 or higher installed
- Google Cloud SDK installed and authenticated
- Access to the Google Cloud project containing your Cloud SQL instance

## Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd talk-to-db
   ```

2. **Set Up Virtual Environment**

   - **Linux/MacOS:**
     ```bash
     python3 -m venv talk2db
     source talk2db/bin/activate
     ```

   - **Windows:**
     ```bash
     python -m venv talk2db
     talk2db\Scripts\activate
     ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Insert Environment Variables**
   Create a `.env` file in the root of the project and populate it with the following variables:
   ```env
   LOCATION=<Your Cloud Region>
   PROJECT_ID=<Your Google Cloud Project ID>
   MODEL_NAME=<Name of the Gemini 1.5 Pro Model>
   CLOUDSQL_IP=<Cloud SQL Instance IP Address>
   DATABASE_NAME=<Your Database Name>
   PORT=<Database Port, e.g., 3306>
   PASSWORD=<Your Database Password>
   FB_API_KEY=<FB_API_KEY>
   FB_AUTH_DOMAIN=<FB_AUTH_DOMAIN>
   FB_DB_URL=<FB_DB_URL>
   FB_PROJECT_ID=<FB_PROJECT>
   FB_STORAGE_BUCKET=<FB_STORAGE_BUCKET>
   FB_MSG_SENDER_ID=<FB_MSG_SENDER_ID>
   FB_APP_ID=<FB_APP_ID>
   FB_MEASUREMENT_ID=<FB_MEASUREMENT_ID>
   ```

5. **Set Up Cloud SQL Proxy**
   Follow the instructions at [Google Cloud SQL Proxy Documentation](https://cloud.google.com/sql/docs/mysql/connect-instance-auth-proxy) to download and start the Cloud SQL Auth Proxy.

   Example:
   ```bash
   ./cloud-sql-proxy <INSTANCE_CONNECTION_NAME>
   ```

   - **Linux/MacOS:**
     ```bash
     ./cloud-sql-proxy <INSTANCE_CONNECTION_NAME>
     ```

   - **Windows:**
     ```cmd
     cloud-sql-proxy.exe <INSTANCE_CONNECTION_NAME>
     ```

6. **Run the Application**
   ```bash
   streamlit run main.py
   ```