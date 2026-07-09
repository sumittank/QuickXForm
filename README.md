# QuickXForm

Live on **https://quickxformapp.onrender.com/**
Wait 45-60 seconds to load the app (in case of the live link i provided or depoly manually over the local system)

QuickXForm is a full-stack AI-powered application.

The project consists of:

- **Frontend:** React + Vite
- **Backend:** FastAPI + LangGraph
- **Database:** MongoDB
- **AI Integration:** LangGraph with Groq/OpenAI models

---

# LangGraph Tools

LangGraph Tools provides an AI-powered workflow system that enables users to interact with applications through chat, voice, automated AI suggestions, and intelligent data management. The system simplifies data creation, modification, workflow automation, and storage using LangGraph-based AI agents.

---

# Features

## 1. Add Directly Through Chat

Users can add information directly through the chat interface.

The LangGraph workflow processes the user's chat input, understands the intent, and automatically updates the required fields, sections, or components.

### Capabilities:
- Natural language data input.
- Automatic field extraction.
- Intelligent workflow execution.
- Real-time updates through chat interaction.

---

## 2. Modify Forms Through Chat

Users can modify existing forms by providing instructions through the chat interface.

The AI understands the requested modifications and dynamically updates the form without requiring manual changes.

### Capabilities:
- Update existing fields.
- Apply changes using natural language commands.

Example:

```
User:
"Add a HCP name to Dr. Ram"

AI:
Automatically updates the form structure and adds the required field.
```

---

## 3. Add Through Voice (Mic)

Users can add new information using voice input.

The microphone-based interaction converts speech into structured data and sends it through the LangGraph workflow.

### Capabilities:
- Speech-to-text conversion.
- Voice-based data entry.
- Automatic information extraction.
- Hands-free workflow execution.

Example:

```
User:
"Create a HCP profile with name SHYM and time will 7 PM "

AI:
Extracts the information and creates the required data structure.
```

---

## 4. Modify Through Voice (Mic)

Users can modify existing forms and data using voice commands.

The AI interprets voice instructions and applies the required changes automatically.

### Capabilities:
- Voice-based editing.
- Intelligent command understanding.
- Dynamic form updates.
- Faster workflow modifications.

Example:

```
User:
"Change the time to 8 PM"

AI:
Updates the existing time field.
```

---

# 5. AI-Based Suggestions and Automated Sections

LangGraph provides intelligent AI-driven suggestions based on user input, workflow context, and previous interactions.

The AI automatically identifies missing information and creates required sections step by step.

### AI Suggestion Capabilities:

- AI Suggested Follow-Ups

### Example:

```
Generate this on save the form by save button.

AI Suggestion:
- Reach out on 2026-07-12 with a concise follow-up summary.
- Send a follow-up summary and confirm next steps.
- Schedule the next touchpoint and confirm availability.
```

The AI continuously analyzes the workflow and suggests improvements to make the process more efficient.

---

# 6. Logs and Activity Tracking

The system maintains detailed logs of all user interactions, AI suggestions, modifications, and workflow executions.

Users can monitor the complete activity history and understand how the AI processed each request.

### Logging Includes:

- User actions.
- Chat interactions.
- Voice commands.
- AI-generated suggestions.
- Form modifications.
- Workflow execution history.
- Database operations.

### Benefits:

- Better transparency.
- Easy debugging.
- Complete workflow visibility.
- Tracking AI decisions.

---

# 7. Save Data to Database Cluster or Local Cluster

After completing the workflow, LangGraph stores the final generated data based on the selected storage configuration.

The system supports both cloud-based database clusters and local database clusters.

### Storage Capabilities:

- Secure data persistence.
- Fast data retrieval.
- Local deployment support.
- Cloud database support.
- Flexible storage configuration.



---

# Workflow Overview

```
User Input
    |
    |
Chat / Voice Interaction
    |
    |
LangGraph AI Agent
    |
    |
AI Suggestions & Workflow Automation
    |
    |
Form Creation / Modification
    |
    |
Logs & Activity Tracking
    |
    |
Database Storage
```

---

# Key Benefits

- AI-powered form generation.
- Chat and voice-based interaction.
- Automated workflow creation.
- Intelligent suggestions.
- Dynamic form modification.
- Complete activity tracking.
- Flexible database storage.
- Reduced manual effort.

---

# Future Enhancements

- Multi-agent LangGraph workflows.
- Advanced AI reasoning.
- More voice interaction capabilities.
- Custom AI agents per workflow.
- Real-time collaboration.

# Project Structure

After cloning the repository, the project structure will look like:

```

NEWFolder/
│
├── frontend/        # React + Vite application
│
└── backend/         # FastAPI + LangGraph API

````

---

# Run Locally

## 1. Clone the Repository

Open any empty/new folder.

Open that folder in VS Code.

Open the terminal and run:

```bash
git clone https://github.com/sumittank/QuickXForm
````

Make sure you are using the **main branch**.

Navigate into the project:

```-
```

You will see two main folders:

```
frontend
backend
```

---

# Backend Setup (FastAPI + LangGraph)

## 1. Navigate to Backend

```bash
cd backend
```

---

## 2. Create Virtual Environment

For Linux:

```bash
python3 -m venv venv
```

---

## 3. Activate Virtual Environment

Linux:

```bash
source venv/bin/activate
```

Windows:

```bash
venv\Scripts\activate
```

---

## 4. Install Dependencies

Run:

```bash
pip install -r requirements.txt
```

---

## 5. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Open `.env` and add the required values:

```env
MONGO_URI=mongodb+srv://XXXXX

GROQ_API_KEY=XXXXXX

GROQ_MODEL=llama-3.3-70b-versatile
```

---

## 6. Start Backend Server

Run:

```bash
uvicorn main:app --reload --port 10999
```

Backend will start at:

```
http://localhost:10999
```

---

# Frontend Setup (React + Vite)

## 1. Navigate to Frontend

Open another terminal:

```bash
cd frontend
```

---

## 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Update `.env`:

```env
VITE_API_BASE_URL=http://localhost:10999
```

---

## 3. Install Dependencies

Run:

```bash
npm install
```

---

## 4. Start Frontend

Run:

```bash
npm run dev
```

The frontend will start on:

```
http://localhost:5173/
```

Open this URL in your browser.

---

# MongoDB Configuration

QuickXForm requires MongoDB for storing application data.

## Option 1: MongoDB Atlas (Cloud Database)

If you are using MongoDB Atlas:

### 1. Create Database

Create a database with:

```
DB_NAME = aivoa_db
```

Create a collection:

```
COLLECTION_NAME = users_test
```

These names must exist inside your MongoDB cluster.

---

### 2. Allow Network Access

In MongoDB Atlas:

```
Security
    |
    └── Network Access
            |
            └── IP Access List
                    |
                    └── Add IP Address
```

Add:

```
0.0.0.0/0
```

Comment:

```
QuickXForm
```

This allows the application to connect from external servers like Render.

---

### 3. MongoDB URI

Add the connection string in `.env`:

```env
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
```

Example:

```env
MONGO_URI=mongodb+srv://user:password@cluster0.mongodb.net/?appName=Cluster0
```

---

# Option 2: Local MongoDB

If you want to use MongoDB locally:

## Install MongoDB

Install MongoDB Community Edition:

[https://www.mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)

Start MongoDB service.

Default local MongoDB URL:

```text
mongodb://localhost:27017
```

Add this in your `.env`:

```env
MONGO_URI=mongodb://localhost:27017
```

---

## Create Database and Collection

MongoDB will create the database automatically when data is inserted.

The application expects:

```
Database:
aivoa_db

Collection:
users_test
```

You can create them manually using MongoDB Compass or Mongo Shell.

Example using Mongo Shell:

```javascript
use aivoa_db

db.createCollection("users_test")
```

---

# Verify Installation

After starting both services:

Backend:

```
http://localhost:10999
```

Frontend:

```
http://localhost:5173/
```

The frontend should communicate with the FastAPI backend.

---

# Deployment

## Backend Deployment

Backend can be deployed on platforms like:

* Render
* AWS
* DigitalOcean
* Any Python hosting provider

Required start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```env
MONGO_URI=
GROQ_API_KEY=
GROQ_MODEL=
```

---

## Frontend Deployment

Frontend is a React + Vite application.

Build command:

```bash
npm install && npm run build
```

Build output:

```
dist/
```

The frontend can be deployed as a static site.

Required environment variable:

```env
VITE_API_BASE_URL=https://your-backend-url.com
```

---

# Technology Stack

## Frontend

* React
* Vite
* JavaScript
* Modern UI components

## Backend

* FastAPI
* LangGraph
* Python
* MongoDB

## AI

* Groq Models
* LangGraph workflow orchestration

---

# Troubleshooting

## MongoDB Connection Failed

Check:

* MongoDB URI is correct
* Database user has correct permissions
* Network Access allows your IP
* Database and collection names match

## Frontend Cannot Connect to Backend

Check:

Frontend `.env`

```env
VITE_API_BASE_URL=http://localhost:10999
```

Backend CORS configuration should allow frontend URL:

```
http://localhost:5173
```

---

# License

This project is for internal development and experimentation.

```

You can save this as:

```

README.md

```

in the root folder:

```

QuickXForm/
├── README.md
├── frontend/
└── backend/

```
```
