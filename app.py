"""
E-Commerce Analytics Dashboard
Built with Streamlit, dbt, and DuckDB
"""

import streamlit as st
import subprocess
import sys
from pathlib import Path
import duckdb
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

from download_and_load_data import download_and_load_data


# Page configuration
st.set_page_config(
    page_title="E-Commerce Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Project paths
PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "ecommerce.duckdb"
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt" / "ecommerce_analytics"
DBT_PROFILES_DIR = PROJECT_ROOT / "dbt"


def init_session_state():
    """Initialize session state variables."""
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'dbt_built' not in st.session_state:
        st.session_state.dbt_built = False
    if 'pipeline_status' not in st.session_state:
        # Check if database already exists (for pre-built deployments)
        if DB_PATH.exists():
            db_ready, _ = check_database_status()
            if db_ready:
                st.session_state.pipeline_status = "dbt_built"
            else:
                st.session_state.pipeline_status = "not_started"
        else:
            st.session_state.pipeline_status = "not_started"


def check_database_status():
    """
    Check if database exists and has analytics models built.

    Returns:
        Tuple of (is_ready: bool, status_message: str)
    """
    if not DB_PATH.exists():
        return False, "Database not found"

    try:
        con = duckdb.connect(str(DB_PATH), read_only=True)

        # Check if raw schema exists
        raw_exists = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'raw'"
        ).fetchone()[0] > 0

        # Check if marts schema exists (indicates dbt has been run)
        marts_exist = con.execute(
            "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'marts'"
        ).fetchone()[0] > 0

        con.close()

        if marts_exist:
            return True, "✅ Ready - Database & models built"
        elif raw_exists:
            return False, "⚠️ Data loaded - Run dbt build"
        else:
            return False, "⚠️ Database exists but empty"

    except Exception as e:
        return False, f"Database error: {e}"


def run_dbt_command(command, *args):
    """
    Run a dbt command.

    Args:
        command: dbt command (e.g., 'run', 'test', 'build')
        *args: Additional arguments

    Returns:
        Tuple of (success: bool, output: str)
    """
    cmd = [
        'dbt', command,
        '--profiles-dir', str(DBT_PROFILES_DIR),
        '--project-dir', str(DBT_PROJECT_DIR)
    ]
    cmd.extend(args)

    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out after 5 minutes"
    except Exception as e:
        return False, f"Error running dbt: {e}"


def get_kaggle_credentials():
    """
    Get Kaggle credentials from Streamlit secrets or environment.

    Returns:
        Tuple of (api_token, username, key)
        - New format: (token, None, None)
        - Legacy format: (None, username, key)
        - Not found: (None, None, None)
    """
    try:
        # Try new token format first
        if "api_token" in st.secrets.get("kaggle", {}):
            return st.secrets["kaggle"]["api_token"], None, None
        # Fall back to legacy format
        elif "username" in st.secrets.get("kaggle", {}) and "key" in st.secrets.get("kaggle", {}):
            return None, st.secrets["kaggle"]["username"], st.secrets["kaggle"]["key"]
    except:
        pass

    # Fall back to None (will use environment or ~/.kaggle/kaggle.json)
    return None, None, None


# Initialize session state
init_session_state()

# Sidebar
with st.sidebar:
    st.title("📊 E-Commerce Analytics")
    st.markdown("---")

    # Database & Pipeline status
    st.subheader("Status")
    db_ready, db_status = check_database_status()
    st.caption(db_status)

    if st.session_state.pipeline_status == "not_started":
        if not DB_PATH.exists():
            st.warning("⏳ Setup required")
        else:
            st.info("📊 Build dbt models")
    elif st.session_state.pipeline_status == "loading":
        st.info("⏳ Loading data...")
    elif st.session_state.pipeline_status == "data_loaded":
        st.info("📊 Build dbt models")
    elif st.session_state.pipeline_status == "dbt_built":
        st.success("✅ Dashboard ready")

    st.markdown("---")

    # Navigation
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📥 Data Pipeline", "📊 Dashboard", "🔍 Data Explorer", "ℹ️ About"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.caption("Built with Streamlit, dbt & DuckDB")


# Main content based on page selection
if page == "🏠 Home":
    st.title("Welcome to E-Commerce Analytics Dashboard")

    st.markdown("""
    This application analyzes Brazilian e-commerce data using modern data stack tools:
    - **Streamlit** for the interactive dashboard
    - **DuckDB** for the analytical database
    - **dbt** for data transformation
    - **Kaggle API** for data sourcing

    ### Quick Start

    1. **📥 Data Pipeline** - Download and load data from Kaggle
    2. **📊 Dashboard** - Explore analytics and insights
    """)

    # Show status-based instructions
    if st.session_state.pipeline_status == "not_started":
        st.info("👉 Go to **Data Pipeline** to get started!")
    elif st.session_state.pipeline_status in ["data_loaded", "dbt_built"]:
        st.markdown("### Database Overview")

        try:
            con = duckdb.connect(str(DB_PATH), read_only=True)

            # Get table list
            raw_tables = con.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'raw'
                ORDER BY table_name
            """).df()

            # Count schemas
            schemas = con.execute("""
                SELECT COUNT(DISTINCT schema_name) as schema_count
                FROM information_schema.schemata
                WHERE schema_name IN ('raw', 'staging', 'intermediate', 'marts')
            """).fetchone()[0]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Raw Tables", len(raw_tables))
            with col2:
                st.metric("dbt Schemas", schemas)
            with col3:
                db_size_mb = DB_PATH.stat().st_size / (1024 * 1024)
                st.metric("Database Size", f"{db_size_mb:.1f} MB")

            con.close()

        except Exception as e:
            st.error(f"Error querying database: {e}")


elif page == "📥 Data Pipeline":
    st.title("Data Pipeline")

    st.markdown("""
    This page manages the data pipeline from Kaggle to DuckDB.

    ### Pipeline Steps:
    1. Download dataset from Kaggle using API
    2. Load CSV files into DuckDB raw schema
    3. Run dbt transformations to build analytics models
    """)

    st.markdown("---")

    # Step 1: Download and Load Data
    st.subheader("Step 1: Download & Load Data")

    # Show different UI based on whether DB exists
    if DB_PATH.exists():
        st.success("✅ Database exists with data")

        # Optional: Refresh/Rebuild button
        with st.expander("🔄 Refresh Data (Optional)", expanded=False):
            st.warning("⚠️ This will delete the existing database and download fresh data from Kaggle. This is optional - only use if you want to demo the pipeline or get updated data.")

            if st.button("🔄 Refresh from Kaggle", use_container_width=True):
                st.session_state.pipeline_status = "loading"
                with st.spinner("Downloading fresh dataset from Kaggle..."):
                    try:
                        # Delete existing database
                        if DB_PATH.exists():
                            DB_PATH.unlink()

                        api_token, username, key = get_kaggle_credentials()

                        # Download and load
                        db_path = download_and_load_data(
                            kaggle_api_token=api_token,
                            kaggle_username=username,
                            kaggle_key=key,
                            project_root=PROJECT_ROOT
                        )

                        st.session_state.data_loaded = True
                        st.session_state.pipeline_status = "data_loaded"
                        st.success(f"✅ Data refreshed successfully!")
                        st.rerun()

                    except Exception as e:
                        st.session_state.pipeline_status = "not_started"
                        st.error(f"❌ Error: {e}")
                        st.info("💡 Make sure you have configured Kaggle credentials in `.streamlit/secrets.toml`")
    else:
        st.info("📥 No database found. Click below to download data from Kaggle.")

        if st.button("📥 Download from Kaggle & Load", type="primary", use_container_width=True):
            st.session_state.pipeline_status = "loading"
            with st.spinner("Downloading dataset from Kaggle..."):
                try:
                    api_token, username, key = get_kaggle_credentials()

                    # Create progress placeholder
                    progress_text = st.empty()
                    progress_text.text("Downloading data from Kaggle...")

                    # Download and load
                    db_path = download_and_load_data(
                        kaggle_api_token=api_token,
                        kaggle_username=username,
                        kaggle_key=key,
                        project_root=PROJECT_ROOT
                    )

                    st.session_state.data_loaded = True
                    st.session_state.pipeline_status = "data_loaded"
                    st.success(f"✅ Data downloaded and loaded successfully!")
                    st.rerun()

                except Exception as e:
                    st.session_state.pipeline_status = "not_started"
                    st.error(f"❌ Error: {e}")
                    st.info("💡 Make sure you have configured Kaggle credentials in `.streamlit/secrets.toml`")

    st.markdown("---")

    # Step 2: Build dbt Models
    st.subheader("Step 2: Build dbt Models")

    # Check if we have raw data to work with
    db_exists = DB_PATH.exists()
    db_ready, _ = check_database_status()

    if not db_exists:
        st.warning("⚠️ Load data first before building dbt models")
    else:
        if db_ready:
            st.success("✅ dbt models already built")

        col1, col2 = st.columns(2)

        with col1:
            button_label = "🔨 Rebuild Models" if db_ready else "🔨 Build All Models"
            if st.button(button_label, use_container_width=True):
                with st.spinner("Running dbt build..."):
                    success, output = run_dbt_command('build')

                    with st.expander("dbt Output", expanded=True):
                        st.code(output, language='bash')

                    if success:
                        st.success("✅ dbt build completed successfully!")
                        st.session_state.dbt_built = True
                        st.session_state.pipeline_status = "dbt_built"
                        # Don't rerun - let user see the output
                    else:
                        st.error("❌ dbt build failed. Check output above.")

        with col2:
            if st.button("🧪 Run Tests Only", use_container_width=True):
                with st.spinner("Running dbt tests..."):
                    with st.expander("Test Results", expanded=True):
                        output_placeholder = st.empty()
                        success, output = run_dbt_command('test')

                        output_placeholder.code(output, language='bash')

                        if success:
                            st.success("✅ All tests passed!")
                        else:
                            st.error("❌ Some tests failed. Check output above.")


elif page == "📊 Dashboard":
    st.title("Analytics Dashboard")

    if st.session_state.pipeline_status == "not_started":
        st.warning("⚠️ No data loaded. Please go to **Data Pipeline** to download data first.")
    elif st.session_state.pipeline_status == "data_loaded":
        st.warning("⚠️ Analytics models not built. Please run **dbt build** in the Data Pipeline page.")
    elif st.session_state.pipeline_status == "dbt_built":
        try:
            con = duckdb.connect(str(DB_PATH), read_only=True)

            # Dashboard tabs
            tab1, tab2, tab3 = st.tabs(["📈 Overview", "👥 Customers", "📦 Products"])

            with tab1:
                st.subheader("Business Overview")

                # Product Category Filter
                categories = con.execute("""
                    SELECT DISTINCT category_english
                    FROM marts.dim_products
                    WHERE category_english IS NOT NULL
                    ORDER BY category_english
                """).df()['category_english'].tolist()

                selected_categories = st.multiselect(
                    "🔍 Filter by Product Category",
                    options=['All Categories'] + categories,
                    default=['All Categories'],
                    help="Select one or more product categories to filter the data"
                )

                # Build filter condition
                if 'All Categories' in selected_categories or len(selected_categories) == 0:
                    category_filter = ""
                    category_filter_with_and = ""
                else:
                    categories_str = "', '".join(selected_categories)
                    category_filter = f"AND p.category_english IN ('{categories_str}')"
                    category_filter_with_and = f"AND p.category_english IN ('{categories_str}')"

                st.markdown("---")

                # Key metrics
                metrics = con.execute(f"""
                    SELECT
                        COUNT(DISTINCT o.order_key) as total_orders,
                        COUNT(DISTINCT o.customer_key) as total_customers,
                        SUM(o.order_value) as total_revenue,
                        AVG(o.order_value) as avg_order_value
                    FROM marts.fct_orders o
                    WHERE o.is_delivered = true
                    {'AND EXISTS (SELECT 1 FROM marts.fct_order_items oi JOIN marts.dim_products p ON oi.product_key = p.product_key WHERE oi.order_key = o.order_key ' + category_filter_with_and + ')' if category_filter else ''}
                """).fetchone()

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Orders", f"{metrics[0]:,}")
                with col2:
                    st.metric("Total Customers", f"{metrics[1]:,}")
                with col3:
                    st.metric("Total Revenue", f"R$ {metrics[2]:,.2f}")
                with col4:
                    st.metric("Avg Order Value", f"R$ {metrics[3]:,.2f}")

                # Orders over time
                st.subheader("Orders Over Time")
                orders_over_time = con.execute(f"""
                    SELECT
                        DATE_TRUNC('month', o.purchased_at) as month,
                        COUNT(DISTINCT o.order_key) as order_count,
                        SUM(o.order_value) as revenue
                    FROM marts.fct_orders o
                    WHERE o.is_delivered = true
                    {'AND EXISTS (SELECT 1 FROM marts.fct_order_items oi JOIN marts.dim_products p ON oi.product_key = p.product_key WHERE oi.order_key = o.order_key ' + category_filter_with_and + ')' if category_filter else ''}
                    GROUP BY month
                    ORDER BY month
                """).df()

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=orders_over_time['month'],
                    y=orders_over_time['order_count'],
                    name='Orders',
                    line=dict(color='#636EFA')
                ))

                filter_text = f" - {', '.join(selected_categories)}" if 'All Categories' not in selected_categories and len(selected_categories) > 0 else ""
                fig.update_layout(
                    title=f"Monthly Orders{filter_text}",
                    xaxis_title="Month",
                    yaxis_title="Number of Orders",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.subheader("Customer Analytics")

                # RFM Explanation
                with st.expander("ℹ️ About RFM Customer Segmentation", expanded=False):
                    st.markdown("""
                    **RFM Analysis** segments customers based on three key behavioral dimensions:

                    **R - Recency:** How recently did the customer make a purchase?
                    - Score 1-5 (5 = most recent)
                    - Recent customers are more likely to respond to promotions

                    **F - Frequency:** How often does the customer purchase?
                    - Score 1-5 (5 = most frequent)
                    - Frequent buyers show higher engagement and loyalty

                    **M - Monetary:** How much does the customer spend?
                    - Score 1-5 (5 = highest spending)
                    - High-value customers contribute most to revenue

                    **Customer Segments:**
                    - 🏆 **Champions:** Best customers (high R, F, M) - VIP treatment
                    - ❤️ **Loyal Customers:** Regular buyers - reward loyalty
                    - 🌟 **Potential Loyalists:** Recent buyers with potential - nurture
                    - 🆕 **Recent Customers:** New customers - encourage repeat
                    - 💎 **Promising:** Above average recency/frequency - engage more
                    - ⚠️ **Need Attention:** Declining engagement - re-engagement campaigns
                    - 🚨 **At Risk:** Previously good customers slipping away - win-back offers
                    - 🆘 **Cannot Lose Them:** High spenders who haven't returned - urgent action
                    - 😴 **Hibernating:** Long time since purchase - reactivation needed
                    - 💔 **Lost:** Lowest scores - likely churned

                    This segmentation enables **targeted marketing** strategies for each group.
                    """)

                # Customer segments
                segments = con.execute("""
                    SELECT
                        customer_segment,
                        COUNT(*) as customer_count
                    FROM marts.dim_customers
                    GROUP BY customer_segment
                    ORDER BY customer_count DESC
                """).df()

                fig = px.pie(
                    segments,
                    values='customer_count',
                    names='customer_segment',
                    title='Customer Segmentation (RFM Analysis)'
                )
                st.plotly_chart(fig, use_container_width=True)

                # Additional RFM metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    champions = segments[segments['customer_segment'] == 'Champions']['customer_count'].sum()
                    st.metric("🏆 Champions", f"{champions:,}")
                with col2:
                    loyal = segments[segments['customer_segment'] == 'Loyal Customers']['customer_count'].sum()
                    st.metric("❤️ Loyal Customers", f"{loyal:,}")
                with col3:
                    at_risk = segments[segments['customer_segment'] == 'At Risk']['customer_count'].sum()
                    st.metric("🚨 At Risk", f"{at_risk:,}")

            with tab3:
                st.subheader("Product Analytics")

                # Top products
                top_products = con.execute("""
                    SELECT
                        p.category_english,
                        COUNT(DISTINCT oi.order_key) as order_count,
                        SUM(oi.total_price) as revenue
                    FROM marts.fct_order_items oi
                    JOIN marts.dim_products p ON oi.product_key = p.product_key
                    GROUP BY p.category_english
                    ORDER BY revenue DESC
                    LIMIT 10
                """).df()

                fig = px.bar(
                    top_products,
                    x='category_english',
                    y='revenue',
                    title='Top 10 Product Categories by Revenue',
                    labels={'category_english': 'Category', 'revenue': 'Revenue (R$)'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

            con.close()

        except Exception as e:
            st.error(f"Error loading dashboard: {e}")


elif page == "🔍 Data Explorer":
    st.title("Data Explorer")

    if st.session_state.pipeline_status == "not_started":
        st.warning("⚠️ No data loaded. Please go to **Data Pipeline** to download data first.")
    else:
        try:
            con = duckdb.connect(str(DB_PATH), read_only=True)

            # Tabs for different exploration views
            explorer_tab1, explorer_tab2, explorer_tab3 = st.tabs(
                ["📊 Schema Browser", "🔗 Table Lineage", "📝 Table Definitions"]
            )

            with explorer_tab1:
                st.subheader("Database Schema Browser")

                # Get all schemas
                schemas = con.execute("""
                    SELECT DISTINCT schema_name
                    FROM information_schema.schemata
                    WHERE schema_name IN ('raw', 'staging', 'intermediate', 'marts')
                    ORDER BY
                        CASE schema_name
                            WHEN 'raw' THEN 1
                            WHEN 'staging' THEN 2
                            WHEN 'intermediate' THEN 3
                            WHEN 'marts' THEN 4
                        END
                """).df()['schema_name'].tolist()

                selected_schema = st.selectbox("Select Schema", schemas)

                # Get tables/views in selected schema
                objects = con.execute(f"""
                    SELECT
                        table_name,
                        table_type,
                        (SELECT COUNT(*) FROM information_schema.columns
                         WHERE table_schema = '{selected_schema}'
                         AND table_name = t.table_name) as column_count
                    FROM information_schema.tables t
                    WHERE table_schema = '{selected_schema}'
                    ORDER BY table_name
                """).df()

                st.markdown(f"### Tables in `{selected_schema}` schema")
                st.dataframe(
                    objects,
                    column_config={
                        "table_name": "Table Name",
                        "table_type": "Type",
                        "column_count": "Columns"
                    },
                    hide_index=True,
                    use_container_width=True
                )

                # Show columns for selected table
                if len(objects) > 0:
                    selected_table = st.selectbox("Select Table to View Columns", objects['table_name'].tolist())

                    columns = con.execute(f"""
                        SELECT
                            column_name,
                            data_type,
                            is_nullable
                        FROM information_schema.columns
                        WHERE table_schema = '{selected_schema}'
                        AND table_name = '{selected_table}'
                        ORDER BY ordinal_position
                    """).df()

                    st.markdown(f"#### Columns in `{selected_schema}.{selected_table}`")
                    st.dataframe(
                        columns,
                        column_config={
                            "column_name": "Column Name",
                            "data_type": "Data Type",
                            "is_nullable": "Nullable"
                        },
                        hide_index=True,
                        use_container_width=True
                    )

                    # Show sample data
                    with st.expander(f"📋 Sample Data (first 10 rows)"):
                        sample_data = con.execute(f"""
                            SELECT * FROM {selected_schema}.{selected_table}
                            LIMIT 10
                        """).df()
                        st.dataframe(sample_data, use_container_width=True)

            with explorer_tab2:
                st.subheader("Table Lineage Diagram")

                st.markdown("""
                This diagram shows how data flows through the dbt transformation layers:

                **Data Flow:**
                - **Raw Layer:** Source data from Kaggle (9 tables)
                - **Staging Layer:** Cleaned and standardized data (8 views)
                - **Intermediate Layer:** Business logic and calculations (4 views)
                - **Marts Layer:** Final dimensional model (5 tables)
                """)

                # Create lineage visualization using Graphviz
                import graphviz

                graph = graphviz.Digraph()
                graph.attr(rankdir='LR', splines='ortho', nodesep='0.5', ranksep='1.5')

                # Raw layer
                with graph.subgraph(name='cluster_raw') as raw:
                    raw.attr(label='Raw Schema', style='filled', color='lightpink')
                    raw.node('R1', 'customers', shape='box', style='filled', fillcolor='#ffcccc')
                    raw.node('R2', 'orders', shape='box', style='filled', fillcolor='#ffcccc')
                    raw.node('R3', 'order_items', shape='box', style='filled', fillcolor='#ffcccc')
                    raw.node('R4', 'order_payments', shape='box', style='filled', fillcolor='#ffcccc')
                    raw.node('R5', 'order_reviews', shape='box', style='filled', fillcolor='#ffcccc')
                    raw.node('R6', 'products', shape='box', style='filled', fillcolor='#ffcccc')
                    raw.node('R7', 'sellers', shape='box', style='filled', fillcolor='#ffcccc')

                # Staging layer
                with graph.subgraph(name='cluster_staging') as staging:
                    staging.attr(label='Staging Schema', style='filled', color='lightblue')
                    staging.node('S1', 'stg_customers', shape='box', style='filled', fillcolor='#cce5ff')
                    staging.node('S2', 'stg_orders', shape='box', style='filled', fillcolor='#cce5ff')
                    staging.node('S3', 'stg_order_items', shape='box', style='filled', fillcolor='#cce5ff')
                    staging.node('S4', 'stg_order_payments', shape='box', style='filled', fillcolor='#cce5ff')
                    staging.node('S5', 'stg_order_reviews', shape='box', style='filled', fillcolor='#cce5ff')
                    staging.node('S6', 'stg_products', shape='box', style='filled', fillcolor='#cce5ff')
                    staging.node('S7', 'stg_sellers', shape='box', style='filled', fillcolor='#cce5ff')

                # Intermediate layer
                with graph.subgraph(name='cluster_intermediate') as intermediate:
                    intermediate.attr(label='Intermediate Schema', style='filled', color='lightgreen')
                    intermediate.node('I1', 'int_customer_orders', shape='box', style='filled', fillcolor='#ccffcc')
                    intermediate.node('I2', 'int_rfm_scores', shape='box', style='filled', fillcolor='#ccffcc')
                    intermediate.node('I3', 'int_product_perf', shape='box', style='filled', fillcolor='#ccffcc')
                    intermediate.node('I4', 'int_seller_perf', shape='box', style='filled', fillcolor='#ccffcc')

                # Marts layer
                with graph.subgraph(name='cluster_marts') as marts:
                    marts.attr(label='Marts Schema', style='filled', color='lightyellow')
                    marts.node('M1', 'fct_orders', shape='box', style='filled', fillcolor='#ffffcc')
                    marts.node('M2', 'fct_order_items', shape='box', style='filled', fillcolor='#ffffcc')
                    marts.node('M3', 'dim_customers', shape='box', style='filled', fillcolor='#ffffcc')
                    marts.node('M4', 'dim_products', shape='box', style='filled', fillcolor='#ffffcc')
                    marts.node('M5', 'dim_sellers', shape='box', style='filled', fillcolor='#ffffcc')

                # Raw to Staging edges
                graph.edge('R1', 'S1')
                graph.edge('R2', 'S2')
                graph.edge('R3', 'S3')
                graph.edge('R4', 'S4')
                graph.edge('R5', 'S5')
                graph.edge('R6', 'S6')
                graph.edge('R7', 'S7')

                # Staging to Intermediate edges
                graph.edge('S1', 'I1')
                graph.edge('S2', 'I1')
                graph.edge('S3', 'I1')
                graph.edge('S1', 'I2')
                graph.edge('S2', 'I2')
                graph.edge('S3', 'I3')
                graph.edge('S6', 'I3')
                graph.edge('S3', 'I4')
                graph.edge('S7', 'I4')

                # Intermediate to Marts edges
                graph.edge('I1', 'M3')
                graph.edge('I2', 'M3')
                graph.edge('I3', 'M4')
                graph.edge('I4', 'M5')

                # Staging to Marts edges (facts)
                graph.edge('S1', 'M1')
                graph.edge('S2', 'M1')
                graph.edge('S3', 'M1')
                graph.edge('S4', 'M1')
                graph.edge('S5', 'M1')
                graph.edge('S1', 'M2')
                graph.edge('S2', 'M2')
                graph.edge('S3', 'M2')

                st.graphviz_chart(graph)

                # Legend
                st.markdown("""
                **Legend:**
                - 🔴 **Raw (Pink):** Original CSV data from Kaggle
                - 🔵 **Staging (Blue):** Type casting, column renaming, basic cleaning
                - 🟢 **Intermediate (Green):** Business logic, aggregations, RFM scoring
                - 🟡 **Marts (Yellow):** Star schema (facts & dimensions) for analytics
                """)

            with explorer_tab3:
                st.subheader("Table & View Definitions")

                st.markdown("View the SQL code that defines each table/view in the database.")

                # Schema selector
                def_schema = st.selectbox(
                    "Select Schema",
                    ['staging', 'intermediate', 'marts'],
                    key='def_schema'
                )

                # Get views/tables
                view_objects = con.execute(f"""
                    SELECT table_name, table_type
                    FROM information_schema.tables
                    WHERE table_schema = '{def_schema}'
                    ORDER BY table_name
                """).df()

                if len(view_objects) > 0:
                    selected_object = st.selectbox(
                        "Select Table/View",
                        view_objects['table_name'].tolist(),
                        key='def_table'
                    )

                    # Get SQL definition
                    try:
                        sql_def = con.execute(f"""
                            SELECT sql
                            FROM duckdb_views()
                            WHERE schema_name = '{def_schema}'
                            AND view_name = '{selected_object}'
                        """).fetchone()

                        if sql_def and sql_def[0]:
                            st.markdown(f"### SQL Definition: `{def_schema}.{selected_object}`")

                            # Format SQL with sqlparse
                            import sqlparse
                            formatted_sql = sqlparse.format(
                                sql_def[0],
                                reindent=True,
                                keyword_case='upper',
                                indent_width=4
                            )

                            st.code(formatted_sql, language='sql')

                            # Show row count
                            row_count = con.execute(f"SELECT COUNT(*) FROM {def_schema}.{selected_object}").fetchone()[0]
                            st.info(f"📊 **Row count:** {row_count:,} rows")

                        else:
                            # Try getting table info instead
                            st.info(f"ℹ️ `{selected_object}` is a table (not a view). Showing table structure instead.")

                            table_info = con.execute(f"""
                                SELECT
                                    column_name,
                                    data_type,
                                    is_nullable
                                FROM information_schema.columns
                                WHERE table_schema = '{def_schema}'
                                AND table_name = '{selected_object}'
                                ORDER BY ordinal_position
                            """).df()

                            st.dataframe(table_info, use_container_width=True)

                            # Show row count
                            row_count = con.execute(f"SELECT COUNT(*) FROM {def_schema}.{selected_object}").fetchone()[0]
                            st.info(f"📊 **Row count:** {row_count:,} rows")

                    except Exception as e:
                        st.error(f"Error retrieving definition: {e}")

            con.close()

        except Exception as e:
            st.error(f"Error loading data explorer: {e}")


elif page == "ℹ️ About":
    st.title("About This Project")

    st.markdown("""
    ## E-Commerce Analytics Platform

    This is a comprehensive analytics platform built with modern data tools.

    ### Tech Stack

    - **Frontend**: Streamlit
    - **Database**: DuckDB (embedded OLAP database)
    - **Transformation**: dbt (data build tool)
    - **Data Source**: Kaggle (Brazilian E-Commerce Public Dataset by Olist)

    ### Features

    - ✅ Automated data pipeline from Kaggle to DuckDB
    - ✅ dbt transformations (staging → intermediate → marts)
    - ✅ Star schema dimensional model
    - ✅ Interactive analytics dashboard
    - ✅ Customer segmentation (RFM analysis)
    - ✅ 70+ data quality tests

    ### Dataset

    The [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
    contains information of 100k orders from 2016 to 2018 made at multiple marketplaces in Brazil.

    ### Project Structure

    ```
    ├── app.py                          # Streamlit app
    ├── ecommerce.duckdb               # Pre-built database (committed to Git)
    ├── scripts/
    │   └── download_and_load_data.py  # Kaggle → DuckDB pipeline
    ├── dbt/
    │   └── ecommerce_analytics/       # dbt project
    │       ├── models/
    │       │   ├── staging/           # Raw data cleaning
    │       │   ├── intermediate/      # Business logic
    │       │   └── marts/             # Star schema
    └── data/
        └── raw/                       # CSV files from Kaggle
    ```

    ### Deployment Architecture

    **For instant portfolio experience:**
    - Pre-built database (`ecommerce.duckdb`) is committed to Git
    - Visitors get **instant access** to the dashboard (no waiting!)
    - Optional "Refresh Data" button to demo the full pipeline

    **Local development:**
    ```bash
    # Clone repo
    git clone <repo-url>

    # Install dependencies
    pip install -r requirements.txt

    # Run app (uses existing database)
    streamlit run app.py

    # Or rebuild from scratch
    python scripts/download_and_load_data.py
    cd dbt && dbt build
    ```

    ### Developer

    Built as a portfolio project to demonstrate:
    - Analytics engineering with dbt
    - Modern data stack proficiency
    - Dashboard development
    - Data pipeline orchestration
    - Production-ready deployment strategy
    """)
