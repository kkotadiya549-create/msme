def run(listening_data: dict, sensor_data: dict) -> dict:
    issue_type = listening_data.get("issueType")
    urgency_guess = listening_data.get("urgencyGuess")
    correlation_status = sensor_data.get("correlationStatus")
    
    action_type = "log_only"
    priority = urgency_guess or "low"
    reasoning = "No specific action required based on simple rules."
    
    if issue_type in ['temperature', 'noise']:
        if correlation_status == 'abnormal':
            action_type = "maintenance_ticket"
            reasoning = "Sensor data confirms abnormal reading for physical issue."
        else:
            reasoning = "Physical issue reported, but sensor data does not confirm abnormality."
    elif issue_type in ['stock', 'delay']:
        action_type = "inventory_alert"
        reasoning = "Operational issue reported, logging as inventory alert."
        
    return {
        "actionType": action_type,
        "priority": priority,
        "reasoning": reasoning
    }
