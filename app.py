import ssl
# Bypass SSL certificate verification (for local testing)
ssl._create_default_https_context = ssl._create_unverified_context

from shiny import App, render, ui
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

app_ui = ui.page_fluid(
    ui.input_select(
        id='emissiontype',
        label='Choose emission type',
        choices=['CO2', 'CH4', 'N2O'],
        selected='CO2'
    ),
    ui.input_select(
        "start_year",
        "Start Year",
        [str(year) for year in range(2004, 2023)]
    ),
    ui.input_select(
        "end_year",
        "End Year",
        [str(year) for year in range(2004, 2023)]
    ),
    ui.output_plot('myplot')
)

def server(input, output, session):
    @output
    @render.plot
    def myplot():
        # Read the pre-processed GHG data from GitHub
        url = "https://raw.githubusercontent.com/PratheepaJ/datasets/refs/heads/master/cleaned_GHG_Emissions.csv"
        df = pd.read_csv(url, encoding='latin1')
        # Convert 'Year' column to integer years
        df['Year'] = pd.to_datetime(df['Year'], format='%Y').dt.year
        # Filter data based on user-selected start and end years
        start_year = int(input.start_year())
        end_year = int(input.end_year())
        df_filtered = df[(df['Year'] >= start_year) & (df['Year'] <= end_year)]
        # Group data by Year and Province/Territory
        df_grouped = df_filtered.groupby(['Year', 'Province_Territory']).agg(
            CO2=('CO2', 'sum'),
            CH4=('CH4', 'sum'),
            N2O=('N2O', 'sum')
        ).reset_index()
        # Determine which emission type to plot
        emission_type = input.emissiontype()
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_grouped, x='Year', y=emission_type, hue='Province_Territory', marker='o')
        plt.title(f'{emission_type} Emissions Trend')
        plt.xlabel('Year')
        plt.ylabel(f'Total {emission_type} Emissions (Tonnes)')
        plt.legend(title='Province/Territory', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(ticks=np.arange(df_grouped['Year'].min(), df_grouped['Year'].max() + 1, 1), rotation=45)
        plt.grid(True)
        return plt.gcf()

app = App(app_ui, server)

if __name__ == "__main__":
    app.run()