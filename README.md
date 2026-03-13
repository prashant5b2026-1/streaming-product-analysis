# Streaming Platform Product Analytics

This project simulates the work of a **Product Data Analyst at a streaming platform**.  
The objective is to analyze content strategy, platform growth, and market expansion using **SQL, Python, and Power BI**.

---

# Business Problem

Streaming platforms continuously evaluate their catalog to answer strategic questions such as:

- How fast is the content library growing?
- Which genres dominate the platform catalog?
- Which genres are emerging trends?
- Which countries produce the most content?
- Is the platform relying too heavily on older content?

This project analyzes a streaming catalog dataset to generate **product intelligence insights** that could support strategic decisions.

---

# Dataset

Dataset Source: Kaggle Netflix Titles Dataset

The dataset contains information about movies and TV shows available on a streaming platform.

Main columns include:

| Column | Description |
|------|-------------|
| title | Name of the movie or TV show |
| type | Movie or TV Show |
| release_year | Year the content was released |
| country | Country of production |
| duration | Runtime or number of seasons |
| listed_in | Genre categories |
| date_added | Date when content was added to the platform |

The dataset was transformed using **feature engineering** to support deeper analytics.

---

# Tools and Technologies

Python  
Pandas  
NumPy  
PostgreSQL  
DBeaver  
SQL  
Power BI  
GitHub  

These tools simulate a typical analytics stack used by data teams.

---

# Project Workflow

The project follows a structured analytics pipeline:

Data Profiling  
→ Data Cleaning  
→ Feature Engineering  
→ SQL Product Analytics  
→ Dashboard Visualization  
→ AI Insight Generation (planned extension)

Each stage builds on the previous one to transform raw data into actionable insights.

---

# Feature Engineering

Additional analytical features were created to improve analysis:

| Feature | Description |
|------|-------------|
| year_added | Year when the content was added |
| month_added | Month when content was added |
| content_age | Age of content relative to current year |
| primary_genre | Primary genre extracted from category list |
| duration_minutes | Numeric movie runtime |
| primary_country | Simplified production country |
| is_movie | Binary indicator for movie vs TV show |

Feature engineering enables deeper **product analytics insights**.

---

# SQL Product Analytics

SQL queries were used to answer key product questions.

Examples include:

- Platform catalog growth over time
- Genre market share analysis
- Top genres by year
- Country-level production analysis
- Content age distribution
- Runtime statistics
- Pareto analysis of catalog composition

Advanced SQL techniques used:

- Window Functions
- Ranking Functions
- Aggregations
- Partitioned Analysis
- Growth Rate Calculations

---

# Dashboard

An interactive Power BI dashboard was created with four analytical sections:

### Platform Overview
Executive metrics and catalog health indicators.

### Content Growth Intelligence
Tracks platform expansion and movie vs TV show growth trends.

### Genre Strategy Intelligence
Analyzes dominant and emerging genres.

### Global Market Intelligence
Explores geographic content distribution and regional production trends.

The dashboard is designed using **analytical storytelling principles** so that insights can be understood quickly.

---

# Key Insights

Examples of insights derived from the analysis include:

- The platform catalog has expanded significantly over recent years.
- A small number of genres dominate the overall content catalog.
- Certain genres show stronger growth in recent years.
- Content production is concentrated in a few major countries.
- A large portion of the catalog consists of relatively older content.

These insights can inform **content acquisition strategy and regional investment decisions**.

---

# Repository Structure
