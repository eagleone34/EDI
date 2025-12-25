# API Documentation

## Overview

The EDI.email API allows you to programmatically convert EDI files to PDF, Excel, and HTML formats.

## Base URL

```
https://api.edi.email/v1
```

## Authentication

All API requests require a Bearer token in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

## Endpoints

### Convert EDI File

**POST** `/convert`

Convert an EDI file to the specified formats.

#### Request

```bash
curl -X POST https://api.edi.email/v1/convert \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@purchase-order.edi" \
  -F "formats=pdf,excel"
```

#### Response

```json
{
  "id": "conv_1234567890",
  "status": "completed",
  "transaction_type": "850",
  "transaction_name": "Purchase Order",
  "processing_time_ms": 8234,
  "downloads": {
    "pdf": "https://edi.email/download/conv_1234567890.pdf",
    "excel": "https://edi.email/download/conv_1234567890.xlsx"
  },
  "created_at": "2024-12-25T10:30:00Z"
}
```

### Get Conversion Status

**GET** `/conversions/{id}`

Get the status of a conversion.

### Download Converted File

**GET** `/conversions/{id}/download/{format}`

Download a converted file. Format can be: `pdf`, `excel`, or `html`.

### Routing Rules

**GET** `/routing-rules` - List all routing rules
**POST** `/routing-rules` - Create a new routing rule
**PUT** `/routing-rules/{id}` - Update a routing rule
**DELETE** `/routing-rules/{id}` - Delete a routing rule

## Supported Transaction Types

| Code | Name |
|------|------|
| 850 | Purchase Order |
| 810 | Invoice |
| 856 | Advance Ship Notice (ASN) |
| 855 | Purchase Order Acknowledgment |
| 997 | Functional Acknowledgment |

## Rate Limits

- Free tier: 10 requests/month
- Pro tier: Unlimited
- API rate limit: 60 requests/minute

## Error Codes

| Code | Description |
|------|-------------|
| 400 | Bad Request - Invalid file or parameters |
| 401 | Unauthorized - Invalid or missing API key |
| 413 | File too large (max 10MB) |
| 422 | Unprocessable - Invalid EDI format |
| 429 | Too many requests |
| 500 | Server error |
