import pandas as pd


def prepare_time_series_data(analysis_data, start_date, end_date, grouping='1M'):
    """
    Prepares a dataframe for visualizing sentiment ratios over time.

    :param analysis_data: The JSON-like dictionary containing analysis results.
    :param start_date: The start date for the period of interest (datetime object).
    :param end_date: The end date for the period of interest (datetime object).
    :param grouping: The grouping period for the time series ('1W', '1M', '3M', 'Y'). Default is '1M'.

    :return: DataFrame grouped by time and sentiment ratio.
    """

    # Convert the created_at timestamps to datetime objects
    df = pd.DataFrame(analysis_data['llm_results'])
    df['created_at'] = pd.to_datetime(df['created_at'], unit='s')

    # Filter data to the specified date range
    df_filtered = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

    # Group by the specified period for time series and sentiment
    df_grouped = (
        df_filtered
        .groupby([pd.Grouper(key='created_at', freq=grouping), 'sentiment'])
        .size()
        .unstack(fill_value=0)
    )

    # Calculate the ratio of each sentiment
    df_ratios = df_grouped.div(df_grouped.sum(axis=1), axis=0)

    return df_ratios


def prepare_spam_barchart_data(analysis_data, start_date, end_date):
    """
    Prepares a dataframe for visualizing spam distribution as a bar chart.

    :param analysis_data: The JSON-like dictionary containing analysis results.
    :param start_date: The start date for the period of interest (datetime object).
    :param end_date: The end date for the period of interest (datetime object).

    :return: pd.DataFrame: DataFrame for spam distribution as a bar chart.
    """

    # Convert the created_at timestamps to datetime objects
    df = pd.DataFrame(analysis_data['llm_results'])
    df['created_at'] = pd.to_datetime(df['created_at'], unit='s')

    # Filter data to the specified date range
    df_filtered = df[(df['created_at'] >= start_date) & (df['created_at'] <= end_date)]

    # Prepare DataFrame for sentiment distribution as a bar chart
    df_sentiment_barchart = df_filtered['spam'].value_counts(normalize=True).reset_index()
    df_sentiment_barchart.columns = ['spam', 'freq']
    df_sentiment_barchart['spam'] = df_sentiment_barchart['spam'].map({'spam': 'Spam', 'not_spam': 'Not Spam'})
    df_sentiment_barchart['freq'] = df_sentiment_barchart['freq'] * 100
    df_sentiment_barchart = df_sentiment_barchart.rename(columns={'spam': 'Spam', 'freq': 'Percentage'})

    return df_sentiment_barchart
