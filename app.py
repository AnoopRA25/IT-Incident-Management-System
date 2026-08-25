import streamlit as st
import pandas as pd
import plotly.express as px
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
    page_title="IT Incident Command Center",
    page_icon="🚨",
    layout="wide"
)


# -------------------------------------------------
# CUSTOM CSS
# -------------------------------------------------

st.markdown("""
<style>

.main {
    background-color: #f6f8fc;
}

.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 0;
}

.subtitle {
    color: #6b7280;
    font-size: 18px;
    margin-bottom: 25px;
}

.metric-card {
    padding: 20px;
    border-radius: 12px;
    background: white;
    border: 1px solid #e5e7eb;
}

.alert-box {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    background-color: #fff4f4;
    border-left: 5px solid #dc2626;
}

</style>
""", unsafe_allow_html=True)


# -------------------------------------------------
# DATABASE INITIALIZATION
# -------------------------------------------------

create_table()


# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------

st.sidebar.title("🚨 IT Command Center")

st.sidebar.caption(
    "Real-Time Incident Monitoring System"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "📊 Dashboard",
        "➕ Create Incident",
        "📋 Incident Explorer",
        "🔧 Update Incident"
    ]
)

st.sidebar.divider()

st.sidebar.success("● System Online")


# -------------------------------------------------
# HELPER FUNCTION
# -------------------------------------------------

def add_sla_status(df):

    if df.empty:
        return df

    df = df.copy()

    df["sla_status"] = df.apply(
        lambda row: get_sla_status(
            row["sla_deadline"],
            row["status"]
        ),
        axis=1
    )

    return df


# =================================================
# DASHBOARD
# =================================================

if page == "📊 Dashboard":

    incidents = get_all_incidents()

    st.markdown(
        '<p class="main-title">🚨 IT Incident Command Center</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<p class="subtitle">Real-time monitoring and incident operations dashboard</p>',
        unsafe_allow_html=True
    )

    if not incidents:

        st.info(
            "No incidents available yet. Create your first incident."
        )

    else:

        df = pd.DataFrame(incidents)

        df = add_sla_status(df)

        # ------------------------------
        # METRICS
        # ------------------------------

        total = len(df)

        open_count = len(
            df[df["status"] == "Open"]
        )

        progress_count = len(
            df[df["status"] == "In Progress"]
        )

        critical_count = len(
            df[
                (df["priority"] == "Critical")
                &
                (df["status"] != "Resolved")
            ]
        )

        breached_count = len(
            df[
                df["sla_status"] == "Breached"
            ]
        )

        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric(
            "📋 Total Incidents",
            total
        )

        col2.metric(
            "🔴 Open",
            open_count
        )

        col3.metric(
            "🟠 In Progress",
            progress_count
        )

        col4.metric(
            "🚨 Critical",
            critical_count
        )

        col5.metric(
            "⚠️ SLA Breached",
            breached_count
        )

        st.divider()

        # ------------------------------
        # ALERTS
        # ------------------------------

        st.subheader("🚨 Active Alerts")

        critical_incidents = df[
            (df["priority"] == "Critical")
            &
            (df["status"] != "Resolved")
        ]

        breached_incidents = df[
            df["sla_status"] == "Breached"
        ]

        if (
            critical_incidents.empty
            and breached_incidents.empty
        ):

            st.success(
                "✅ No critical or breached incidents detected."
            )

        else:

            for _, incident in critical_incidents.iterrows():

                st.error(
                    f"🚨 CRITICAL INCIDENT: "
                    f"{incident['incident_id']} | "
                    f"{incident['title']}"
                )

            for _, incident in breached_incidents.iterrows():

                if incident["status"] != "Resolved":

                    st.warning(
                        f"⚠️ SLA BREACHED: "
                        f"{incident['incident_id']} | "
                        f"{incident['title']}"
                    )

        st.divider()

        # ------------------------------
        # INTERACTIVE ANALYTICS
        # ------------------------------

        st.subheader("📊 Incident Analytics")

        chart1, chart2 = st.columns(2)

        with chart1:

            priority_data = (
                df["priority"]
                .value_counts()
                .reset_index()
            )

            priority_data.columns = [
                "Priority",
                "Count"
            ]

            fig_priority = px.pie(
                priority_data,
                names="Priority",
                values="Count",
                title="Incidents by Priority",
                hole=0.45
            )

            st.plotly_chart(
                fig_priority,
                use_container_width=True
            )

        with chart2:

            status_data = (
                df["status"]
                .value_counts()
                .reset_index()
            )

            status_data.columns = [
                "Status",
                "Count"
            ]

            fig_status = px.bar(
                status_data,
                x="Status",
                y="Count",
                title="Incidents by Status",
                text="Count"
            )

            st.plotly_chart(
                fig_status,
                use_container_width=True
            )

        # ------------------------------
        # CATEGORY ANALYTICS
        # ------------------------------

        category_data = (
            df["category"]
            .value_counts()
            .reset_index()
        )

        category_data.columns = [
            "Category",
            "Count"
        ]

        fig_category = px.bar(
            category_data,
            x="Category",
            y="Count",
            title="Incidents by Category",
            text="Count"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

        st.divider()

        # ------------------------------
        # RECENT INCIDENTS
        # ------------------------------

        st.subheader("📋 Recent Incidents")

        display_columns = [
            "incident_id",
            "title",
            "priority",
            "status",
            "assigned_team",
            "sla_status"
        ]

        st.dataframe(
            df[display_columns].head(10),
            use_container_width=True,
            hide_index=True
        )


# =================================================
# CREATE INCIDENT
# =================================================

elif page == "➕ Create Incident":

    st.title("➕ Create New Incident")

    st.caption(
        "Create and automatically prioritize a new IT incident."
    )

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
            "🚀 Create Incident",
            use_container_width=True
        )

    if submitted:

        if not title.strip():

            st.error(
                "Please enter an incident title."
            )

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
                f"🎉 Incident {incident_id} created successfully!"
            )

            col1, col2 = st.columns(2)

            col1.metric(
                "Calculated Priority",
                priority
            )

            col2.metric(
                "SLA Deadline",
                sla_deadline.strftime(
                    "%d-%m-%Y %I:%M %p"
                )
            )


# =================================================
# INCIDENT EXPLORER
# =================================================

elif page == "📋 Incident Explorer":

    st.title("📋 Incident Explorer")

    incidents = get_all_incidents()

    if not incidents:

        st.info(
            "No incidents available."
        )

    else:

        df = pd.DataFrame(incidents)

        df = add_sla_status(df)

        st.subheader("🔍 Search and Filters")

        search = st.text_input(
            "Search by Incident ID or Title"
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            status_filter = st.selectbox(
                "Status",
                [
                    "All",
                    "Open",
                    "In Progress",
                    "Resolved"
                ]
            )

        with col2:

            priority_filter = st.selectbox(
                "Priority",
                [
                    "All",
                    "Critical",
                    "High",
                    "Medium",
                    "Low"
                ]
            )

        with col3:

            categories = [
                "All"
            ] + sorted(
                df["category"].dropna().unique().tolist()
            )

            category_filter = st.selectbox(
                "Category",
                categories
            )

        filtered_df = df.copy()

        # Search
        if search:

            search_lower = search.lower()

            filtered_df = filtered_df[
                filtered_df["incident_id"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
                |
                filtered_df["title"]
                .str.lower()
                .str.contains(
                    search_lower,
                    na=False
                )
            ]

        # Status filter
        if status_filter != "All":

            filtered_df = filtered_df[
                filtered_df["status"]
                == status_filter
            ]

        # Priority filter
        if priority_filter != "All":

            filtered_df = filtered_df[
                filtered_df["priority"]
                == priority_filter
            ]

        # Category filter
        if category_filter != "All":

            filtered_df = filtered_df[
                filtered_df["category"]
                == category_filter
            ]

        st.caption(
            f"{len(filtered_df)} incident(s) found"
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
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # ------------------------------
        # INCIDENT DETAILS
        # ------------------------------

        if not filtered_df.empty:

            st.subheader("🔎 Incident Details")

            selected_id = st.selectbox(
                "Select an incident to inspect",
                filtered_df["incident_id"].tolist()
            )

            incident = get_incident_by_id(
                selected_id
            )

            if incident:

                detail_col1, detail_col2 = st.columns(2)

                with detail_col1:

                    st.write(
                        f"**Incident ID:** "
                        f"{incident['incident_id']}"
                    )

                    st.write(
                        f"**Priority:** "
                        f"{incident['priority']}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{incident['status']}"
                    )

                    st.write(
                        f"**Category:** "
                        f"{incident['category']}"
                    )

                with detail_col2:

                    st.write(
                        f"**Assigned Team:** "
                        f"{incident['assigned_team']}"
                    )

                    st.write(
                        f"**Created At:** "
                        f"{incident['created_at']}"
                    )

                    st.write(
                        f"**SLA Deadline:** "
                        f"{incident['sla_deadline']}"
                    )

                st.info(
                    f"**Description:** "
                    f"{incident['description']}"
                )

                if incident["root_cause"]:

                    st.warning(
                        f"**Root Cause:** "
                        f"{incident['root_cause']}"
                    )

                if incident["resolution"]:

                    st.success(
                        f"**Resolution:** "
                        f"{incident['resolution']}"
                    )


# =================================================
# UPDATE INCIDENT
# =================================================

elif page == "🔧 Update Incident":

    st.title("🔧 Update / Resolve Incident")

    incidents = get_all_incidents()

    if not incidents:

        st.info(
            "No incidents available to update."
        )

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
            f"{incident['incident_id']} — "
            f"{incident['title']}"
        )

        info_col1, info_col2, info_col3 = st.columns(3)

        info_col1.metric(
            "Priority",
            incident["priority"]
        )

        info_col2.metric(
            "Current Status",
            incident["status"]
        )

        info_col3.metric(
            "Assigned Team",
            incident["assigned_team"]
        )

        with st.form("update_incident_form"):

            status_options = [
                "Open",
                "In Progress",
                "Resolved"
            ]

            status = st.selectbox(
                "Update Status",
                status_options,
                index=status_options.index(
                    incident["status"]
                )
            )

            root_cause = st.text_area(
                "Root Cause Analysis",
                value=incident["root_cause"] or ""
            )

            resolution = st.text_area(
                "Resolution Details",
                value=incident["resolution"] or ""
            )

            submitted = st.form_submit_button(
                "💾 Save Incident Update",
                use_container_width=True
            )

        if submitted:

            update_incident(
                selected_id,
                status,
                root_cause,
                resolution
            )

            st.success(
                f"✅ Incident {selected_id} "
                f"updated successfully!"
            )

            st.rerun()