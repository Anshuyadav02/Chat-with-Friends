import frappe
from frappe import _
from frappe.utils import now_datetime, add_days


# ─── Signup ───────────────────────────────────────────────────────────────────

@frappe.whitelist(allow_guest=True)
def signup(first_name, last_name, email, password):
    if frappe.db.exists("User", email):
        frappe.throw(_("An account with this email already exists."), frappe.DuplicateEntryError)

    user = frappe.get_doc({
        "doctype": "User",
        "email": email,
        "first_name": first_name,
        "last_name": last_name,
        "send_welcome_email": 0,
        "user_type": "System User",
    })
    user.insert(ignore_permissions=True)

    from frappe.utils.password import update_password
    update_password(email, password)
    frappe.local.login_manager.login_as(email)

    return {"status": "ok", "user": email}


# ─── Users ────────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_users():
    current_user = frappe.session.user
    users = frappe.get_all(
        "User",
        filters={
            "name": ["not in", [current_user, "Guest"]],
            "enabled": 1,
            "user_type": "System User",
        },
        fields=["name", "full_name", "first_name", "last_name", "user_image"],
        order_by="full_name asc",
    )
    return users


# ─── Send Message ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def send_message(receiver, message):
    sender = frappe.session.user
    now = now_datetime()
    today = now.date()

    # Always store user_1/user_2 in sorted order for consistent lookup
    u1, u2 = sorted([sender, receiver])
    cutoff = add_days(today, -2)

    # Find an active conversation between these two users (last active within 2 days)
    existing = frappe.db.sql("""
        SELECT name FROM `tabConversation`
        WHERE user_1 = %(u1)s AND user_2 = %(u2)s
          AND end_date >= %(cutoff)s
        ORDER BY end_date DESC
        LIMIT 1
    """, {"u1": u1, "u2": u2, "cutoff": str(cutoff)}, as_dict=True)

    if existing:
        conv = frappe.get_doc("Conversation", existing[0].name)
        conv.end_date = today
    else:
        conv = frappe.get_doc({
            "doctype": "Conversation",
            "user_1": u1,
            "user_2": u2,
            "start_date": today,
            "end_date": today,
        })

    conv.append("messages", {
        "sender": sender,
        "message": message,
        "timestamp": now,
    })

    if conv.is_new():
        conv.insert(ignore_permissions=True)
    else:
        conv.save(ignore_permissions=True)

    frappe.db.commit()

    payload = {
        "conversation_name": conv.name,
        "start_date": str(conv.start_date),
        "sender": sender,
        "receiver": receiver,
        "message": message,
        "timestamp": str(now),
    }

    # Notify both sender and receiver via realtime
    frappe.publish_realtime("new_message", payload, user=receiver)
    frappe.publish_realtime("new_message", payload, user=sender)

    return payload


# ─── Get Messages ─────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_messages(other_user):
    current_user = frappe.session.user
    u1, u2 = sorted([current_user, other_user])

    conversations = frappe.db.sql("""
        SELECT name, start_date, end_date
        FROM `tabConversation`
        WHERE user_1 = %(u1)s AND user_2 = %(u2)s
        ORDER BY start_date ASC
    """, {"u1": u1, "u2": u2}, as_dict=True)

    result = []
    for conv in conversations:
        doc = frappe.get_doc("Conversation", conv.name)
        messages = []
        for msg in doc.messages:
            messages.append({
                "sender": msg.sender,
                "message": msg.message,
                "timestamp": str(msg.timestamp) if msg.timestamp else "",
            })
        # Sort messages by timestamp ascending
        messages.sort(key=lambda m: m["timestamp"])
        result.append({
            "conversation_name": conv.name,
            "start_date": str(conv.start_date),
            "end_date": str(conv.end_date),
            "messages": messages,
        })

    return result


# ─── Get Conversations (sidebar preview) ─────────────────────────────────────

@frappe.whitelist()
def get_conversations():
    current_user = frappe.session.user

    # Get most recent conversation per peer
    convs = frappe.db.sql("""
        SELECT name, user_1, user_2, end_date
        FROM `tabConversation`
        WHERE user_1 = %(user)s OR user_2 = %(user)s
        ORDER BY end_date DESC
    """, {"user": current_user}, as_dict=True)

    result = []
    seen_peers = set()

    for conv in convs:
        peer = conv.user_2 if conv.user_1 == current_user else conv.user_1
        if peer in seen_peers:
            continue
        seen_peers.add(peer)

        # Get last message in this conversation
        last_msg = frappe.db.sql("""
            SELECT sender, message, timestamp
            FROM `tabChat Message`
            WHERE parent = %(conv)s
            ORDER BY timestamp DESC
            LIMIT 1
        """, {"conv": conv.name}, as_dict=True)

        user_info = frappe.db.get_value(
            "User", peer, ["full_name", "first_name", "user_image"], as_dict=True
        ) or {}

        result.append({
            "peer": peer,
            "full_name": user_info.get("full_name") or user_info.get("first_name") or peer,
            "user_image": user_info.get("user_image"),
            "last_message": last_msg[0].message if last_msg else "",
            "timestamp": str(last_msg[0].timestamp) if last_msg else "",
        })

    return result
