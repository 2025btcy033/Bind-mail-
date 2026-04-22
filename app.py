import streamlit as st
import requests
import hashlib

# ==========================================
# GLOBAL SETTINGS & HELPERS
# ==========================================
HEADERS = {
    "User-Agent": "GarenaMSDK/4.0.30",
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}

APP_ID = "100067"
REGION = "PK"
LOCALE = "en_PK"

def call_post(url, data):
    try:
        resp = requests.post(url, headers=HEADERS, data=data)
        return resp.json()
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}

# ==========================================
# STREAMLIT UI SETUP
# ==========================================
st.set_page_config(page_title="Account Management Tool", layout="centered")
st.title("Account Management Tool")

# Sidebar navigation
menu = [
    "1. Bind Info", 
    "2. Send OTP", 
    "3. Unbind (OTP)", 
    "4. Unbind (Secondary Pass)", 
    "5. Rebind (Secondary Pass) - Step 1", 
    "6. Verify Rebind - Step 2", 
    "7. Cancel Bind", 
    "8. Change Bind (OTP)"
]
choice = st.sidebar.selectbox("Select an Action", menu)

# ==========================================
# 1. BIND INFO
# ==========================================
if choice == "1. Bind Info":
    st.header("Get Bind Info")
    access_token = st.text_input("Access Token")
    
    if st.button("Fetch Info"):
        if not access_token:
            st.error("Access token is required")
        else:
            url = f"https://bind-info-nu.vercel.app/bind_info?access_token={access_token}"
            try:
                resp = requests.get(url)
                st.json(resp.json())
            except Exception as e:
                st.error(f"Failed to fetch bind info: {str(e)}")

# ==========================================
# 2. SEND OTP
# ==========================================
elif choice == "2. Send OTP":
    st.header("Send OTP")
    access_token = st.text_input("Access Token")
    email = st.text_input("Email Address")
    
    if st.button("Send OTP"):
        if not access_token or not email:
            st.error("Access token and email are required")
        else:
            url_send = "https://100067.connect.garena.com/game/account_security/bind:send_otp"
            payload = {"email": email, "app_id": APP_ID, "access_token": access_token, "locale": LOCALE, "region": REGION}
            res = call_post(url_send, payload)
            st.json(res)

# ==========================================
# 3. UNBIND OTP-BASED
# ==========================================
elif choice == "3. Unbind (OTP)":
    st.header("Unbind Account via OTP")
    access_token = st.text_input("Access Token")
    email = st.text_input("Email Address")
    otp = st.text_input("OTP Code")
    
    if st.button("Submit Unbind"):
        if not access_token or not email or not otp:
            st.error("All fields are required")
        else:
            # Step 1: Verify OTP
            res_identity = call_post(
                "https://100067.connect.garena.com/game/account_security/bind:verify_identity",
                {"email": email, "app_id": APP_ID, "access_token": access_token, "otp": otp}
            )
            identity_token = res_identity.get("identity_token")
            
            if not identity_token:
                st.error("Identity verification failed.")
                st.json(res_identity)
            else:
                # Step 2: Create Unbind
                res_unbind = call_post(
                    "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request",
                    {"app_id": APP_ID, "access_token": access_token, "identity_token": identity_token}
                )
                st.success("Unbind request created!")
                st.json(res_unbind)

# ==========================================
# 4. UNBIND SECONDARY PASSWORD
# ==========================================
elif choice == "4. Unbind (Secondary Pass)":
    st.header("Unbind via Secondary Password")
    access_token = st.text_input("Access Token")
    security_code = st.text_input("Security Code (Secondary Password)")
    
    if st.button("Submit Unbind"):
        if not access_token or not security_code:
            st.error("All fields are required")
        else:
            secondary_password = hashlib.sha256(security_code.encode()).hexdigest().upper()
            
            # Step 1: Verify Identity
            res_identity = call_post(
                "https://100067.connect.garena.com/game/account_security/bind:verify_identity",
                {"secondary_password": secondary_password, "app_id": APP_ID, "access_token": access_token}
            )
            identity_token = res_identity.get("identity_token")
            
            if not identity_token:
                st.error("Identity verification failed.")
                st.json(res_identity)
            else:
                # Step 2: Create Unbind
                res_unbind = call_post(
                    "https://100067.connect.garena.com/game/account_security/bind:create_unbind_request",
                    {"app_id": APP_ID, "access_token": access_token, "identity_token": identity_token}
                )
                st.success("Unbind request created!")
                st.json(res_unbind)

# ==========================================
# 5. REBIND SECONDARY PASSWORD (STEP 1)
# ==========================================
elif choice == "5. Rebind (Secondary Pass) - Step 1":
    st.header("Rebind via Secondary Password (Step 1)")
    st.info("This step verifies your password and sends an OTP to your new email.")
    
    access_token = st.text_input("Access Token")
    security_code = st.text_input("Security Code")
    new_email = st.text_input("New Email Address")
    
    if st.button("Verify & Send OTP"):
        if not access_token or not security_code or not new_email:
            st.error("All fields are required")
        else:
            secondary_password = hashlib.sha256(security_code.encode()).hexdigest().upper()
            
            # Step 1: Verify Identity
            res_identity = call_post(
                "https://100067.connect.garena.com/game/account_security/bind:verify_identity",
                {"secondary_password": secondary_password, "app_id": APP_ID, "access_token": access_token}
            )
            identity_token = res_identity.get("identity_token")
            
            if not identity_token:
                st.error("Identity verification failed.")
                st.json(res_identity)
            else:
                # Step 2: Send OTP
                res_send = call_post(
                    "https://100067.connect.garena.com/game/account_security/bind:send_otp",
                    {"email": new_email, "locale": LOCALE, "region": REGION, "app_id": APP_ID, "access_token": access_token}
                )
                if res_send.get("result") != 0:
                    st.error("Failed to send OTP.")
                    st.json(res_send)
                else:
                    st.success("OTP sent successfully to the new email!")
                    st.warning("⚠️ Copy the Identity Token below, you will need it for Step 2:")
                    st.code(identity_token)

# ==========================================
# 6. VERIFY REBIND SECONDARY (STEP 2)
# ==========================================
elif choice == "6. Verify Rebind - Step 2":
    st.header("Verify OTP & Complete Rebind (Step 2)")
    
    access_token = st.text_input("Access Token")
    identity_token = st.text_input("Identity Token (Generated from Step 1)")
    new_email = st.text_input("New Email Address")
    otp = st.text_input("OTP Code")
    
    if st.button("Complete Rebind"):
        if not all([access_token, identity_token, new_email, otp]):
            st.error("All fields are required")
        else:
            # Step 3: Verify OTP
            res_verify = call_post(
                "https://100067.connect.garena.com/game/account_security/bind:verify_otp",
                {"email": new_email, "app_id": APP_ID, "access_token": access_token, "otp": otp}
            )
            verifier_token = res_verify.get("verifier_token")
            
            if not verifier_token:
                st.error("OTP Verification failed.")
                st.json(res_verify)
            else:
                # Step 4: Create Rebind
                res_rebind = call_post(
                    "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request",
                    {
                        "identity_token": identity_token,
                        "email": new_email,
                        "app_id": APP_ID,
                        "verifier_token": verifier_token,
                        "access_token": access_token
                    }
                )
                st.success("Rebind request complete!")
                st.json(res_rebind)

# ==========================================
# 7. CANCEL BIND
# ==========================================
elif choice == "7. Cancel Bind":
    st.header("Cancel Bind Request")
    access_token = st.text_input("Access Token")
    
    if st.button("Cancel Request"):
        if not access_token:
            st.error("Access token is required")
        else:
            res_cancel = call_post(
                "https://100067.connect.gopapi.io/game/account_security/bind:cancel_request",
                {"app_id": APP_ID, "access_token": access_token}
            )
            st.json(res_cancel)

# ==========================================
# 8. CHANGE BIND (OTP)
# ==========================================
elif choice == "8. Change Bind (OTP)":
    st.header("Change Bind via OTP")
    
    access_token = st.text_input("Access Token")
    old_email = st.text_input("Old Email Address")
    old_otp = st.text_input("Old Email OTP")
    new_email = st.text_input("New Email Address")
    new_otp = st.text_input("New Email OTP")
    
    if st.button("Submit Change"):
        if not all([access_token, old_email, old_otp, new_email, new_otp]):
            st.error("All fields are required")
        else:
            # Step 1: Verify Old Email OTP
            res_identity = call_post(
                "https://100067.connect.garena.com/game/account_security/bind:verify_identity",
                {"email": old_email, "app_id": APP_ID, "access_token": access_token, "otp": old_otp}
            )
            identity_token = res_identity.get("identity_token")
            
            if not identity_token:
                st.error("Identity verification (Old Email) failed.")
                st.json(res_identity)
            else:
                # Step 2: Verify New Email OTP
                res_verifier = call_post(
                    "https://100067.connect.garena.com/game/account_security/bind:verify_otp",
                    {"email": new_email, "app_id": APP_ID, "access_token": access_token, "otp": new_otp}
                )
                verifier_token = res_verifier.get("verifier_token")
                
                if not verifier_token:
                    st.error("Verifier token generation (New Email) failed.")
                    st.json(res_verifier)
                else:
                    # Step 3: Create Rebind
                    res_rebind = call_post(
                        "https://100067.connect.garena.com/game/account_security/bind:create_rebind_request",
                        {
                            "identity_token": identity_token,
                            "email": new_email,
                            "app_id": APP_ID,
                            "verifier_token": verifier_token,
                            "access_token": access_token
                        }
                    )
                    st.success("Change request complete!")
                    st.json(res_rebind)
                
