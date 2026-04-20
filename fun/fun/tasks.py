import frappe
from frappe.utils import now_datetime


def delete_expired_statuses():
    """
    Hourly cleanup: deletes all User Status documents whose expires_at
    is in the past. Runs once per hour via the Frappe scheduler.
    """
    now = now_datetime()
    expired = frappe.get_all(
        "User Status",
        filters=[["expires_at", "<", now]],
        fields=["name"],
    )
    for row in expired:
        try:
            frappe.delete_doc("User Status", row.name, ignore_permissions=True)
        except Exception:
            frappe.log_error(f"Failed to delete expired status: {row.name}")
    if expired:
        frappe.db.commit()
        frappe.logger().info(f"[tasks] Deleted {len(expired)} expired statuses.")
