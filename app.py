import streamlit as st
import os
import asyncio
from pathlib import Path

# Set environment variables from secrets
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
os.environ["SCRAPFLY_KEY"] = st.secrets["SCRAPFLY_KEY"]

# Import your existing functions
from src.innorep.run_scrape import scrape
from src.innorep.run_llm import main as run_analysis
from src.innorep.create_pdf import main as create_pdf_report


def main():
    st.title("InnoRep Analytical Report Generator")

    st.sidebar.title("Options")
    username = st.sidebar.text_input("Instagram Username")
    # Removed checkboxes for scraping and analysis

    if st.sidebar.button("Run"):
        try:
            # Scrape Instagram data
            st.write(f"Scraping Instagram profile: {username}")
            with st.spinner("Scraping data..."):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(scrape(username))
            st.success("Scraping completed.")

            # Analyze comments
            st.write("Analyzing comments...")
            with st.spinner("Analyzing data..."):
                run_analysis(username)
            st.success("Analysis completed.")

            # Generate PDF report
            st.write("Generating PDF report...")
            with st.spinner("Creating PDF report..."):
                # Define the output path for the PDF
                report_dir = Path(__file__).resolve().parent / 'report' / 'reports'
                report_dir.mkdir(parents=True, exist_ok=True)
                output_pdf = report_dir / f'{username}_innorep_report.pdf'
                create_pdf_report(username, str(output_pdf))
            st.success("Report generated.")

            # Display the generated report
            if output_pdf.exists():
                st.write("Generated Report:")
                with output_pdf.open("rb") as f:
                    st.download_button(
                        label="Download Report",
                        data=f.read(),
                        file_name=f"{username}_innorep_report.pdf",
                        mime="application/pdf"
                    )
            else:
                st.error("Report not found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
