LAB 6 - LAPTOP SPECIFICATION ANALYSIS

FILES
- laptop_analysis_app.py : Streamlit dashboard source code
- laptop_dataset.csv     : Dataset used by the dashboard
- requirements.txt       : Python libraries required
- Lab6_Report.docx       : Project documentation

RUN LOCALLY
1. Open a terminal in this folder.
2. Install the required libraries:
   pip install -r requirements.txt
3. Start the application:
   streamlit run laptop_analysis_app.py
4. Open the local URL shown in the terminal (usually http://localhost:8501).

DEPLOY ON STREAMLIT COMMUNITY CLOUD
1. Sign in to Streamlit Community Cloud using your GitHub account.
2. Create a GitHub repository and upload all files in this folder.
3. In Streamlit Community Cloud, select the repository and branch.
4. Set the app file path to laptop_analysis_app.py.
5. Deploy the application and copy its public URL into the report.

NOTE
The dataset must remain in the same folder/repository as the Python file.
The dataset contains laptop specifications but no price column.
