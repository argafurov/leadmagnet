import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer, PageTemplate, Frame, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

# Import your analysis functions
from src.innorep.analyze.prepare import prepare_time_series_data, prepare_spam_barchart_data


def load_json(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return None


def create_time_series_chart(df_time_series, grouping, filename):
    # Prepare data without resetting index to avoid the issue with palette keys
    df_melted = df_time_series.reset_index().melt(id_vars='created_at', var_name='sentiment', value_name='count')

    # Convert 'created_at' to datetime if not already
    df_melted['created_at'] = pd.to_datetime(df_melted['created_at'])

    # Set Seaborn style for a professional look
    sns.set(style="whitegrid")

    # Define custom colors
    palette = {'positive': 'lightblue', 'neutral': 'grey', 'negative': 'lightcoral'}

    # Create the plot using Seaborn for a cleaner and more professional look
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df_melted, x='created_at', y='count', hue='sentiment', palette=palette, lw=3)

    # Customize the plot with labels and title
    plt.xlabel('', fontsize=12)
    plt.ylabel('', fontsize=12)
    plt.xticks(rotation=45)
    plt.yticks(ticks=[i * 0.1 for i in range(1, 11) if i % 2 == 0], labels=[f"{10*i}%" for i in range(1, 11) if i % 2 == 0])
    plt.legend(title='Sentiment', loc='upper left')

    # Remove image borders
    sns.despine()

    # Save the figure
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def create_spam_distribution_chart(df_spam_barchart, filename):
    # Prepare data
    labels = df_spam_barchart['Spam']
    percentages = df_spam_barchart['Percentage']

    # Plot
    plt.figure(figsize=(7, 7))
    colors = ['lightcoral', 'lightblue']  # Use same colors as sentiment: lightcoral for Spam and lightblue for Not Spam
    plt.pie(percentages, labels=labels, colors=colors, startangle=90, counterclock=False, textprops={'fontsize': 20},
            wedgeprops=dict(width=0.4, edgecolor='w'), autopct='%1.1f%%', pctdistance=0.8)

    # Show the figure
    plt.tight_layout()
    plt.savefig(filename, transparent=True)
    plt.close()


def header_footer(canvas, doc):
    canvas.saveState()

    # Draw the background image
    current_dir = Path(__file__).resolve().parent
    bg_image_path = current_dir / 'background.jpg'  # Replace with your image filename
    bg_image = ImageReader(bg_image_path)
    width, height = A4  # Use A4 dimensions
    canvas.drawImage(bg_image, 0, 0, width=width, height=height)

    styles = getSampleStyleSheet()

    # Header
    header_style = styles['Normal']
    header_style.fontSize = 9
    header_style.textColor = colors.grey

    current_date = datetime.now().strftime('%Y-%m-%d')
    header_text = Paragraph(f"InnoRep Analytical Report - {current_date}", header_style)
    w, h = header_text.wrap(doc.width, doc.topMargin)
    header_text.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h + 60)

    # # Optional: Add a logo to the header
    # logo = ImageReader(current_dir / 'logo.png')  # Replace with your logo's path
    # canvas.drawImage(logo, doc.width - inch, doc.height + doc.topMargin - h + 5, width=150, height=50)

    # Footer
    footer_style = styles['Normal']
    footer_style.fontSize = 7
    footer_style.textColor = colors.grey

    footer_text = Paragraph(
        "This is a demo. The full version delivers deeper insights and personalized strategies to elevate your audience engagement and reputation.",
        footer_style
    )
    w, h = footer_text.wrap(doc.width, doc.bottomMargin)
    footer_text.drawOn(canvas, doc.leftMargin, h)

    canvas.restoreState()


def create_pdf_report(output_path, chart_images, analysis_data, start_date, end_date, df_spam_barchart, df_time_series):
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    flowables = []

    positive_max_date_var = True
    positive_max_date = True
    negative_max_date = True

    # Reset index to ensure 'created_at' is a column
    df_time_series = df_time_series.reset_index()
    for col in ['positive', 'neutral', 'negative']:
        if col not in df_time_series.columns:
            df_time_series[col] = 0
            if col == 'positive':
                positive_max_date = False
            elif col == 'negative':
                negative_max_date = False

    # Title
    title = Paragraph(f"Sentiment & Engagement Report Demo for {analysis_data['username']}", styles['Title'])
    flowables.append(title)
    flowables.append(Spacer(1, 12))

    # Sentiment Dynamics
    flowables.append(Paragraph("Sentiment Dynamics", styles['Heading2']))
    flowables.append(Image(chart_images['time_series_chart'], width=6*inch, height=3*inch))
    flowables.append(Spacer(1, 12))

    # Analyze df_time_series for spikes
    if positive_max_date:
        positive_max = df_time_series['positive'].max()
        positive_max_date = df_time_series[df_time_series['positive'] == positive_max]['created_at'].values[0]
        positive_max_date = pd.to_datetime(positive_max_date).strftime('%B %d, %Y')
        if df_time_series['positive'].var() == 0:
            positive_max_date_var = False

    if negative_max_date:
        negative_max = df_time_series['negative'].max()
        negative_max_date = df_time_series[df_time_series['negative'] == negative_max]['created_at'].values[0]
        negative_max_date = pd.to_datetime(negative_max_date).strftime('%B %d, %Y')

    # sentiment_text = f"The highest positive sentiment was observed on {positive_max_date}, while the highest negative sentiment occurred on {negative_max_date}."
    sentiment_text = ""
    if positive_max_date and negative_max_date:
        sentiment_text = (
            f"Positive sentiment peaked on {positive_max_date}, signaling strong audience engagement, while the most "
            f"significant negative sentiment occurred on {negative_max_date}, highlighting a potential concern to address."
        )
    elif positive_max_date and positive_max_date_var:
        sentiment_text = (
            f"Positive sentiment peaked on {positive_max_date}, indicating strong audience engagement."
        )
    elif positive_max_date and not positive_max_date_var:
        sentiment_text = (
            "Positive sentiment was consistently high throughout the period, indicating strong audience engagement."
        )
    elif negative_max_date:
        sentiment_text = (
            f"The most significant negative sentiment occurred on {negative_max_date}, highlighting a potential concern to address."
        )
    sentiment_paragraph = Paragraph(sentiment_text, styles['Normal'])
    flowables.append(sentiment_paragraph)
    flowables.append(Spacer(1, 12))

    # Spam Distribution
    flowables.append(Paragraph("Spam Distribution", styles['Heading2']))

    # Extract spam percentage
    try:
        spam_percentage = df_spam_barchart[df_spam_barchart['Spam'] == 'Spam']['Percentage'].values[0]
    except IndexError:
        spam_percentage = 0.0

    # Create paragraph with template
    if spam_percentage == 0:
        spam_text = "No spam interactions were detected, indicating a high-quality audience engagement."
    else:
        low_spam_template = "Only {spam_percentage}% of your audience interactions were identified as spam, indicating high-quality engagement from authentic users."
        mid_spam_template = "{spam_percentage}% of interactions are spam, showing moderate engagement with room to improve user quality."
        high_spam_template = "{spam_percentage}% of interactions are spam, suggesting a need to attract more authentic users."
        spam_percentage = round(spam_percentage, 1)
        if spam_percentage < 10:
            spam_text = low_spam_template.format(spam_percentage=spam_percentage)
        elif spam_percentage < 25:
            spam_text = mid_spam_template.format(spam_percentage=spam_percentage)
        else:
            spam_text = high_spam_template.format(spam_percentage=spam_percentage)
    spam_paragraph = Paragraph(spam_text, styles['Normal'])

    # Create table with image and paragraph
    spam_image = Image(chart_images['spam_chart'], width=3.5*inch, height=3.5*inch, hAlign='LEFT')
    data = [[spam_image, spam_paragraph]]
    table = Table(data, colWidths=[3.5*inch, 3.5*inch])

    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    flowables.append(table)

    # Define the frame and template for header, footer, and background
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')
    template = PageTemplate(id='background', frames=frame, onPage=header_footer)
    doc.addPageTemplates([template])

    # Build PDF
    doc.build(flowables)


def main(profile_name, output_pdf):
    # Adjust paths using Path objects
    json_path = Path(__file__).resolve().parent / "analysis_results" / f"analysis_{profile_name}.json"

    # Load analysis data
    analysis_data = load_json(json_path)
    if not analysis_data:
        print("Failed to load analysis data.")
        return

    # Define date range and grouping
    start_date = datetime(2023, 1, 1)
    end_date = datetime.now()
    grouping = '1M'

    # Prepare data
    df_time_series = prepare_time_series_data(analysis_data, start_date, end_date, grouping=grouping)
    df_spam_barchart = prepare_spam_barchart_data(analysis_data, start_date, end_date)

    # Create and save charts
    charts_dir = Path(__file__).resolve().parent / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    time_series_chart_file = charts_dir / 'time_series_chart.png'
    spam_chart_file = charts_dir / 'spam_chart.png'

    create_time_series_chart(df_time_series, grouping, str(time_series_chart_file))
    create_spam_distribution_chart(df_spam_barchart, str(spam_chart_file))

    # Create PDF report
    chart_images = {
        'time_series_chart': str(time_series_chart_file),
        'spam_chart': str(spam_chart_file)
    }

    create_pdf_report(output_pdf, chart_images, analysis_data, start_date, end_date, df_spam_barchart, df_time_series)

    print(f"PDF report has been generated: {output_pdf}")
