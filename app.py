import streamlit as st
import pandas as pd
import numpy as np
import joblib
import json
import random
from datetime import datetime

from database import get_connection


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="SecureBank",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #0b1220;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }

    p, label, span {
        color: #cbd5e1;
    }

    [data-testid="stSidebar"] {
        background-color: #0d243b;
        border-right: 1px solid #1e3a56;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
    }

    [data-baseweb="input"] {
        background-color: #151c2b !important;
        border-radius: 10px !important;
    }

    [data-baseweb="input"] input {
        color: #ffffff !important;
    }

    [data-baseweb="select"] > div {
        background-color: #151c2b !important;
        border-color: #334155 !important;
        border-radius: 10px !important;
    }

    [data-baseweb="select"] span {
        color: #ffffff !important;
    }

    [data-testid="stNumberInput"] button {
        background-color: #1e293b !important;
        color: white !important;
    }

    .stButton > button {
        min-height: 44px;
        border-radius: 10px;
        font-weight: 700;
        border: 1px solid #334155;
    }

    .stButton > button[kind="primary"] {
        background-color: #2563eb !important;
        color: white !important;
        border: 1px solid #3b82f6 !important;
    }

    [data-testid="stForm"] {
        background-color: #111827;
        border: 1px solid #263448;
        border-radius: 16px;
        padding: 24px;
    }

    [data-testid="stMetric"] {
        background-color: #111827;
        border: 1px solid #263448;
        border-radius: 14px;
        padding: 16px;
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    [data-testid="stExpander"] {
        background-color: #111827;
        border: 1px solid #263448;
        border-radius: 12px;
    }

    .security-card {
        background: #111827;
        border: 1px solid #263448;
        border-radius: 16px;
        padding: 22px;
        margin-bottom: 15px;
    }

    .security-title {
        color: #f8fafc;
        font-size: 20px;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .security-text {
        color: #94a3b8;
        font-size: 14px;
    }

    .risk-critical {
        background: #3f1515;
        border: 1px solid #7f1d1d;
        border-radius: 16px;
        padding: 22px;
    }

    .risk-high {
        background: #422006;
        border: 1px solid #92400e;
        border-radius: 16px;
        padding: 22px;
    }

    .risk-medium {
        background: #3f3507;
        border: 1px solid #854d0e;
        border-radius: 16px;
        padding: 22px;
    }

    .risk-low {
        background: #0f2d23;
        border: 1px solid #166534;
        border-radius: 16px;
        padding: 22px;
    }

    .big-risk {
        font-size: 30px;
        font-weight: 800;
        color: white;
    }

    .small-white {
        color: #e2e8f0;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# SESSION STATE
# ============================================================

PAGES = [
    "Home",
    "Check a Payment",
    "Transactions",
    "Security",
    "Live Fraud Monitoring"
]

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "kafka_status" not in st.session_state:
    st.session_state.kafka_status = None


# ============================================================
# NAVIGATION
# ============================================================

def go_to(page):
    if page in PAGES:
        st.session_state.page = page
        st.rerun()


def previous_page():
    current = PAGES.index(st.session_state.page)
    st.session_state.page = PAGES[(current - 1) % len(PAGES)]
    st.rerun()


def next_page():
    current = PAGES.index(st.session_state.page)
    st.session_state.page = PAGES[(current + 1) % len(PAGES)]
    st.rerun()


# ============================================================
# DATABASE
# ============================================================

@st.cache_data(ttl=5, show_spinner=False)
def load_data():

    conn = None

    try:

        conn = get_connection()

        query = """
        SELECT
            transaction_id,
            customer_id,
            transaction_date,
            amount,
            transaction_type,
            city,
            device_type,
            hour,
            is_fraud,
            fraud_type,
            fraud_probability,
            risk_level,
            prediction_source
        FROM transactions
        ORDER BY transaction_date DESC, transaction_id DESC
        """

        data = pd.read_sql(query, conn)

        if data.empty:
            return data

        data["transaction_date"] = pd.to_datetime(
            data["transaction_date"],
            errors="coerce"
        )

        for column in ["amount", "fraud_probability"]:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            ).fillna(0)

        for column in ["customer_id", "hour", "is_fraud"]:

            data[column] = pd.to_numeric(
                data[column],
                errors="coerce"
            ).fillna(0).astype(int)

        data["risk_level"] = (
            data["risk_level"]
            .fillna("LOW")
            .astype(str)
            .str.upper()
        )

        data["transaction_type"] = (
            data["transaction_type"]
            .fillna("UNKNOWN")
            .astype(str)
            .str.upper()
        )

        data["city"] = (
            data["city"]
            .fillna("Unknown")
            .astype(str)
        )

        data["device_type"] = (
            data["device_type"]
            .fillna("Unknown")
            .astype(str)
        )

        return data

    except Exception as e:

        st.error(
            "Unable to load transaction data from MySQL."
        )

        return pd.DataFrame()

    finally:

        if conn:
            conn.close()


# ============================================================
# UNIQUE TRANSACTION ID
# ============================================================

def generate_transaction_id():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        for _ in range(20):

            transaction_id = random.randint(
                100000,
                999999999
            )

            cursor.execute(
                """
                SELECT transaction_id
                FROM transactions
                WHERE transaction_id = %s
                """,
                (transaction_id,)
            )

            if cursor.fetchone() is None:
                return transaction_id

        return int(
            datetime.now().strftime("%H%M%S%f")[:9]
        )

    except Exception:

        return int(
            datetime.now().strftime("%H%M%S%f")[:9]
        )

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# SAVE TRANSACTION
# ============================================================

def save_transaction(
    transaction_id,
    customer_id,
    amount,
    method,
    city,
    device,
    hour,
    probability,
    risk,
    prediction_source="STREAMLIT"
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO transactions
        (
            transaction_id,
            customer_id,
            transaction_date,
            amount,
            transaction_type,
            city,
            device_type,
            hour,
            is_fraud,
            fraud_type,
            fraud_probability,
            risk_level,
            prediction_source
        )
        VALUES
        (
            %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s
        )
        ON DUPLICATE KEY UPDATE
            fraud_probability = VALUES(fraud_probability),
            risk_level = VALUES(risk_level),
            prediction_source = VALUES(prediction_source)
        """

        values = (
            int(transaction_id),
            int(customer_id),
            datetime.now().date(),
            float(amount),
            str(method).upper(),
            str(city).title(),
            str(device).title(),
            int(hour),
            0,
            "Normal",
            float(probability),
            str(risk).upper(),
            prediction_source
        )

        cursor.execute(query, values)

        conn.commit()

        return True, None

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# ============================================================
# SEND TO KAFKA
# ============================================================

def send_to_kafka(transaction):

    try:

        from kafka import KafkaProducer

        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda value:
                json.dumps(value).encode("utf-8"),
            request_timeout_ms=5000,
            api_version_auto_timeout_ms=5000
        )

        future = producer.send(
            "bank_transactions",
            transaction
        )

        future.get(timeout=5)

        producer.flush()
        producer.close()

        return True, None

    except Exception as e:

        return False, str(e)


# ============================================================
# MODEL
# ============================================================

@st.cache_resource
def load_model():

    try:

        return joblib.load(
            "model/fraud_model.pkl"
        )

    except Exception:

        return None


@st.cache_resource
def load_config():

    try:

        return joblib.load(
            "model/model_config.pkl"
        )

    except Exception:

        return {}


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def build_features(
    customer_id,
    amount,
    method,
    city,
    device,
    hour
):

    method = str(method).upper()
    city = str(city).title()
    device = str(device).title()

    transaction_date = pd.Timestamp.today().normalize()

    row = pd.DataFrame(
        [{
            "transaction_id": 999999,
            "customer_id": int(customer_id),
            "transaction_date": transaction_date,
            "amount": float(amount),
            "transaction_type": method,
            "city": city,
            "device_type": device,
            "hour": int(hour),
            "is_fraud": 0,
            "fraud_type": "Normal"
        }]
    )

    row["is_night_transaction"] = (
        row["hour"].between(0, 4)
    ).astype(int)

    row["is_high_value"] = (
        row["amount"] > 50000
    ).astype(int)

    row["is_very_high_value"] = (
        row["amount"] > 100000
    ).astype(int)

    row["is_weekend"] = (
        row["transaction_date"].dt.dayofweek >= 5
    ).astype(int)

    row["is_upi"] = (
        row["transaction_type"] == "UPI"
    ).astype(int)

    row["is_card"] = (
        row["transaction_type"] == "CARD"
    ).astype(int)

    row["is_atm"] = (
        row["transaction_type"] == "ATM"
    ).astype(int)

    row["is_upi_night"] = (
        (row["transaction_type"] == "UPI") &
        (row["hour"] <= 5)
    ).astype(int)

    row["is_large_atm"] = (
        (row["transaction_type"] == "ATM") &
        (row["amount"] > 60000)
    ).astype(int)

    row["amount_log"] = np.log1p(
        row["amount"]
    )

    return row


# ============================================================
# FRAUD SCREENING
# ============================================================

def screen(
    customer_id,
    amount,
    method,
    city,
    device,
    hour
):

    model = load_model()
    config = load_config()

    if model is None:

        return None, "UNAVAILABLE"

    try:

        row = build_features(
            customer_id,
            amount,
            method,
            city,
            device,
            hour
        )

        features = config.get(
            "features",
            []
        )

        if features:

            row = row.reindex(
                columns=features,
                fill_value=0
            )

        probability = float(
            model.predict_proba(row)[0][1]
        )

        if probability >= 0.70:

            risk = "CRITICAL"

        elif probability >= 0.50:

            risk = "HIGH"

        elif probability >= 0.30:

            risk = "MEDIUM"

        else:

            risk = "LOW"

        return probability, risk

    except Exception:

        return None, "UNAVAILABLE"


# ============================================================
# EXPLANATION
# ============================================================

def get_reasons(
    amount,
    method,
    city,
    device,
    hour
):

    reasons = []

    if amount > 100000:

        reasons.append(
            "Very high-value payment detected."
        )

    elif amount > 50000:

        reasons.append(
            "The payment amount is relatively high."
        )

    if 0 <= hour <= 4:

        reasons.append(
            "The payment is being attempted during "
            "overnight hours."
        )

    if method == "UPI" and hour <= 5:

        reasons.append(
            "UPI is being used during unusual hours."
        )

    if method == "ATM" and amount > 60000:

        reasons.append(
            "The ATM withdrawal amount is unusually large."
        )

    if device == "Unknown":

        reasons.append(
            "The selected device is not recognised."
        )

    if amount > 100000 and hour <= 4:

        reasons.append(
            "The combination of a very high amount "
            "and overnight timing increases the risk."
        )

    if not reasons:

        reasons.append(
            "No major warning signal was detected "
            "from the supplied payment details."
        )

    return reasons


# ============================================================
# RECOMMENDATION
# ============================================================

def get_recommendation(risk):

    if risk == "CRITICAL":

        return (
            "STOP. Do not proceed until you verify "
            "the recipient, amount and payment request "
            "through an official banking channel."
        )

    if risk == "HIGH":

        return (
            "Pause the payment and carefully verify "
            "the recipient and amount before continuing."
        )

    if risk == "MEDIUM":

        return (
            "Review the transaction carefully. "
            "Continue only if you recognise the payment."
        )

    return (
        "The payment does not show major warning signals. "
        "Continue only if you recognise the recipient "
        "and amount."
    )


# ============================================================
# MONEY
# ============================================================

def money(value):

    return f"₹{float(value):,.2f}"


# ============================================================
# LOAD DATABASE
# ============================================================

df = load_data()


# ============================================================
# CUSTOMER LIST
# ============================================================

if not df.empty:

    customers = sorted(
        df["customer_id"]
        .dropna()
        .unique()
        .tolist()
    )

else:

    customers = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        "# 🏦 SecureBank"
    )

    st.caption(
        "Personal payment protection"
    )

    st.divider()

    if customers:

        default_customer = (
            1058
            if 1058 in customers
            else customers[0]
        )

        customer_id = st.selectbox(
            "Account",
            customers,
            index=customers.index(
                default_customer
            ),
            key="customer_selector"
        )

    else:

        customer_id = st.number_input(
            "Account",
            min_value=1,
            value=1058,
            step=1,
            key="customer_input"
        )

    st.caption(
        f"Customer ID: {customer_id}"
    )

    st.divider()

    st.markdown(
        "### Navigation"
    )

    for page_name in PAGES:

        if st.button(
            page_name,
            use_container_width=True,
            type=(
                "primary"
                if st.session_state.page == page_name
                else "secondary"
            ),
            key=f"nav_{page_name}"
        ):

            go_to(page_name)

    st.divider()

    if st.button(
        "↻ Refresh activity",
        use_container_width=True,
        key="refresh"
    ):

        st.cache_data.clear()
        st.rerun()

    st.caption(
        "SecureBank does not transfer real money. "
        "It evaluates transaction security."
    )


# ============================================================
# CUSTOMER DATA
# ============================================================

if not df.empty:

    customer_df = df[
        df["customer_id"] == customer_id
    ].copy()

else:

    customer_df = pd.DataFrame()


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "Home":

    st.title(
        "Good to see you."
    )

    st.caption(
        "Understand your spending and check a payment "
        "before you send it."
    )

    st.divider()

    if customer_df.empty:

        st.info(
            "No transaction activity is available "
            "for this account yet."
        )

    else:

        spending = customer_df["amount"].sum()
        count = len(customer_df)

        alerts = int(
            customer_df["risk_level"]
            .isin(["HIGH", "CRITICAL"])
            .sum()
        )

        safe_activity = max(
            count - alerts,
            0
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Transaction value",
                money(spending)
            )

        with c2:

            st.metric(
                "Transactions",
                f"{count:,}"
            )

        with c3:

            st.metric(
                "Needs attention",
                f"{alerts:,}"
            )

        with c4:

            st.metric(
                "Lower-risk activity",
                f"{safe_activity:,}"
            )

        st.write("")

        st.subheader(
            "Your activity"
        )

        graph1, graph2 = st.columns(2)

        with graph1:

            st.caption(
                "Spending over time"
            )

            spending_data = customer_df.dropna(
                subset=["transaction_date"]
            ).copy()

            if not spending_data.empty:

                spending_data["Date"] = (
                    spending_data[
                        "transaction_date"
                    ].dt.date
                )

                daily_spending = (
                    spending_data
                    .groupby("Date")["amount"]
                    .sum()
                    .sort_index()
                )

                st.line_chart(
                    daily_spending,
                    height=280
                )

        with graph2:

            st.caption(
                "Security activity"
            )

            risk_counts = (
                customer_df[
                    "risk_level"
                ]
                .value_counts()
                .reindex(
                    [
                        "LOW",
                        "MEDIUM",
                        "HIGH",
                        "CRITICAL"
                    ],
                    fill_value=0
                )
            )

            st.bar_chart(
                risk_counts,
                height=280
            )

        st.write("")

        st.subheader(
            "Recent activity"
        )

        recent = customer_df.head(8).copy()

        recent["Date"] = (
            recent["transaction_date"]
            .dt.strftime("%d %b %Y")
        )

        recent["Amount"] = (
            recent["amount"]
            .map(money)
        )

        recent["Payment"] = (
            recent["transaction_type"]
            .str.replace("_", " ")
        )

        table = recent[
            [
                "Date",
                "Payment",
                "city",
                "Amount",
                "risk_level"
            ]
        ].rename(
            columns={
                "city": "City",
                "risk_level": "Security"
            }
        )

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            height=300
        )

    st.write("")

    st.markdown(
        """
        <div class="security-card">
            <div class="security-title">
                🔐 About to make a payment?
            </div>
            <div class="security-text">
                Enter the payment details and SecureBank will
                evaluate the transaction using the fraud detection
                model before you proceed.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Check payment security →",
        type="primary",
        use_container_width=True,
        key="home_check"
    ):

        go_to("Check a Payment")


# ============================================================
# CHECK PAYMENT
# ============================================================

elif st.session_state.page == "Check a Payment":

    st.title(
        "Check a payment"
    )

    st.caption(
        "Enter the payment you are about to make. "
        "SecureBank will assess its security risk."
    )

    st.divider()

    # --------------------------------------------------------
    # QUICK SCENARIOS
    # --------------------------------------------------------

    st.subheader(
        "Quick scenarios"
    )

    q1, q2, q3 = st.columns(3)

    with q1:

        if st.button(
            "Normal payment",
            use_container_width=True
        ):

            st.session_state.demo_amount = 2500.0
            st.session_state.demo_method = "UPI"
            st.session_state.demo_city = "Bangalore"
            st.session_state.demo_device = "Mobile"
            st.session_state.demo_hour = datetime.now().hour
            st.rerun()

    with q2:

        if st.button(
            "Large payment",
            use_container_width=True
        ):

            st.session_state.demo_amount = 75000.0
            st.session_state.demo_method = "UPI"
            st.session_state.demo_city = "Bangalore"
            st.session_state.demo_device = "Mobile"
            st.session_state.demo_hour = 14
            st.rerun()

    with q3:

        if st.button(
            "Suspicious scenario",
            use_container_width=True
        ):

            st.session_state.demo_amount = 120000.0
            st.session_state.demo_method = "UPI"
            st.session_state.demo_city = "Bangalore"
            st.session_state.demo_device = "Mobile"
            st.session_state.demo_hour = 2
            st.rerun()

    amount_default = st.session_state.get(
        "demo_amount",
        5000.0
    )

    method_default = st.session_state.get(
        "demo_method",
        "UPI"
    )

    city_default = st.session_state.get(
        "demo_city",
        "Bangalore"
    )

    device_default = st.session_state.get(
        "demo_device",
        "Mobile"
    )

    hour_default = st.session_state.get(
        "demo_hour",
        datetime.now().hour
    )

    st.write("")

    # --------------------------------------------------------
    # PAYMENT FORM
    # --------------------------------------------------------

    with st.form(
        "payment_form",
        clear_on_submit=False
    ):

        st.subheader(
            "Payment details"
        )

        left, right = st.columns(2)

        with left:

            amount = st.number_input(
                "Amount",
                min_value=1.0,
                max_value=10000000.0,
                value=float(amount_default),
                step=500.0
            )

            methods = [
                "UPI",
                "CARD",
                "ATM",
                "BANK_TRANSFER"
            ]

            method = st.selectbox(
                "Payment method",
                methods,
                index=methods.index(method_default)
                if method_default in methods
                else 0
            )

            cities = [
                "Bangalore",
                "Mumbai",
                "Delhi",
                "Hyderabad",
                "Chennai",
                "Pune",
                "Kolkata",
                "Ahmedabad"
            ]

            city = st.selectbox(
                "Payment location",
                cities,
                index=cities.index(city_default)
                if city_default in cities
                else 0
            )

        with right:

            devices = [
                "Mobile",
                "Desktop",
                "Tablet",
                "Unknown"
            ]

            device = st.selectbox(
                "Device",
                devices,
                index=devices.index(device_default)
                if device_default in devices
                else 0
            )

            current_payment_time = datetime.now()

            st.markdown(
                f"""
                <div class="security-card" style="margin-top: 8px;">
                    <div class="security-title">
                        Current payment time
                    </div>
                    <div class="big-risk" style="font-size: 26px;">
                        {current_payment_time.strftime("%I:%M:%S %p")}
                    </div>
                    <div class="security-text">
                        SecureBank automatically uses the current time
                        when this payment is checked.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        st.info(
            "This is a security check only. "
            "No real payment will be transferred."
        )

        submitted = st.form_submit_button(
            "🔍 Check payment security",
            type="primary",
            use_container_width=True
        )

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    if submitted:

        if amount <= 0:

            st.error(
                "Please enter a valid payment amount."
            )

        else:

            # Capture the exact current time when the payment is checked.
            payment_checked_at = datetime.now()
            hour = payment_checked_at.hour

            with st.spinner(
                "Analysing payment risk..."
            ):

                probability, risk = screen(
                    customer_id,
                    amount,
                    method,
                    city,
                    device,
                    hour
                )

            if risk == "UNAVAILABLE":

                st.error(
                    "The fraud detection model could not "
                    "process this payment."
                )

            else:

                transaction_id = (
                    generate_transaction_id()
                )

                percentage = probability * 100

                reasons_list = get_reasons(
                    amount,
                    method,
                    city,
                    device,
                    hour
                )

                recommendation = (
                    get_recommendation(risk)
                )

                # --------------------------------------------
                # SAVE TO MYSQL
                # --------------------------------------------

                saved, db_error = save_transaction(
                    transaction_id,
                    customer_id,
                    amount,
                    method,
                    city,
                    device,
                    hour,
                    probability,
                    risk
                )

                if not saved:

                    st.error(
                        "The payment was analysed, but "
                        "the result could not be saved."
                    )

                    st.code(db_error)

                else:

                    st.session_state.last_result = {
                        "transaction_id": transaction_id,
                        "customer_id": customer_id,
                        "amount": amount,
                        "method": method,
                        "city": city,
                        "device": device,
                        "hour": hour,
                        "probability": probability,
                        "risk": risk
                    }

                    st.cache_data.clear()

                    st.divider()

                    st.success(
                        f"Security check completed • "
                        f"Transaction #{transaction_id}"
                    )

                    # ----------------------------------------
                    # DECISION
                    # ----------------------------------------

                    if risk == "CRITICAL":

                        box_class = "risk-critical"

                        icon = "🛑"
                        title = "Payment blocked for review"

                    elif risk == "HIGH":

                        box_class = "risk-high"

                        icon = "⚠️"
                        title = "Payment requires caution"

                    elif risk == "MEDIUM":

                        box_class = "risk-medium"

                        icon = "⚠️"
                        title = "Payment needs review"

                    else:

                        box_class = "risk-low"

                        icon = "✓"
                        title = "Payment appears lower risk"

                    st.markdown(
                        f"""
                        <div class="{box_class}">
                            <div class="big-risk">
                                {icon} {title}
                            </div>
                            <br>
                            <div class="small-white">
                                Automated security assessment
                                based on the payment details provided.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.write("")

                    r1, r2, r3 = st.columns(3)

                    with r1:

                        st.metric(
                            "Security level",
                            risk
                        )

                    with r2:

                        st.metric(
                            "Risk score",
                            f"{percentage:.1f}%"
                        )

                    with r3:

                        st.metric(
                            "Amount",
                            money(amount)
                        )

                    st.progress(
                        min(
                            max(probability, 0),
                            1
                        ),
                        text=(
                            f"Fraud risk estimate: "
                            f"{percentage:.1f}%"
                        )
                    )

                    st.write("")

                    # ----------------------------------------
                    # RECOMMENDATION
                    # ----------------------------------------

                    st.subheader(
                        "What should you do?"
                    )

                    if risk == "CRITICAL":

                        st.error(
                            "🛑 " + recommendation
                        )

                    elif risk == "HIGH":

                        st.warning(
                            "⚠️ " + recommendation
                        )

                    elif risk == "MEDIUM":

                        st.warning(
                            "⚠️ " + recommendation
                        )

                    else:

                        st.success(
                            "✓ " + recommendation
                        )

                    st.write("")

                    # ----------------------------------------
                    # WHY
                    # ----------------------------------------

                    st.subheader(
                        "Why did the system give this result?"
                    )

                    for reason in reasons_list:

                        st.info(
                            "• " + reason
                        )

                    # ----------------------------------------
                    # PAYMENT DETAILS
                    # ----------------------------------------

                    st.subheader(
                        "Payment details"
                    )

                    s1, s2, s3, s4 = st.columns(4)

                    with s1:

                        st.metric(
                            "Method",
                            method
                        )

                    with s2:

                        st.metric(
                            "Location",
                            city
                        )

                    with s3:

                        st.metric(
                            "Device",
                            device
                        )

                    with s4:

                        st.metric(
                            "Time",
                            payment_checked_at.strftime("%H:%M:%S")
                        )

                    st.write("")

                    # ----------------------------------------
                    # KAFKA
                    # ----------------------------------------

                    st.subheader(
                        "Live fraud monitoring"
                    )

                    st.caption(
                        "Send this transaction into the real-time "
                        "Kafka → PySpark → ML → MySQL pipeline."
                    )

                    if st.button(
                        "⚡ Send to live fraud monitoring",
                        type="primary",
                        use_container_width=True,
                        key=f"kafka_{transaction_id}"
                    ):

                        kafka_transaction = {
                            "transaction_id": int(
                                transaction_id
                            ),
                            "customer_id": int(
                                customer_id
                            ),
                            "amount": float(
                                amount
                            ),
                            "transaction_type": str(
                                method
                            ).upper(),
                            "city": str(
                                city
                            ).title(),
                            "device_type": str(
                                device
                            ).title(),
                            "hour": int(
                                hour
                            )
                        }

                        with st.spinner(
                            "Sending transaction to "
                            "live monitoring..."
                        ):

                            kafka_ok, kafka_error = (
                                send_to_kafka(
                                    kafka_transaction
                                )
                            )

                        if kafka_ok:

                            st.session_state.kafka_status = (
                                "success"
                            )

                            st.success(
                                "Transaction sent to Kafka successfully. "
                                "PySpark can now process it in real time."
                            )

                        else:

                            st.session_state.kafka_status = (
                                "failed"
                            )

                            st.warning(
                                "The payment result is saved in MySQL, "
                                "but Kafka is currently unavailable."
                            )

                            with st.expander(
                                "Technical details"
                            ):

                                st.code(
                                    kafka_error
                                )

                    st.write("")

                    # ----------------------------------------
                    # NAVIGATION
                    # ----------------------------------------

                    n1, n2 = st.columns(2)

                    with n1:

                        if st.button(
                            "View transaction history",
                            use_container_width=True
                        ):

                            go_to(
                                "Transactions"
                            )

                    with n2:

                        if st.button(
                            "Check another payment",
                            use_container_width=True
                        ):

                            st.session_state.last_result = None
                            st.rerun()


# ============================================================
# TRANSACTIONS
# ============================================================

elif st.session_state.page == "Transactions":

    st.title(
        "Your transactions"
    )

    st.caption(
        "Review your payments and identify transactions "
        "that may require attention."
    )

    st.divider()

    fresh_df = load_data()

    if not fresh_df.empty:

        customer_df = fresh_df[
            fresh_df["customer_id"] == customer_id
        ].copy()

    if customer_df.empty:

        st.info(
            "No transactions are currently available "
            "for this account."
        )

    else:

        total_value = customer_df[
            "amount"
        ].sum()

        transaction_count = len(
            customer_df
        )

        attention_count = int(
            customer_df["risk_level"]
            .isin(
                [
                    "HIGH",
                    "CRITICAL"
                ]
            )
            .sum()
        )

        t1, t2, t3 = st.columns(3)

        with t1:

            st.metric(
                "Total value",
                money(total_value)
            )

        with t2:

            st.metric(
                "Transactions",
                f"{transaction_count:,}"
            )

        with t3:

            st.metric(
                "Needs attention",
                f"{attention_count:,}"
            )

        st.write("")

        # ----------------------------------------------------
        # ACTIVITY GRAPH
        # ----------------------------------------------------

        st.subheader(
            "Transaction activity"
        )

        graph_data = customer_df.dropna(
            subset=["transaction_date"]
        ).copy()

        if not graph_data.empty:

            graph_data["Date"] = (
                graph_data[
                    "transaction_date"
                ].dt.date
            )

            daily_transactions = (
                graph_data
                .groupby("Date")
                .size()
                .sort_index()
            )

            st.line_chart(
                daily_transactions,
                height=260
            )

        st.write("")

        # ----------------------------------------------------
        # FILTERS
        # ----------------------------------------------------

        st.subheader(
            "Find a transaction"
        )

        search = st.text_input(
            "Search",
            placeholder=(
                "Search city, payment method "
                "or security level"
            )
        )

        f1, f2, f3 = st.columns(3)

        with f1:

            methods = sorted(
                customer_df[
                    "transaction_type"
                ]
                .dropna()
                .unique()
                .tolist()
            )

            method_filter = st.selectbox(
                "Payment method",
                ["All"] + methods
            )

        with f2:

            risk_filter = st.selectbox(
                "Security",
                [
                    "All",
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL"
                ]
            )

        with f3:

            cities = sorted(
                customer_df[
                    "city"
                ]
                .dropna()
                .unique()
                .tolist()
            )

            city_filter = st.selectbox(
                "City",
                ["All"] + cities
            )

        view = customer_df.copy()

        if method_filter != "All":

            view = view[
                view[
                    "transaction_type"
                ] == method_filter
            ]

        if risk_filter != "All":

            view = view[
                view[
                    "risk_level"
                ] == risk_filter
            ]

        if city_filter != "All":

            view = view[
                view[
                    "city"
                ] == city_filter
            ]

        if search.strip():

            search_text = (
                search.strip().lower()
            )

            mask = (
                view[
                    "transaction_type"
                ]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
                |
                view[
                    "city"
                ]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
                |
                view[
                    "risk_level"
                ]
                .astype(str)
                .str.lower()
                .str.contains(
                    search_text,
                    na=False
                )
            )

            view = view[mask]

        st.write(
            f"**{len(view):,}** transactions found"
        )

        # ----------------------------------------------------
        # TABLE
        # ----------------------------------------------------

        show = view.copy()

        show["Date"] = (
            show[
                "transaction_date"
            ]
            .dt.strftime(
                "%d %b %Y"
            )
        )

        show["Amount"] = (
            show[
                "amount"
            ].map(money)
        )

        show["Risk score"] = (
            show[
                "fraud_probability"
            ]
            .mul(100)
            .round(1)
            .astype(str)
            + "%"
        )

        show["Payment"] = (
            show[
                "transaction_type"
            ]
            .astype(str)
            .str.replace(
                "_",
                " "
            )
        )

        table = show[
            [
                "transaction_id",
                "Date",
                "Payment",
                "city",
                "Amount",
                "Risk score",
                "risk_level"
            ]
        ].rename(
            columns={
                "transaction_id":
                    "Transaction ID",
                "city":
                    "City",
                "risk_level":
                    "Security"
            }
        )

        st.dataframe(
            table,
            hide_index=True,
            use_container_width=True,
            height=430
        )

        csv = show.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "Download transaction history",
            csv,
            "securebank_transactions.csv",
            "text/csv",
            use_container_width=True
        )


# ============================================================
# SECURITY
# ============================================================

elif st.session_state.page == "Security":

    st.title(
        "Security center"
    )

    st.caption(
        "Understand suspicious activity and learn "
        "how to respond safely."
    )

    st.divider()

    fresh_df = load_data()

    if not fresh_df.empty:

        customer_df = fresh_df[
            fresh_df["customer_id"] == customer_id
        ].copy()

    if customer_df.empty:

        st.info(
            "There is currently no security activity "
            "to review."
        )

    else:

        critical = customer_df[
            customer_df[
                "risk_level"
            ] == "CRITICAL"
        ]

        high = customer_df[
            customer_df[
                "risk_level"
            ] == "HIGH"
        ]

        medium = customer_df[
            customer_df[
                "risk_level"
            ] == "MEDIUM"
        ]

        low = customer_df[
            customer_df[
                "risk_level"
            ] == "LOW"
        ]

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(
                "Critical",
                len(critical)
            )

        with c2:

            st.metric(
                "High",
                len(high)
            )

        with c3:

            st.metric(
                "Medium",
                len(medium)
            )

        with c4:

            st.metric(
                "Low",
                len(low)
            )

        st.write("")

        st.subheader(
            "Security overview"
        )

        risk_counts = (
            customer_df[
                "risk_level"
            ]
            .value_counts()
            .reindex(
                [
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                    "CRITICAL"
                ],
                fill_value=0
            )
        )

        st.bar_chart(
            risk_counts,
            height=280
        )

        st.write("")

        # ----------------------------------------------------
        # SECURITY GUIDANCE
        # ----------------------------------------------------

        st.subheader(
            "If something looks unfamiliar"
        )

        g1, g2 = st.columns(2)

        with g1:

            st.markdown(
                """
                <div class="security-card">
                    <div class="security-title">
                        1. Stop
                    </div>
                    <div class="security-text">
                        Do not continue a payment you do
                        not recognise.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="security-card">
                    <div class="security-title">
                        2. Verify
                    </div>
                    <div class="security-text">
                        Check the recipient, amount and
                        payment request.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with g2:

            st.markdown(
                """
                <div class="security-card">
                    <div class="security-title">
                        3. Protect
                    </div>
                    <div class="security-text">
                        Never share OTPs, PINs, passwords
                        or banking credentials.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                """
                <div class="security-card">
                    <div class="security-title">
                        4. Contact
                    </div>
                    <div class="security-text">
                        If the transaction remains suspicious,
                        contact your bank through an official channel.
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ----------------------------------------------------
        # SUSPICIOUS TRANSACTIONS
        # ----------------------------------------------------

        suspicious = customer_df[
            customer_df[
                "risk_level"
            ].isin(
                [
                    "HIGH",
                    "CRITICAL"
                ]
            )
        ].copy()

        st.write("")

        if suspicious.empty:

            st.success(
                "✓ No high or critical transactions "
                "are currently visible for this account."
            )

        else:

            st.subheader(
                "Payments requiring attention"
            )

            alerts = suspicious.head(
                10
            ).copy()

            alerts["Date"] = (
                alerts[
                    "transaction_date"
                ]
                .dt.strftime(
                    "%d %b %Y"
                )
            )

            alerts["Amount"] = (
                alerts[
                    "amount"
                ].map(money)
            )

            alerts["Risk score"] = (
                alerts[
                    "fraud_probability"
                ]
                .mul(100)
                .round(1)
                .astype(str)
                + "%"
            )

            alerts["Payment"] = (
                alerts[
                    "transaction_type"
                ]
                .str.replace(
                    "_",
                    " "
                )
            )

            alert_table = alerts[
                [
                    "transaction_id",
                    "Date",
                    "Payment",
                    "city",
                    "Amount",
                    "Risk score",
                    "risk_level"
                ]
            ].rename(
                columns={
                    "transaction_id":
                        "Transaction ID",
                    "city":
                        "City",
                    "risk_level":
                        "Security"
                }
            )

            st.dataframe(
                alert_table,
                hide_index=True,
                use_container_width=True
            )

        with st.expander(
            "How SecureBank makes a decision"
        ):

            st.write(
                "The application sends the payment details "
                "through the trained fraud-detection model."
            )

            st.write(
                "The model produces a fraud probability. "
                "The application converts that probability "
                "into LOW, MEDIUM, HIGH or CRITICAL risk."
            )

            st.write(
                "For live monitoring, the transaction can then "
                "be sent to Kafka, processed by PySpark and "
                "written back to MySQL."
            )

            st.write(
                "The result is an automated security estimate, "
                "not a guarantee that a transaction is fraudulent."
            )


# ============================================================
# LIVE FRAUD MONITORING
# ============================================================

elif st.session_state.page == "Live Fraud Monitoring":

    st.title("Live Fraud Monitoring")

    st.caption(
        "Every payment checked in SecureBank appears here, with "
        "Kafka → PySpark processing available for live streaming."
    )

    st.divider()

    live_conn = None

    try:
        live_conn = get_connection()

        live_query = """
        SELECT
            transaction_id,
            customer_id,
            transaction_date,
            amount,
            transaction_type,
            city,
            device_type,
            hour,
            fraud_probability,
            risk_level,
            prediction_source
        FROM transactions
        WHERE prediction_source IN ('STREAMLIT', 'KAFKA_PYSPARK')
        ORDER BY transaction_date DESC, transaction_id DESC
        """

        live_df = pd.read_sql(live_query, live_conn)

    except Exception:
        live_df = pd.DataFrame()
        st.error("Unable to load live fraud monitoring data.")

    finally:
        if live_conn:
            live_conn.close()

    if live_df.empty:
        st.info(
            "No payments have been checked in SecureBank yet. "
            "Payments checked from the Check a Payment page will "
            "appear here automatically."
        )

    else:
        live_df["fraud_probability"] = pd.to_numeric(
            live_df["fraud_probability"], errors="coerce"
        ).fillna(0)

        live_df["risk_level"] = (
            live_df["risk_level"]
            .fillna("LOW")
            .astype(str)
            .str.upper()
        )

        critical_count = int((live_df["risk_level"] == "CRITICAL").sum())
        high_count = int((live_df["risk_level"] == "HIGH").sum())
        medium_count = int((live_df["risk_level"] == "MEDIUM").sum())

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Live transactions", len(live_df))

        with c2:
            st.metric("Critical", critical_count)

        with c3:
            st.metric("High", high_count)

        with c4:
            st.metric("Medium", medium_count)

        st.write("")

        st.subheader("Live risk distribution")

        risk_counts = (
            live_df["risk_level"]
            .value_counts()
            .reindex(
                ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
                fill_value=0
            )
        )

        st.bar_chart(
            risk_counts,
            height=300,
            use_container_width=True
        )

        st.write("")

        st.subheader("Latest processed transactions")

        display = live_df.copy()

        display["Amount"] = display["amount"].map(money)

        display["Risk score"] = (
            display["fraud_probability"]
            .mul(100)
            .round(1)
            .astype(str)
            + "%"
        )

        display["Payment"] = (
            display["transaction_type"]
            .astype(str)
            .str.replace("_", " ")
        )

        display["Source"] = display["prediction_source"]

        live_table = display[
            [
                "transaction_id",
                "customer_id",
                "Amount",
                "Payment",
                "city",
                "device_type",
                "hour",
                "Risk score",
                "risk_level",
                "Source"
            ]
        ].rename(
            columns={
                "transaction_id": "Transaction ID",
                "customer_id": "Customer ID",
                "city": "City",
                "device_type": "Device",
                "hour": "Hour",
                "risk_level": "Security"
            }
        )

        st.dataframe(
            live_table,
            hide_index=True,
            use_container_width=True,
            height=430
        )

        latest = live_df.iloc[0]
        latest_probability = float(latest["fraud_probability"])
        latest_risk = str(latest["risk_level"]).upper()

        st.write("")
        st.subheader("Latest alert")

        if latest_risk == "CRITICAL":
            st.error(
                f"🛑 Latest transaction #{int(latest['transaction_id'])} "
                f"is CRITICAL with a {latest_probability * 100:.1f}% "
                "fraud risk estimate."
            )
        elif latest_risk == "HIGH":
            st.warning(
                f"⚠️ Latest transaction #{int(latest['transaction_id'])} "
                f"is HIGH risk with a {latest_probability * 100:.1f}% "
                "fraud risk estimate."
            )
        else:
            st.info(
                f"Latest transaction #{int(latest['transaction_id'])} "
                f"was processed with {latest_probability * 100:.1f}% "
                f"fraud risk and {latest_risk} security level."
            )

    st.write("")

    if st.button(
        "↻ Refresh live monitoring",
        use_container_width=True,
        key="refresh_live_monitoring"
    ):
        st.cache_data.clear()
        st.rerun()

    st.info(
        "Live flow: Payment check → ML fraud scoring → MySQL → "
        "Live Fraud Monitoring. If sent to Kafka, the same payment "
        "also flows through Kafka → PySpark → ML → MySQL."
    )


# ============================================================
# BOTTOM NAVIGATION
# ============================================================

st.divider()

left, middle, right = st.columns(
    [1, 2, 1]
)

with left:

    if st.button(
        "← Previous",
        use_container_width=True,
        key="previous_page"
    ):

        previous_page()

with middle:

    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding-top:10px;
            color:#64748b;
            font-size:14px;
        ">
            SecureBank • {st.session_state.page}
        </div>
        """,
        unsafe_allow_html=True
    )

with right:

    if st.button(
        "Next →",
        use_container_width=True,
        key="next_page"
    ):

        next_page()