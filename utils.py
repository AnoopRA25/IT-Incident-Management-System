from datetime import datetime, timedelta


def calculate_priority(impact, urgency):

    priority_matrix = {
        ("High", "High"): "Critical",
        ("High", "Medium"): "High",
        ("High", "Low"): "Medium",

        ("Medium", "High"): "High",
        ("Medium", "Medium"): "Medium",
        ("Medium", "Low"): "Low",

        ("Low", "High"): "Medium",
        ("Low", "Medium"): "Low",
        ("Low", "Low"): "Low",
    }

    return priority_matrix.get((impact, urgency), "Low")


def get_sla_hours(priority):

    sla_hours = {
        "Critical": 1,
        "High": 4,
        "Medium": 8,
        "Low": 24
    }

    return sla_hours.get(priority, 24)


def calculate_sla_deadline(priority):

    hours = get_sla_hours(priority)

    return datetime.now() + timedelta(hours=hours)


def get_sla_status(deadline, status):

    if status == "Resolved":
        return "Resolved"

    if isinstance(deadline, str):
        deadline = datetime.fromisoformat(deadline)

    if datetime.now() > deadline:
        return "Breached"

    return "Within SLA"