# Newsletter Subscription Handler

A serverless function built for Scaleway that manages newsletter subscriptions by storing registration data in a CSV
file using Object Storage.

## Overview

This serverless function provides an API endpoint to handle newsletter subscriptions. When users register, their email
addresses and registration timestamps are stored in a CSV file within Scaleway's Object Storage (S3-compatible).

## Features

- Handles POST requests with email parameters
- Stores registrations with French-formatted timestamps
- Maintains a CSV file with subscription records
- Automatically creates the CSV file if it doesn't exist
- Uses Scaleway's Object Storage for data persistence

## Prerequisites

- Scaleway Account
- Object Storage bucket
- Function credentials (Access and Secret keys)

## Environment Variables

The following environment variables must be set:

```
SCW_ACCESS_KEY=your_access_key
SCW_SECRET_KEY=your_secret_key
BUCKET_NAME=your_bucket_name
```

## Usage

### API Endpoint

Send a POST request to your function URL with an email parameter:

```bash
curl -X POST "https://your-function-url.functions.fnc.fr-par.scw.cloud?email=user@example.com"
```

### Successful Response

```json
{
  "message": "Successfully subscribed to newsletter"
}
```

## Data Storage

Subscriptions are stored in `newsletter_register.csv` with the following format:

```csv
datetime,email
Tue Nov 16 08:30:00 2024,user@example.com
```

## Error Handling

The API returns appropriate HTTP status codes:

| Status Code | Description             |
|-------------|-------------------------|
| 200         | Successful subscription |
| 400         | Missing email parameter |
| 405         | Invalid HTTP method     |
| 500         | Server error            |

## Development

To run locally:

```bash
python -m scaleway_functions_python.local
```

## Technical Details

- Runtime: Python
- Memory Limit: 512MB
- Region: Paris (fr-par)
- Storage: Scaleway Object Storage