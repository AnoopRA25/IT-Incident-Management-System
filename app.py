import streamlit as st
import pandas as pd
from datetime import datetime

from database import (
    create_table,
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    update_incident
)

from utils import (
    calculate_priority,
    calculate_sla_deadline,
    get_sla_status
)


# -------------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------------

st.set_page_config(
    page_title="IT Incident Management System",
    page_icon="🛠️",
    layout="wide"
)


# Create database table when application starts
create_table()


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("🛠️ IT Service Management")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "Create Incident",
        "View Incidents",
        "Update Incident"
    ]
)


# -------------------------------------------------
# DASHBOARD
# -------------------------------------------------

if page == "Dashboard":

    st.title("📊 Incident Management Dashboard")

    incidents = get_all_incidents()

    if not incidents:
        st.info("No incidents available. Create your first incident.")

    else:
        df = pd.DataFrame(incidents)

        total = len(df)
        open_count = len(df[df["status"] == "Open"])
        progress_count = len(df[df["status"] == "In Progress"])
        resolved_count = len(df[df["status"] == "Resolved"])
        critical_count = len(df[df["priority"] == "Critical"])

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total", total)
        col2.metric("Open", open_count)
        col3.metric("In Progress", progress_count)
        col4.metric("Resolved", resolved_count)
        col5.metric("Critical", critical_count)

        st.divider()

        st.subheader("Recent Incidents")

        display_columns = [
            "incident_id",
            "title",
            "priority",
            "status",
            "assigned_team"
        ]

        st.dataframe(
            df[display_columns],
            use_container_width=True
        )


# -------------------------------------------------
# CREATE INCIDENT
# -------------------------------------------------

elif page == "Create Incident":

    st.title("➕ Create New Incident")

    with st.form("create_incident_form"):

        title = st.text_input(
            "Incident Title"
        )

        description = st.text_area(
            "Incident Description"
        )

        category = st.selectbox(
            "Category",
            [
                "Application",
                "Database",
                "Network",
                "Hardware",
                "Software",
                "Security",
                "Other"
            ]
        )

        col1, col2 = st.columns(2)

        with col1:
            impact = st.selectbox(
                "Impact",
                ["Low", "Medium", "High"]
            )

        with col2:
            urgency = st.selectbox(
                "Urgency",
                ["Low", "Medium", "High"]
            )

        assigned_team = st.selectbox(
            "Assigned Team",
            [
                "Application Support",
                "Database Support",
                "Network Support",
                "IT Operations",
                "Security Team"
            ]
        )

        submitted = st.form_submit_button(
            "Create Incident"
        )

    if submitted:

        if not title.strip():

            st.error("Please enter an incident title.")

        else:

            priority = calculate_priority(
                impact,
                urgency
            )

            sla_deadline = calculate_sla_deadline(
                priority
            )

            incident_id = create_incident(
                title,
                description,
                category,
                impact,
                urgency,
                priority,
                assigned_team,
                sla_deadline
            )

            st.success(
                f"Incident {incident_id} created successfully!"
            )

            st.info(
                f"Priority: {priority} | "
                f"SLA Deadline: "
                f"{sla_deadline.strftime('%d-%m-%Y %I:%M %p')}"
            )


# -------------------------------------------------
# VIEW INCIDENTS
# -------------------------------------------------

elif page == "View Incidents":

    st.title("📋 View Incidents")

    incidents = get_all_incidents()

    if not incidents:

        st.info("No incidents available.")

    else:

        df = pd.DataFrame(incidents)

        st.subheader("Filters")

        col1, col2 = st.columns(2)

        with col1:

            status_filter = st.selectbox(
                "Filter by Status",
                ["All", "Open", "In Progress", "Resolved"]
            )

        with col2:

            priority_filter = st.selectbox(
                "Filter by Priority",
                ["All", "Critical", "High", "Medium", "Low"]
            )

        filtered_df = df.copy()

        if status_filter != "All":

            filtered_df = filtered_df[
                filtered_df["status"] == status_filter
            ]

        if priority_filter != "All":

            filtered_df = filtered_df[
                filtered_df["priority"] == priority_filter
            ]

        filtered_df["sla_status"] = filtered_df.apply(
            lambda row: get_sla_status(
                row["sla_deadline"],
                row["status"]
            ),
            axis=1
        )

        display_columns = [
            "incident_id",
            "title",
            "category",
            "priority",
            "status",
            "assigned_team",
            "sla_status"
        ]

        st.dataframe(
            filtered_df[display_columns],
            use_container_width=True
        )


# -------------------------------------------------
# UPDATE INCIDENT
# -------------------------------------------------

elif page == "Update Incident":

    st.title("🔧 Update / Resolve Incident")

    incidents = get_all_incidents()

    if not incidents:

        st.info("No incidents available to update.")

    else:

        incident_ids = [
            incident["incident_id"]
            for incident in incidents
        ]

        selected_id = st.selectbox(
            "Select Incident",
            incident_ids
        )

        incident = get_incident_by_id(
            selected_id
        )

        st.subheader(
            f"{incident['incident_id']} - {incident['title']}"
        )

        st.write(
            f"**Current Status:** {incident['status']}"
        )

        with st.form("update_incident_form"):

            status = st.selectbox(
                "Update Status",
                [
                    "Open",
                    "In Progress",
                    "Resolved"
                ],
                index=[
                    "Open",
                    "In Progress",
                    "Resolved"
                ].index(incident["status"])
            )

            root_cause = st.text_area(
                "Root Cause",
                value=incident["root_cause"] or ""
            )

            resolution = st.text_area(
                "Resolution",
                value=incident["resolution"] or ""
            )

            submitted = st.form_submit_button(
                "Save Update"
            )

        if submitted:

            update_incident(
                selected_id,
                status,
                root_cause,
                resolution
            )

            st.success(
                f"Incident {selected_id} updated successfully!"
            )