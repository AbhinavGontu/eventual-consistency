# Eventual Consistency SAGA Framework

> A distributed transaction orchestrator implementing the **SAGA Pattern** to ensure data consistency across microservices.

## Overview

In microservices/distributed systems, I learned the hard way that you cannot simply "join" tables across databases or rely on ACID transactions. I built this framework to solve the problem of data consistency.

## Tech Stack
- **Python 3.9+**
- **FastAPI**
- **SAGA Pattern**

## Architecture
I chose **Orchestration** over Choreography to avoid distributed spaghetti code.

## Usage
`pip install -r requirements.txt`
