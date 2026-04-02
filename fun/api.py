import frappe
from frappe import _
from frappe.utils import add_days, format_duration, now_datetime, time_diff_in_seconds


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
    try:
        current_user = frappe.session.user
        users = frappe.get_all(
            "User",
            filters={
                "name": ["not in", [current_user, "Guest"]],
                "enabled": 1,
            },
            fields=["name", "full_name", "first_name", "last_name", "user_image"],
            order_by="full_name asc",
        )
        return users
    except Exception as e:
        frappe.log_error(f"Error in get_users: {str(e)}")
        return {"error": str(e)}


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


# ─── Call Logs / Calling ──────────────────────────────────────────────────────

ALLOWED_CALL_TYPES = {"Audio", "Video"}
ACTIVE_CALL_STATUSES = {"Ringing", "Ongoing"}


def _validate_call_type(call_type):
    normalized = (call_type or "").strip().title()
    if normalized not in ALLOWED_CALL_TYPES:
        frappe.throw(_("Invalid call type."))
    return normalized


def _serialize_call_log(doc, current_user=None):
    current_user = current_user or frappe.session.user
    peer = doc.receiver if doc.caller == current_user else doc.caller
    duration_seconds = 0

    if doc.start_time and doc.end_time:
        duration_seconds = max(int(time_diff_in_seconds(doc.end_time, doc.start_time)), 0)

    return {
        "name": doc.name,
        "call_id": doc.call_id,
        "caller": doc.caller,
        "receiver": doc.receiver,
        "peer": peer,
        "call_type": doc.call_type,
        "status": doc.status,
        "start_time": str(doc.start_time) if doc.start_time else "",
        "end_time": str(doc.end_time) if doc.end_time else "",
        "duration": doc.duration or "",
        "duration_seconds": duration_seconds,
        "direction": "outgoing" if doc.caller == current_user else "incoming",
    }


def _publish_call_event(event_name, payload, *users):
    for user in {u for u in users if u and u != "Guest"}:
        frappe.publish_realtime(event_name, payload, user=user)


def _get_call_log_for_user(call_id, user=None):
    user = user or frappe.session.user
    call_doc = frappe.get_doc("Call Log", call_id)
    if user not in {call_doc.caller, call_doc.receiver}:
        frappe.throw(_("You are not allowed to access this call."), frappe.PermissionError)
    return call_doc


def _save_call_log(call_doc):
    call_doc.save(ignore_permissions=True)
    frappe.db.commit()
    return call_doc


@frappe.whitelist()
def initiate_call(receiver, call_type, call_id=None):
    caller = frappe.session.user
    normalized_call_type = _validate_call_type(call_type)

    if receiver == caller:
        frappe.throw(_("You cannot call yourself."))

    if not frappe.db.exists("User", receiver):
        frappe.throw(_("Receiver does not exist."))

    call_id = (call_id or frappe.generate_hash(length=14)).strip()

    if frappe.db.exists("Call Log", call_id):
        frappe.throw(_("Call ID already exists. Please retry."))

    now = now_datetime()
    call_doc = frappe.get_doc(
        {
            "doctype": "Call Log",
            "call_id": call_id,
            "caller": caller,
            "receiver": receiver,
            "call_type": normalized_call_type,
            "status": "Ringing",
            "start_time": now,
        }
    )
    call_doc.insert(ignore_permissions=True)
    frappe.db.commit()

    payload = _serialize_call_log(call_doc, caller)
    _publish_call_event("call_initiated", payload, receiver, caller)
    return payload


@frappe.whitelist()
def accept_call(call_id):
    call_doc = _get_call_log_for_user(call_id)
    accepted_by = frappe.session.user

    if call_doc.status not in ACTIVE_CALL_STATUSES:
        frappe.throw(_("This call is no longer active."))

    call_doc.status = "Ongoing"
    call_doc.start_time = now_datetime()

    _save_call_log(call_doc)

    payload = _serialize_call_log(call_doc)
    payload["accepted_by"] = accepted_by
    _publish_call_event("call_accepted", payload, call_doc.caller, call_doc.receiver)
    return payload


@frappe.whitelist()
def reject_call(call_id):
    call_doc = _get_call_log_for_user(call_id)
    rejected_by = frappe.session.user
    call_doc.status = "Rejected"
    call_doc.end_time = now_datetime()
    call_doc.duration = "00:00"

    _save_call_log(call_doc)

    payload = _serialize_call_log(call_doc)
    payload["rejected_by"] = rejected_by
    _publish_call_event("call_rejected", payload, call_doc.caller, call_doc.receiver)
    return payload


@frappe.whitelist()
def end_call(call_id):
    call_doc = _get_call_log_for_user(call_id)
    ended_by = frappe.session.user
    now = now_datetime()

    if call_doc.status == "Ringing":
        call_doc.status = "Missed"
        call_doc.duration = "00:00"
    else:
        call_doc.status = "Completed"
        if call_doc.start_time:
            seconds = max(int(time_diff_in_seconds(now, call_doc.start_time)), 0)
            call_doc.duration = format_duration(seconds)

    call_doc.end_time = now
    _save_call_log(call_doc)

    payload = _serialize_call_log(call_doc)
    payload["ended_by"] = ended_by
    _publish_call_event("call_ended", payload, call_doc.caller, call_doc.receiver)
    return payload


@frappe.whitelist()
def timeout_call(call_id):
    call_doc = _get_call_log_for_user(call_id)

    if call_doc.status != "Ringing":
        return _serialize_call_log(call_doc)

    call_doc.status = "Missed"
    call_doc.end_time = now_datetime()
    call_doc.duration = "00:00"
    _save_call_log(call_doc)

    payload = _serialize_call_log(call_doc)
    payload["reason"] = "timeout"
    _publish_call_event("call_ended", payload, call_doc.caller, call_doc.receiver)
    return payload


@frappe.whitelist()
def relay_call_signal(call_id, receiver, signal_type, payload=None):
    call_doc = _get_call_log_for_user(call_id)
    sender = frappe.session.user

    if receiver not in {call_doc.caller, call_doc.receiver}:
        frappe.throw(_("Receiver is not part of this call."))

    if sender == receiver:
        frappe.throw(_("Receiver must be the other participant."))

    message = {
        "call_id": call_id,
        "from": sender,
        "to": receiver,
        "signal_type": signal_type,
        "payload": payload or {},
        "call_type": call_doc.call_type,
    }
    _publish_call_event("call_signal", message, receiver)
    return {"ok": True}


@frappe.whitelist()
def get_call_logs(other_user=None, limit=10):
    current_user = frappe.session.user
    limit = max(min(frappe.utils.cint(limit or 10), 50), 1)

    conditions = ["(caller = %(current_user)s OR receiver = %(current_user)s)"]
    values = {"current_user": current_user, "limit": limit}

    if other_user:
        conditions.append("(caller = %(other_user)s OR receiver = %(other_user)s)")
        values["other_user"] = other_user

    where_clause = " AND ".join(conditions)

    call_logs = frappe.db.sql(
        f"""
        SELECT name
        FROM `tabCall Log`
        WHERE {where_clause}
        ORDER BY modified DESC
        LIMIT %(limit)s
        """,
        values,
        as_dict=True,
    )

    serialized = []
    for row in call_logs:
        serialized.append(_serialize_call_log(frappe.get_doc("Call Log", row.name), current_user))

    summary_row = frappe.db.sql(
        f"""
        SELECT
            COUNT(*) AS call_count,
            SUM(
                CASE
                    WHEN status = 'Missed' AND receiver = %(current_user)s THEN 1
                    ELSE 0
                END
            ) AS missed_calls
        FROM `tabCall Log`
        WHERE {where_clause}
        """,
        values,
        as_dict=True,
    )[0]

    summary = {
        "call_count": summary_row.call_count or 0,
        "missed_calls": summary_row.missed_calls or 0,
    }

    return {"logs": serialized, "summary": summary}
