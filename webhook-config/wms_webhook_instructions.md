# Oracle WMS Webhook Manual Configuration Instructions

## Overview

Configure webhooks in Oracle WMS to send real-time notifications when data changes.

## Target Webhook URL

<https://your-api.example.com/wms-webhook>

## Entities to Configure

- facility
- item
- inventory
- location
- order_hdr
- order_dtl
- receipt
- receipt_dtl
- shipment
- allocation
- putaway
- pick
- cycle_count
- adjustment
- move
- wave

## Configuration Steps

### 1. Access WMS Admin Console

- Login to Oracle WMS Cloud Console
- Navigate to: Setup > Integration > Webhooks

### 2. Create Webhook Endpoint

- URL: <https://your-api.example.com/wms-webhook>
- Method: POST
- Format: JSON
- Authentication: Bearer Token

### 3. Configure Each Entity

For each entity (facility, item, inventory, location, order_hdr, order_dtl, receipt, receipt_dtl, shipment, allocation, putaway, pick, cycle_count, adjustment, move, wave):

```json
{
  "entity": "{entity_name}",
  "events": ["CREATE", "UPDATE", "DELETE"],
  "url": "https://your-api.example.com/wms-webhook",
  "active": true,
  "format": "json",
  "headers": {
    "Content-Type": "application/json",
    "X-WMS-Entity": "{entity_name}",
    "Authorization": "Bearer {webhook_token}"
  },
  "filters": {
    "company_code": "RAIZEN",
    "facility_code": "*"
  },
  "retry_config": {
    "max_retries": 3,
    "retry_delay": 5
  }
}
```

### 4. Test Configuration

- Use WMS test tools to trigger events
- Verify webhook receives notifications
- Check logs for any errors

### 5. Monitor and Maintain

- Set up monitoring for webhook endpoint
- Configure alerting for failed deliveries
- Regular health checks

## Security Considerations

- Use HTTPS for webhook URL
- Implement proper authentication
- Validate webhook signatures
- Rate limiting and DOS protection

## Troubleshooting

- Check WMS logs for webhook errors
- Verify network connectivity
- Test with webhook.site for debugging
- Monitor endpoint response times
