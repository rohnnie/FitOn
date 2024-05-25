# FitOn: A Personalized Health and Fitness Companion

FitOn is a cutting-edge application designed to monitor and analyze real-time health data, including heart rate, sleep duration, daily steps, BMI, and more. The primary objective of FitOn is to provide personalized exercise recommendations based on the analysis of user metrics. Leveraging the KNearestNeighbour (KNN) machine learning model deployed on Amazon SageMaker, FitOn predicts the most suitable exercise regimen corresponding to the user’s recorded data.

## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [System Architecture](#system-architecture)
4. [Setup Instructions](#setup-instructions)
5. [Usage](#usage)
6. [Methodology](#methodology)
7. [Security Considerations](#security-considerations)
8. [Scalability](#scalability)
9. [Results](#results)

## Introduction
In an era where health and fitness are becoming increasingly prioritized, the demand for intuitive and comprehensive health monitoring solutions is on the rise. FitOn emerges as a pioneering application aimed at revolutionizing the way individuals track, analyze, and improve their overall well-being.

FitOn integrates cutting-edge technologies to deliver a holistic health monitoring and recommendation system. It leverages the Google Fit API to extract real-time data on various health metrics and uses Amazon RDS for in-depth analysis and processing. The KNN model on Amazon SageMaker provides actionable insights and personalized exercise recommendations.

## Features
- **Real-time Health Monitoring**: Tracks heart rate, sleep duration, daily steps, BMI, and more.
- **Personalized Exercise Recommendations**: Uses KNN machine learning model for tailored fitness regimens.
- **User-friendly Interface**: Intuitive dashboard for seamless input and tracking of health metrics.
- **Advanced Visualization**: Comprehensive insights with charts and graphs on health trends.
- **Secure User Authentication**: AWS Cognito ensures secure login and data privacy.
- **Cloud-based Storage**: Efficient data storage and management using AWS services.

## System Architecture
FitOn is built with a robust architecture as shown below:

![image](https://github.com/rohnnie/FitOn/assets/46161834/65d02c33-83f7-4e43-849e-8d8f5490ef4e)


## Setup Instructions
1. **Clone the Repository**
   ```bash
   git clone https://github.com/rohnnie/FitOn.git
   cd FitOn
2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
3. **Configure AWS Services**
  - Set up AWS Cognito for user authentication.
  - Create RDS, DynamoDB, S3, SQS, and SNS instances.
  - Deploy machine learning models on Amazon SageMaker.
4. **Run the Application**
    ```bash
    python manage.py runserver

## Usage

### Sign Up / Login
- Users can sign up or log in via email using AWS Cognito.

### Dashboard
- Track various health metrics in real-time.
- View graphical representations of health trends.

### Exercise Recommendations
- Access personalized workout recommendations based on recorded data.

### Data Management
- Manage user profiles, synchronize data with Google Fit, and upload profile pictures.

## Methodology

### User Authentication and Website Access
- Secure user authentication through AWS Cognito.
- Access the FitOn website hosted on AWS Beanstalk.

### Data Processing
- **Health Metrics Tracking**: Data synchronized from Google Fit API and stored in DynamoDB.
- **Exercise Recommendations**: KNN algorithm on SageMaker provides personalized exercise suggestions.
- **Sleep Score Prediction**: Predict sleep scores using KNN model.

### Data Retrieval and Scalability
- Requests handled via SQS and processed by AWS Lambda.
- Notifications sent using SNS when data retrieval is complete.

## Security Considerations

- **User Authentication**: Handled through AWS Cognito.
- **Data Encryption**: Encrypted data at rest and in transit.
- **Access Control**: AWS IAM roles and policies for resource access.

## Scalability

- **Cloud-based Services**: AWS enables horizontal scaling.
- **Serverless Functions**: AWS Lambda for cost-effective processing.
- **Data Retrieval Queue**: Amazon SQS for asynchronous processing.

## Results

FitOn successfully implements a secure and scalable architecture, delivering a comprehensive health and fitness tracking experience. Key features include:

- Secure user authentication and profile management.
- Real-time health data tracking.
- Machine learning-powered sleep score prediction and exercise recommendations.
- Customizable dashboards for a holistic view of health metrics.


