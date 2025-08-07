# Wildfire Tracking & Prediction
An end-to-end project for tracking, visualizing, and predicting wildfires in certain geographic regions.

---

## Purpose

To develop an automated system that combines fixed landscape data from particular geographic regions with daily-ingested climate and wildfire data to predict the daily probability of wildfire ignition across those regions. The system will provide a risk score, explain the key contributing factors for each region, and visualize patterns across the landscape.

## Outline
#### Current Stage: Planning and Learning

The project aims to follow an end-to-end data science lifecycle starting with ingestion of raw data sources to deployment of a useable app or dashboard:

0. **Planning and Learning**: AI-assisted planning of the project, along with deep dives into setting up necessary accounts, reading documentation for required tools, finding data sources, and exploring simpler but related mini-projects for ideation.
   
2.  **Data Ingestion:** Dynamic daily weather data is fetched from public sources. Static geospatial data (topography, land cover, historical fire perimeters) is sourced from USGS, NASA, CAL FIRE, etc.

3.  **Automated Processing & Storage:** A serverless GitHub Actions workflow will be set up to run daily and fetch the latest weather data and store it in a structured cloud object storage bucket (GCS/S3), which emulates a simple "data lake".

4.  **Feature Engineering:** A comprehensive data processing script will fuse all data sources. This step will create a standardized geographic grid and build a historical, analysis-ready dataset where each row represents a specific location on a specific day, with all corresponding features.

5.  **Predictive Modeling:** A classification model will be trained on the historical data to predict ignition probability. The critical challenge of a highly imbalanced dataset is addressed. The trained model is then coupled with the SHAP (SHapley Additive exPlanations) library to ensure every prediction is fully interpretable.

6.  **Interactive Visualization:** A web application/dashboard to serve as the user interface. Provides the latest daily predictions, displays a risk heatmap on an interactive map, and allows users to select any location to view a more detailed risk assessment. Utilizes model interpretability techniques like SHAP values for assessing the top risk factors.

## Tools

*   **Automation & Cloud:** GitHub Actions, Google Cloud Storage (GCS) or Amazon S3 (or similar)
*   **Data Processing:** Python, Polars, GeoPandas, Rasterio
*   **Machine Learning:** Scikit-learn, XGBoost, SHAP, LightGBM, PyTorch
*   **Visualization & Application:** Streamlit, Plotly, marimo
   
## Skills
*   **Data Engineering:** Building automated, serverless data pipelines (CI/CD); cloud data management and organization (Data Lake principles); ingesting and processing diverse data formats (API, vector, raster).
*   **Geospatial Analysis:** Fusing heterogeneous geospatial datasets; performing spatial joins and raster sampling; creating and working with standardized geographic grids.
*   **Machine Learning:** Advanced classification technique, potentially many for comparison; solving the critical problem of highly imbalanced data; implementing state-of-the-art model interpretability for Explainable AI (XAI).
*   **Application Development:** Building and deploying a full-stack, interactive data application from scratch using a modern Python framework.

