# Wildfire Tracking & Prediction

>#### **Prerequisites**
>This project assumes basic familiarity with Python, familiarity with predictive modeling, and a GitHub account for version control and automation, and an account with a cloud provider like Google Cloud Platform (GCP) or Amazon Web Services (AWS) for storage. If one or more of these prerequisites is not met, additional required learning (or creation of accounts) will increase time-to-completion but not render the project unapproachable. 

### **STEP 1: Data Sources - A Mix of Dynamic and Static**

This foundational step is critical, as the quality and relevance of your data directly impact model accuracy. We will act as data detectives, combining frequently changing (dynamic) data with fixed (static) data. Focusing on a specific region like California makes the project manageable. Future updates to the project could include wider geographic regions.

---

#### **Dynamic Data (Fetched Daily): Weather's Crucial Role**

Wildfire ignition is heavily influenced by daily weather, so a reliable, up-to-date source is essential.

*   **Source:** Open-Meteo Weather API.
*   **Why it's a great choice:** It's a free, open-source API with no key required, simplifying development. It provides extensive historical and forecast data (temperature, humidity, wind speed, precipitation) for any latitude/longitude, which is crucial for training our model.
*   **Granular Details:**
    *   **API Endpoint:** Use the `/v1/forecast` endpoint with the `past_days` parameter for historical data.
    *   **Data Format:** The API returns data in JSON, which is easily parsed in Python.
    *   **Geographic Specificity:** Make requests for a grid of points covering California to create a spatially explicit risk map.
    *   **Temporal Resolution:** Requesting hourly data provides a fine-grained view, as fire risk can change significantly within a day.

---

#### **Static Data (Downloaded Once): The Unchanging Landscape**

The underlying geography and landscape are massive factors in fire risk. This data is downloaded once and stored.

*   **Source 1 (Target Variable): CAL FIRE Fire Perimeters Dataset**
    *   **What it is:** Maintained by CAL FIRE, this dataset contains polygons of historical wildfires, including location and start date. This is our "target variable"—it tells us where and when fires occurred.
    *   **Why it's essential:** To train a model, we need positive examples ("fire") to contrast with negative examples ("no fire").
    *   **Details:** It comes in GIS formats (e.g., Shapefile), requiring a library like GeoPandas. Be aware that historical data may have gaps, a common real-world challenge.

*   **Source 2 (Topography): USGS Topography Data**
    *   **What it is:** The U.S. Geological Survey (USGS) provides Digital Elevation Models (DEMs), which are raster files where each pixel value is the elevation.
    *   **Why it's essential:** Topography impacts fire behavior. From a DEM, we can derive crucial features like **elevation**, **slope** (fires move faster uphill), and **aspect** (the direction a slope faces affects fuel moisture).
    *   **Details:** Downloadable from the USGS National Map Viewer in GeoTIFF format, which can be processed with a library like `rasterio`.

*   **Source 3 (Land Cover): NASA's MODIS Land Cover Type Data**
    *   **What it is:** NASA's MODIS satellites classify the Earth's surface into types like forest, grassland, etc.
    *   **Why it's essential:** Vegetation is the fuel. A dense forest has a different risk profile than a sparse grassland. This data provides the "fuel" component of our risk equation.
    *   **Details:** The MCD12Q1 product is a yearly, 500-meter resolution dataset. It often comes in HDF format, which may require specialized Python libraries.

---

#### **What You'll Learn**
You'll learn to source and evaluate diverse data types (API, vector, raster) and understand the domain-specific importance of each data source for a real-world problem.

### **STEP 2: Scheduled Batch Processing - The Automation Engine**

We need to automatically fetch dynamic weather data daily. We will use GitHub Actions, a simple yet powerful tool integrated directly into our project's repository.

---

#### **Tool: GitHub Actions**

We'll use GitHub Actions instead of a dedicated server or complex orchestrator like Apache Airflow. It's a CI/CD platform perfect for our scheduling needs.

*   **Why it's a great choice:**
    *   **Integrated:** The automation logic is version-controlled with your code.
    *   **Serverless:** GitHub provides a temporary virtual machine ("runner") for each job, so there's no server to manage.
    *   **Cost-Effective:** A generous free tier is sufficient for this project.
    *   **Declarative:** You define the workflow in a human-readable YAML file.

---

#### **What You'll Do: A Granular Breakdown**

You will create a workflow file at `.github/workflows/daily-update.yml`. This file instructs the GitHub runner.

*   **Workflow Triggers:**
    *   **`on: schedule:`**: Defines a recurring schedule using cron syntax (e.g., `'0 8 * * *'` for 8:00 AM UTC daily). This ensures you get the previous day's complete weather data.
    *   **`on: workflow_dispatch:`**: Adds a manual "Run" button in GitHub's Actions tab, which is invaluable for testing.
*   **Job Steps:** The workflow will execute a sequence of commands on an `ubuntu-latest` runner:
    1.  **Checkout Code:** Use `actions/checkout@v4` to access your repository's scripts.
    2.  **Setup Python:** Install the required Python version.
    3.  **Install Dependencies:** Run `pip install -r requirements.txt` to install necessary libraries (e.g., `requests`, `polars`).
    4.  **Authenticate to Cloud:** Securely log in to GCS/S3 using credentials stored as **GitHub Secrets**. Never hard-code secret keys.
    5.  **Run Fetch Script:** Execute your Python script (`src/fetch_weather_data.py`), which gets the latest weather data and saves it as a date-stamped file to your cloud storage bucket.

---

#### **What You'll Learn**
You'll learn CI/CD basics, serverless automation, Infrastructure as Code (IaC) using YAML, and the critical practice of secure credential management with GitHub Secrets.

### **STEP 3: Cloud Storage - Your Project's Central Data Hub**

We need a central, reliable place for our data so all our systems (GitHub Actions, local development, the final web app) can access the same files. We'll use a cloud object storage service.

---

#### **Tool: Google Cloud Storage (GCS) or Amazon S3**

These services act as infinitely scalable hard drives on the internet. We'll use GCS as our example.

*   **Why it's a great choice:** They offer extreme durability, high availability, and accessibility from anywhere via an API. Python has excellent libraries (`google-cloud-storage`, `boto3`) for easy integration.

---

#### **What You'll Do: A Granular Breakdown**

Your cloud setup will be simple but highly organized.

1.  **Create a Single Storage "Bucket":** A bucket is your top-level container. You'll create one with a globally unique name (e.g., `my-ca-wildfire-project-2025`) in the cloud provider's web console.

2.  **Establish a Clear Folder Structure:** This logical flow is key to a maintainable pipeline.
    *   **`raw-weather-data/`**: The destination for your daily GitHub Actions job. It holds the immutable, untouched raw data from the Open-Meteo API. This is your source of truth, allowing you to replay processing if needed.
    *   **`static-geo-data/`**: Where you'll manually upload your large, unchanging files one time: the CAL FIRE perimeters, the USGS DEM, and the NASA Land Cover data. This centralizes your static assets.
    *   **`processed-model-input/`**: Will store the final, cleaned feature table after transformation (from Step 4). Saving this analysis-ready data here avoids repeating costly processing steps.

---

#### **What You'll Learn**
You'll learn the core principles of a Data Lake, effective data organization (raw vs. processed), and foundational cloud infrastructure skills transferable to countless other projects.

### **STEP 4: Data Transformation & Feature Engineering - Forging the Master Dataset**

Here, we fuse our raw ingredients—weather, topography, land cover, and historical fire data—into a single, cohesive dataset. This is a computationally intensive process that creates the fuel for our model.

---

#### **Tools: Python with Polars, GeoPandas, and Rasterio**

*   **Why this combination:** **Polars** (or Pandas) for high-performance tabular data manipulation. **GeoPandas** for vector data (our grid and fire perimeters). **Rasterio** for raster data (DEM and land cover).

---

#### **What You'll Do: A Granular Breakdown**

The goal is a massive table where **each row represents a specific grid cell on a specific day**, with feature columns and a target column (`fire_occurred`).

1.  **Create a Geographic Grid:** Define a uniform grid (e.g., 1km x 1km cells) covering California using GeoPandas. This standardizes our analysis space, allowing us to merge disparate data types. Each cell gets a unique `cell_id`.

2.  **Enrich the Grid with Static Features:** For each grid cell, sample the underlying static data to extract features.
    *   **Topography:** Use Rasterio to sample the DEM and calculate average **elevation**, **slope**, and **aspect**.
    *   **Land Cover:** Sample the MODIS raster to find the dominant land cover type.
    *   **Critical Optimization:** Save this enriched grid (cell ID + static features) as a separate file. This is a computationally expensive, one-time task that you don't want to repeat.

3.  **Build the Historical Training Dataset:** This is the main event. Iterate through every **day** in your historical period and every **grid cell**. For each "cell-day":
    *   **A. Find Weather:** Load the day's weather data.
    *   **B. Look Up Static Features:** Merge the pre-calculated static features for that cell.
    *   **C. Check for Fire (Create Target Variable):** Using a spatial join in GeoPandas, check if a fire from the CAL FIRE dataset started in that cell on that day. If yes, `fire_occurred = 1`; otherwise, `fire_occurred = 0`.

4.  **Save the Final Dataset:** Save the resulting massive table to your `processed-model-input/` folder using the **Parquet** file format. Parquet is highly efficient for large analytical datasets due to its columnar storage and high compression.

---

#### **What You'll Learn**
You'll gain hands-on experience in geospatial data processing, feature engineering, creating labeled datasets for supervised learning, and handling large data with efficient tools and formats.

### **STEP 5: Advanced Modeling & Interpretation - From Data to Actionable Insight**

Now we transition from data engineering to data science. We will train a model not only to predict wildfire probability but also to explain *why* a region is at risk.

---

#### **Tools: Python, XGBoost, and SHAP (SHapley Additive exPlanations)**

*   **Why this combination:** **XGBoost** is a powerful gradient boosting algorithm that excels at finding complex patterns in tabular data. **SHAP** is a state-of-the-art library for model interpretability, opening the "black box" to explain any individual prediction.

---

#### **What You'll Do: A Granular Breakdown**

1.  **Train a Classification Model:**
    *   **Load Data:** Load the `training_features.parquet` file from cloud storage.
    *   **Handle Imbalanced Data (Critical):** Your "no fire" days will vastly outnumber "fire" days. A naive model would just predict "no fire." To fix this, set XGBoost's `scale_pos_weight` hyperparameter to `(count of 'no fire') / (count of 'fire')`, forcing the model to pay attention to the rare positive cases.
    *   **Split Data:** Use a **chronological split** for your time-series data (e.g., train on 2015-2021, test on 2022-2023) to simulate predicting the future.
    *   **Train & Evaluate:** Train the XGBoost classifier. Evaluate its performance using metrics suited for imbalanced data like **Precision**, **Recall**, and **AUC-PR (Area Under the Precision-Recall Curve)**. Accuracy is a misleading metric here.
    *   **Save Model:** Save the trained model object to a file for later use.

2.  **Explain Your Model with SHAP:**
    *   **Create Explainer:** Load your trained model and pass it to SHAP to create an `explainer` object.
    *   **Calculate SHAP Values:** For any prediction, the explainer can calculate the exact contribution of each feature. A positive SHAP value means the feature pushed the risk up; a negative value means it pushed the risk down.
    *   **Example Interpretation:** For a cell with 85% risk, SHAP might show: `relative_humidity = +0.3` (major risk driver), `wind_speed = +0.2`, `precipitation = -0.05` (minor risk reducer). This turns a number into a story.

---

#### **What You'll Learn**
You'll master an advanced classification algorithm, learn the crucial technique for handling imbalanced data, and gain the state-of-the-art skill of model interpretability with SHAP.

### **STEP 6: Create a Daily Prediction Script**

This operational script runs every day as part of your automated workflow, using your trained model to generate the daily risk map data.

---

#### **What You'll Do in the Script**

This script is the second part of the daily GitHub Actions workflow initiated in Step 2. After the raw weather data is fetched, this script runs.

1.  **Load Assets:** Load the saved XGBoost model, the SHAP explainer, and the enriched static grid (with topography/land cover).
2.  **Prepare Today's Features:** Fetch the latest daily weather file from GCS and join it with the static grid to create a complete feature table for the current day.
3.  **Calculate Risk and Explanations:**
    *   Feed today's feature table into the XGBoost model to get a `risk_score` for every grid cell.
    *   Feed the same table into the SHAP explainer to get the SHAP values for every feature for every cell.
4.  **Save Daily Output:** Combine all this information (`cell_id`, location, `risk_score`, SHAP values) into a single DataFrame and save it to GCS as a new Parquet file named with the current date (e.g., `predictions/daily_risk_2025-08-07.parquet`).

---

#### **What You'll Learn**
You'll learn how to operationalize a machine learning model, taking it from a static, trained object to a dynamic tool that generates new insights on an automated schedule.

### **STEP 7: Advanced Interactive Visualization - The Human Interface**

This final step translates all the backend complexity into a clean, intuitive, and actionable web application for a user. The goal is to tell a clear story about wildfire risk.

---

#### **Tool: Streamlit**

Streamlit is an open-source Python library for building data apps with minimal code.

*   **Why it's the perfect choice:** You build the app in pure Python, development is incredibly fast, and it integrates seamlessly with libraries like Plotly and SHAP.

---

#### **What You'll Do: A Granular Breakdown**

Your app will be a single `app.py` script.

1.  **Data Loading and Caching:** The app will start by downloading the latest daily prediction file from GCS. Use Streamlit's `@st.cache_data` decorator on your loading function to make the app feel instantaneous by preventing re-downloads on every user interaction.

2.  **Main View: Interactive Risk Heatmap:** Use a library like **Plotly Express** to render a map of California, with each grid cell colored by its `risk_score`. This provides an immediate, high-level overview. Users can zoom, pan, and hover to see details.

3.  **Deep-Dive Interactivity: The "Risk Profile" Sidebar:** When a user selects a high-risk cell from the map or a dropdown, a sidebar updates with a detailed profile for that specific location.
    *   **1. Overall Risk Score:** Display the top-line prediction clearly (e.g., "Predicted Risk: 78%").
    *   **2. SHAP Explanation Plot:** This is the payoff. Generate a SHAP **force plot** or **waterfall plot** for the selected cell. This visually shows the features pushing risk up (in red) and down (in blue), explaining the "why" behind the prediction.
    *   **3. Forecast Trend Chart:** Identify the top 3 risk drivers from the SHAP plot. Make a live API call to Open-Meteo for the 48-hour *forecast* of those variables for that location. Display the trend in a simple line chart to answer, "Is the risk getting better or worse?"

---

#### **What You'll Learn**
You will learn to build a full-stack data application, master the art of data storytelling, design a compelling user experience, and create a practical, operational dashboard for Explainable AI (XAI).
