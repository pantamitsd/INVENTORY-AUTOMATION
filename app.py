from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

# 🔥 MULTI WAREHOUSE CONFIG
ACCOUNTS = {
    "RATAN": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000493",
        "warehouse_id": "600071"
    },
    "ACT B2B": {
        "cred": "act@swissmilitaryindia.com",
        "password": "Swiss@123",
        "seller_id": "80000332",
        "warehouse_id": "600040"
    },
    "RETAIL": {
        "cred": "billdesk@swissmilitaryindia.com",
        "password": "Emiza@123",
        "seller_id": "80000333",
        "warehouse_id": "600040"
    }
}

# ✅ HOME
@app.route("/")
def home():
    return "Inventory Server Running 🚀"


# 🔥 INVENTORY DOWNLOAD API
@app.route("/get-inventory", methods=["GET"])
def get_inventory():
    try:
        warehouse = request.args.get("warehouse")
        account = ACCOUNTS.get(warehouse)

        if not account:
            return jsonify({
                "status": "FAILED",
                "message": "Invalid warehouse"
            })

        # -----------------------
        # 🔐 LOGIN
        # -----------------------
        login_url = "https://edge-service.emizainc.com/identity-service/user/login"

        login_payload = {
            "cred": account["cred"],
            "password": account["password"],
            "user_type": "SELLERS",
            "is_otp_login": False
        }

        login_headers = {
            "content-type": "application/json",
            "x-device-id": "armaze-web"
        }

        login_res = requests.post(login_url, json=login_payload, headers=login_headers)

        pim_sid = login_res.headers.get("pim-sid")

        if not pim_sid:
            return jsonify({
                "status": "FAILED",
                "message": "Login failed"
            })

        # -----------------------
        # 📦 INVENTORY CSV API
        # -----------------------
        inventory_url = f"https://edge-service.emizainc.com/inventory-service/api/v1/inventory/report/seller/csv?report_type=inventory_snapshot&filter=created_at&seller_id={account['seller_id']}&warehouseId={account['warehouse_id']}"

        headers = {
            "pim-sid": pim_sid,
            "x-device-id": "armaze-web",
            "x-seller-id": account["seller_id"],
            "x-tenant-id": "1",
            "x-user-id": "300000000850",
            "x-warehouse-id": account["warehouse_id"]
        }

        res = requests.get(inventory_url, headers=headers)

        return Response(
            res.text,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=inventory.csv"}
        )

    except Exception as e:
        return jsonify({
            "status": "ERROR",
            "message": str(e)
        })


# 🔥 RUN
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
