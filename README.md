# HNG13 Backend Stage 0 - Dynamic Profile Endpoint

## Overview
This FastAPI app provides a "/me"endpoint that returns:
- Your name, email, and backend stack
- The current UTC timestamp
- A random cat fact from the Cat Facts API

##  **API Endpoint**

### **GET** `/me`

**Base URL:**
[https://written-rey-chiedozie-735aaaa7.koyeb.app/me](https://written-rey-chiedozie-735aaaa7.koyeb.app/me)

## Sample Response
```json
{
    "status": "success",
    "user": {
        "email": "leoclinton2011@hotmail.com",
        "name": "Nwokocha Chiedozie Clinton",
        "stack": "Python/FastAPI"
    },
    "timestamp": "2025-10-19Y19:07:03.875498+00:00",
    "fact": "In just seven years, a single pair of cats and their offspring could produce a staggering total of 420,000 kittens."
}