import json
import mimetypes

import frappe
from frappe import _
from frappe.utils import add_days, add_to_date, format_duration, now_datetime, time_diff_in_seconds
from frappe.utils.file_manager import save_file


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

CHAT_MESSAGE_SCHEMA = "fun_chat_message"


def _guess_attachment_kind(file_name=None, mime_type=None):
    resolved_mime_type = (mime_type or mimetypes.guess_type(file_name or "")[0] or "").lower()

    if resolved_mime_type.startswith("image/"):
        return "image"
    if resolved_mime_type.startswith("video/"):
        return "video"
    if resolved_mime_type.startswith("audio/"):
        return "audio"
    return "file"


def _normalize_chat_attachment(attachment):
    parsed_attachment = frappe.parse_json(attachment) if isinstance(attachment, str) else attachment
    if not parsed_attachment:
        return None

    if not isinstance(parsed_attachment, dict):
        frappe.throw(_("Invalid attachment data."))

    file_url = str(parsed_attachment.get("file_url") or "").strip()
    if not file_url:
        frappe.throw(_("Uploaded file is missing."))

    file_doc = frappe.db.get_value(
        "File",
        {"file_url": file_url},
        ["file_name", "file_size", "file_url"],
        as_dict=True,
    )
    if not file_doc:
        frappe.throw(_("Uploaded file could not be found."))

    file_name = str(parsed_attachment.get("file_name") or file_doc.file_name or "").strip()
    mime_type = str(parsed_attachment.get("mime_type") or mimetypes.guess_type(file_name or file_url)[0] or "").strip()
    media_kind = str(parsed_attachment.get("media_kind") or _guess_attachment_kind(file_name, mime_type)).strip().lower()
    if media_kind not in {"image", "video", "audio", "file"}:
        media_kind = _guess_attachment_kind(file_name, mime_type)

    return {
        "file_name": file_name or file_url.rsplit("/", 1)[-1],
        "file_size": int(parsed_attachment.get("file_size") or file_doc.file_size or 0),
        "file_url": file_doc.file_url,
        "media_kind": media_kind,
        "mime_type": mime_type,
    }


def _normalize_chat_message_meta(metadata=None):
    parsed_meta = frappe.parse_json(metadata) if isinstance(metadata, str) else metadata
    if not parsed_meta:
        return {}

    if not isinstance(parsed_meta, dict):
        frappe.throw(_("Invalid message metadata."))

    deleted_for = []
    for user in parsed_meta.get("deleted_for") or []:
        normalized_user = str(user or "").strip()
        if normalized_user and normalized_user not in deleted_for:
            deleted_for.append(normalized_user)

    normalized = {}
    if deleted_for:
        normalized["deleted_for"] = deleted_for
    if parsed_meta.get("deleted_for_everyone"):
        normalized["deleted_for_everyone"] = True
    if parsed_meta.get("forwarded"):
        normalized["forwarded"] = True

    edited_at = str(parsed_meta.get("edited_at") or "").strip()
    if edited_at:
        normalized["edited_at"] = edited_at

    return normalized


def _serialize_chat_message_value(message=None, attachment=None, metadata=None, force_structured=False):
    normalized_message = str(message or "").strip()
    normalized_attachment = _normalize_chat_attachment(attachment)
    normalized_metadata = _normalize_chat_message_meta(metadata)

    if normalized_attachment or normalized_metadata or force_structured:
        payload = {
            "schema": CHAT_MESSAGE_SCHEMA,
            "text": normalized_message,
        }
        if normalized_attachment:
            payload["attachment"] = normalized_attachment
        if normalized_metadata:
            payload["meta"] = normalized_metadata
        return json.dumps(payload)

    return normalized_message


def _build_chat_preview_text(message=None, attachment=None, deleted_for_everyone=False):
    if deleted_for_everyone:
        return _("Message deleted")

    normalized_message = str(message or "").strip()
    if normalized_message:
        return normalized_message

    if not attachment:
        return ""

    if attachment["media_kind"] == "image":
        return _("Photo")
    if attachment["media_kind"] == "video":
        return _("Video")
    if attachment["media_kind"] == "audio":
        return _("Audio")
    return attachment.get("file_name") or _("File")


def _parse_chat_message_content(raw_message):
    raw_text = raw_message if isinstance(raw_message, str) else str(raw_message or "")
    message_text = raw_text
    attachment = None
    metadata = {}

    if raw_text:
        try:
            parsed_message = json.loads(raw_text)
        except (TypeError, ValueError):
            parsed_message = None

        if isinstance(parsed_message, dict) and parsed_message.get("schema") == CHAT_MESSAGE_SCHEMA:
            message_text = str(parsed_message.get("text") or "").strip()
            attachment = _normalize_chat_attachment(parsed_message.get("attachment"))
            metadata = _normalize_chat_message_meta(parsed_message.get("meta"))

    deleted_for_everyone = bool(metadata.get("deleted_for_everyone"))
    preview_text = _build_chat_preview_text(message_text, attachment, deleted_for_everyone=deleted_for_everyone)
    if deleted_for_everyone:
        message_type = "deleted"
    elif attachment and message_text:
        message_type = "mixed"
    elif attachment:
        message_type = "attachment"
    else:
        message_type = "text"

    return {
        "attachment": None if deleted_for_everyone else attachment,
        "deleted_for": metadata.get("deleted_for") or [],
        "deleted_for_everyone": deleted_for_everyone,
        "edited_at": metadata.get("edited_at") or "",
        "forwarded": bool(metadata.get("forwarded")),
        "message": "" if deleted_for_everyone else message_text,
        "message_type": message_type,
        "meta": metadata,
        "preview_text": preview_text,
    }


def _is_chat_message_visible_to_user(parsed_content, user):
    return user not in set(parsed_content.get("deleted_for") or [])


def _build_chat_message_payload(conversation, row):
    parsed_content = _parse_chat_message_content(row.message)
    receiver = conversation.user_1 if row.sender == conversation.user_2 else conversation.user_2

    return {
        "attachment": parsed_content["attachment"],
        "conversation_name": conversation.name,
        "deleted_for_everyone": parsed_content["deleted_for_everyone"],
        "edited": bool(parsed_content["edited_at"]),
        "edited_at": parsed_content["edited_at"],
        "forwarded": parsed_content["forwarded"],
        "id": row.name,
        "message": parsed_content["message"],
        "message_type": parsed_content["message_type"],
        "preview_text": parsed_content["preview_text"],
        "reactions": frappe.parse_json(getattr(row, "reactions", None) or "{}"),
        "receiver": receiver,
        "sender": row.sender,
        "start_date": str(conversation.start_date),
        "timestamp": str(row.timestamp) if row.timestamp else "",
    }


def _get_chat_message_context(message_id):
    current_user = frappe.session.user
    message_name = str(message_id or "").strip()
    if not message_name:
        frappe.throw(_("Message is required."))

    message_entry = frappe.db.get_value("Chat Message", message_name, ["parent"], as_dict=True)
    if not message_entry:
        frappe.throw(_("Message not found."))

    conversation = frappe.get_doc("Conversation", message_entry.parent)
    participants = {conversation.user_1, conversation.user_2}
    if current_user not in participants:
        frappe.throw(_("You are not allowed to update this message."))

    row = next((entry for entry in conversation.messages if entry.name == message_name), None)
    if not row:
        frappe.throw(_("Message not found."))

    return conversation, row, participants


def _publish_chat_message_update(conversation, row, participants):
    payload = _build_chat_message_payload(conversation, row)

    for participant in participants:
        frappe.publish_realtime(
            "realtime",
            {
                "data": payload,
                "event": "chat_message_updated",
            },
            user=participant,
        )

    return payload


def _store_chat_message(sender, receiver, message=None, attachment=None, metadata=None):
    now = now_datetime()
    today = now.date()
    stored_message = _serialize_chat_message_value(
        message=message,
        attachment=attachment,
        metadata=metadata,
    )
    parsed_content = _parse_chat_message_content(stored_message)

    if not parsed_content["message"] and not parsed_content["attachment"]:
        frappe.throw(_("Message or attachment is required."))

    u1, u2 = sorted([sender, receiver])
    cutoff = add_days(today, -2)

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
        "message": stored_message,
        "timestamp": now,
    })

    if conv.is_new():
        conv.insert(ignore_permissions=True)
    else:
        conv.save(ignore_permissions=True)

    frappe.db.commit()

    row = conv.messages[-1]
    payload = _build_chat_message_payload(conv, row)

    frappe.publish_realtime("new_message", payload, user=receiver)
    frappe.publish_realtime("new_message", payload, user=sender)

    return payload


@frappe.whitelist()
def upload_chat_file():
    uploaded_file = frappe.request.files.get("file")
    if not uploaded_file:
        frappe.throw(_("Please choose a file to upload."))

    file_name = getattr(uploaded_file, "filename", None) or getattr(uploaded_file, "name", None) or "attachment"
    content = uploaded_file.stream.read() if getattr(uploaded_file, "stream", None) else uploaded_file.read()
    if not content:
        frappe.throw(_("Uploaded file is empty."))

    file_doc = save_file(file_name, content, None, None, is_private=0)
    mime_type = getattr(uploaded_file, "content_type", None) or mimetypes.guess_type(file_doc.file_name or file_name)[0] or ""

    return {
        "file_name": file_doc.file_name,
        "file_size": file_doc.file_size,
        "file_url": file_doc.file_url,
        "media_kind": _guess_attachment_kind(file_doc.file_name, mime_type),
        "mime_type": mime_type,
    }

@frappe.whitelist()
def send_message(receiver, message=None, attachment=None):
    sender = frappe.session.user
    return _store_chat_message(sender, receiver, message=message, attachment=attachment)


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
            parsed_content = _parse_chat_message_content(msg.message)
            if not _is_chat_message_visible_to_user(parsed_content, current_user):
                continue
            messages.append(_build_chat_message_payload(doc, msg))
        # Sort messages by timestamp ascending
        messages.sort(key=lambda m: m["timestamp"])
        if not messages:
            continue
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

        doc = frappe.get_doc("Conversation", conv.name)
        visible_messages = []
        for msg in doc.messages:
            parsed_content = _parse_chat_message_content(msg.message)
            if not _is_chat_message_visible_to_user(parsed_content, current_user):
                continue
            visible_messages.append(_build_chat_message_payload(doc, msg))
        visible_messages.sort(key=lambda row: row["timestamp"], reverse=True)
        last_msg = visible_messages[0] if visible_messages else None

        user_info = frappe.db.get_value(
            "User", peer, ["full_name", "first_name", "user_image"], as_dict=True
        ) or {}

        result.append({
            "peer": peer,
            "full_name": user_info.get("full_name") or user_info.get("first_name") or peer,
            "user_image": user_info.get("user_image"),
            "last_message": last_msg["preview_text"] if last_msg else "",
            "timestamp": last_msg["timestamp"] if last_msg else "",
        })

    return result


@frappe.whitelist()
def edit_message(message_id, message=None):
    current_user = frappe.session.user
    conversation, row, participants = _get_chat_message_context(message_id)

    if row.sender != current_user:
        frappe.throw(_("Only your own messages can be edited."))

    parsed_content = _parse_chat_message_content(row.message)
    if parsed_content["deleted_for_everyone"]:
        frappe.throw(_("Deleted messages cannot be edited."))

    next_message = str(message or "").strip()
    if not next_message and not parsed_content["attachment"]:
        frappe.throw(_("Message cannot be empty."))

    metadata = {
        **parsed_content["meta"],
        "edited_at": str(now_datetime()),
    }
    row.message = _serialize_chat_message_value(
        message=next_message,
        attachment=parsed_content["attachment"],
        metadata=metadata,
        force_structured=True,
    )

    conversation.save(ignore_permissions=True)
    frappe.db.commit()

    return _publish_chat_message_update(conversation, row, participants)


@frappe.whitelist()
def delete_message_for_me(message_id):
    current_user = frappe.session.user
    conversation, row, _participants = _get_chat_message_context(message_id)
    parsed_content = _parse_chat_message_content(row.message)

    deleted_for = list(parsed_content["meta"].get("deleted_for") or [])
    if current_user not in deleted_for:
        deleted_for.append(current_user)

    metadata = {
        **parsed_content["meta"],
        "deleted_for": deleted_for,
    }
    row.message = _serialize_chat_message_value(
        message=parsed_content["message"],
        attachment=parsed_content["attachment"],
        metadata=metadata,
        force_structured=True,
    )

    conversation.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "message_id": row.name,
        "status": "ok",
    }


@frappe.whitelist()
def delete_message_for_everyone(message_id):
    current_user = frappe.session.user
    conversation, row, participants = _get_chat_message_context(message_id)

    if row.sender != current_user:
        frappe.throw(_("Only your own messages can be deleted for everyone."))

    parsed_content = _parse_chat_message_content(row.message)
    metadata = {
        **parsed_content["meta"],
        "deleted_for_everyone": True,
    }
    row.message = _serialize_chat_message_value(
        message="",
        attachment=None,
        metadata=metadata,
        force_structured=True,
    )

    conversation.save(ignore_permissions=True)
    frappe.db.commit()

    return _publish_chat_message_update(conversation, row, participants)


@frappe.whitelist()
def forward_message(message_id, receiver):
    current_user = frappe.session.user
    conversation, row, _participants = _get_chat_message_context(message_id)
    parsed_content = _parse_chat_message_content(row.message)

    if not _is_chat_message_visible_to_user(parsed_content, current_user):
        frappe.throw(_("This message is no longer available."))
    if parsed_content["deleted_for_everyone"]:
        frappe.throw(_("Deleted messages cannot be forwarded."))

    normalized_receiver = str(receiver or "").strip()
    if not normalized_receiver:
        frappe.throw(_("Please choose a user to forward this message to."))

    if normalized_receiver == "Guest":
        frappe.throw(_("Invalid recipient."))

    if not frappe.db.exists("User", normalized_receiver):
        frappe.throw(_("Recipient not found."))

    return _store_chat_message(
        current_user,
        normalized_receiver,
        message=parsed_content["message"],
        attachment=parsed_content["attachment"],
        metadata={"forwarded": True},
    )


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


def _get_call_log_filters(current_user=None, other_user=None):
    current_user = current_user or frappe.session.user
    conditions = ["(caller = %(current_user)s OR receiver = %(current_user)s)"]
    values = {"current_user": current_user}

    if other_user:
        conditions.append("(caller = %(other_user)s OR receiver = %(other_user)s)")
        values["other_user"] = other_user

    return " AND ".join(conditions), values


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
def delete_call_log(call_id):
    call_doc = _get_call_log_for_user(call_id)

    if call_doc.status in ACTIVE_CALL_STATUSES:
        frappe.throw(_("Active calls cannot be deleted."))

    payload = {"call_id": call_doc.call_id, "name": call_doc.name}
    participants = [call_doc.caller, call_doc.receiver]

    frappe.delete_doc("Call Log", call_doc.name, ignore_permissions=True)
    frappe.db.commit()

    _publish_call_event("call_log_deleted", payload, *participants)
    return {"ok": True, **payload}


def _parse_call_ids(call_ids):
    parsed_call_ids = frappe.parse_json(call_ids) if isinstance(call_ids, str) else call_ids

    if parsed_call_ids is None:
        return []

    if not isinstance(parsed_call_ids, (list, tuple, set)):
        frappe.throw(_("Please select valid call logs."))

    normalized_call_ids = []
    for value in parsed_call_ids:
        call_id = str(value or "").strip()
        if call_id and call_id not in normalized_call_ids:
            normalized_call_ids.append(call_id)

    return normalized_call_ids


def _delete_call_log_rows(rows):
    deleted_call_ids = []
    skipped_active_call_ids = []
    participants = set()

    for row in rows:
        if row.status in ACTIVE_CALL_STATUSES:
            skipped_active_call_ids.append(row.call_id)
            continue

        participants.update({row.caller, row.receiver})
        frappe.delete_doc("Call Log", row.name, ignore_permissions=True)
        deleted_call_ids.append(row.call_id)

    frappe.db.commit()

    payload = {
        "deleted_call_ids": deleted_call_ids,
        "deleted_count": len(deleted_call_ids),
        "skipped_active_call_ids": skipped_active_call_ids,
        "skipped_active_count": len(skipped_active_call_ids),
    }

    if deleted_call_ids:
        _publish_call_event("call_logs_cleared", payload, *participants)

    return payload


@frappe.whitelist()
def delete_selected_call_logs(call_ids):
    normalized_call_ids = _parse_call_ids(call_ids)

    if not normalized_call_ids:
        return {
            "ok": True,
            "deleted_call_ids": [],
            "deleted_count": 0,
            "skipped_active_call_ids": [],
            "skipped_active_count": 0,
        }

    placeholders = ", ".join(["%s"] * len(normalized_call_ids))
    rows = frappe.db.sql(
        f"""
        SELECT name, call_id, caller, receiver, status
        FROM `tabCall Log`
        WHERE (caller = %s OR receiver = %s)
          AND call_id IN ({placeholders})
        ORDER BY modified DESC
        """,
        [frappe.session.user, frappe.session.user, *normalized_call_ids],
        as_dict=True,
    )

    return {"ok": True, **_delete_call_log_rows(rows)}


@frappe.whitelist()
def clear_call_logs(other_user=None):
    current_user = frappe.session.user
    where_clause, values = _get_call_log_filters(current_user=current_user, other_user=other_user)

    rows = frappe.db.sql(
        f"""
        SELECT name, call_id, caller, receiver, status
        FROM `tabCall Log`
        WHERE {where_clause}
        ORDER BY modified DESC
        """,
        values,
        as_dict=True,
    )

    return {"ok": True, **_delete_call_log_rows(rows)}


@frappe.whitelist()
def get_call_logs(other_user=None, limit=10):
    current_user = frappe.session.user
    limit = max(min(frappe.utils.cint(limit or 10), 50), 1)
    where_clause, values = _get_call_log_filters(current_user=current_user, other_user=other_user)
    values["limit"] = limit

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


# ─── Status ───────────────────────────────────────────────────────────────────

def _serialize_status(doc, current_user):
    """Convert a User Status doc to a plain serializable dict."""
    owner_name = frappe.db.get_value("User", doc.owner, "full_name") or doc.owner
    owner_image = frappe.db.get_value("User", doc.owner, "user_image") or ""
    reactions = frappe.parse_json(doc.reactions or "{}")
    seen_by = frappe.parse_json(doc.seen_by or "[]")
    comments = [
        {
            "commenter": row.commenter,
            "commenter_name": frappe.db.get_value("User", row.commenter, "full_name") or row.commenter,
            "text": row.text,
            "timestamp": str(row.timestamp),
        }
        for row in (doc.comments or [])
    ]
    return {
        "name": doc.name,
        "owner": doc.owner,
        "owner_name": owner_name,
        "owner_image": owner_image,
        "file_url": doc.file_url,
        "media_kind": doc.media_kind,
        "mime_type": doc.mime_type or "",
        "caption": doc.caption or "",
        "caption_color": getattr(doc, "caption_color", None) or "#ffffff",
        "caption_size": getattr(doc, "caption_size", None) or "medium",
        "bg_music_url": getattr(doc, "bg_music_url", None) or "",
        "expires_at": str(doc.expires_at),
        "creation": str(doc.creation),
        "reactions": reactions,
        "seen_by": seen_by,
        "comments": comments,
        "is_mine": doc.owner == current_user,
    }


@frappe.whitelist()
def post_status(file_url, media_kind, mime_type=None, caption=None, caption_color=None, caption_size=None, bg_music_url=None):
    """Create a new status post (photo or video, expires in 24h)."""
    if not file_url:
        frappe.throw(_("File URL is required."))
    if media_kind not in ("image", "video"):
        frappe.throw(_("media_kind must be 'image' or 'video'."))

    current_user = frappe.session.user
    expires_at = add_to_date(now_datetime(), hours=24)

    doc = frappe.get_doc({
        "doctype": "User Status",
        "file_url": file_url,
        "media_kind": media_kind,
        "mime_type": mime_type or "",
        "caption": caption or "",
        "caption_color": caption_color or "#ffffff",
        "caption_size": caption_size or "medium",
        "bg_music_url": bg_music_url or "",
        "expires_at": expires_at,
        "reactions": "{}",
        "seen_by": "[]",
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    payload = _serialize_status(doc, current_user)

    # notify all other users in real-time
    other_users = frappe.get_all(
        "User",
        filters={"name": ["not in", [current_user, "Guest"]], "enabled": 1},
        fields=["name"],
    )
    for u in other_users:
        frappe.publish_realtime("new_status", payload, user=u.name)

    return payload


@frappe.whitelist()
def get_statuses():
    """Return all active (non-expired) statuses grouped by owner."""
    current_user = frappe.session.user
    now = now_datetime()

    rows = frappe.get_all(
        "User Status",
        filters=[["expires_at", ">", now]],
        fields=["name"],
        order_by="creation asc",
    )

    groups = {}  # owner -> group dict
    for row in rows:
        doc = frappe.get_doc("User Status", row.name)
        s = _serialize_status(doc, current_user)
        owner = s["owner"]
        if owner not in groups:
            groups[owner] = {
                "owner": owner,
                "owner_name": s["owner_name"],
                "owner_image": s["owner_image"],
                "is_mine": s["is_mine"],
                "statuses": [],
            }
        groups[owner]["statuses"].append(s)

    result = list(groups.values())

    # compute all_seen per group
    for g in result:
        g["all_seen"] = all(
            current_user in s["seen_by"] or s["is_mine"]
            for s in g["statuses"]
        )

    # sort: own group first, then unseen, then seen
    def sort_key(g):
        if g["is_mine"]:
            return 0
        if not g["all_seen"]:
            return 1
        return 2

    result.sort(key=sort_key)
    return result


@frappe.whitelist()
def mark_status_seen(status_name):
    """Mark a status as seen by the current user."""
    current_user = frappe.session.user
    try:
        doc = frappe.get_doc("User Status", status_name)
    except frappe.DoesNotExistError:
        return {"ok": False}

    seen_by = frappe.parse_json(doc.seen_by or "[]")
    if current_user not in seen_by:
        seen_by.append(current_user)
        doc.seen_by = frappe.as_json(seen_by)
        doc.save(ignore_permissions=True)
        frappe.db.commit()

    return {"ok": True, "seen_by": seen_by}


@frappe.whitelist()
def react_to_status(status_name, emoji):
    """Add or remove an emoji reaction on a status."""
    current_user = frappe.session.user
    doc = frappe.get_doc("User Status", status_name)

    reactions = frappe.parse_json(doc.reactions or "{}")

    if not emoji:
        # remove reaction
        reactions.pop(current_user, None)
    else:
        reactions[current_user] = emoji

    doc.reactions = frappe.as_json(reactions)
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    frappe.publish_realtime(
        "status_reacted",
        {"status_name": status_name, "reactions": reactions},
        user=doc.owner,
    )

    # Send chat message to status owner when adding (not removing) a reaction
    if emoji and current_user != doc.owner:
        try:
            reactor_name = frappe.db.get_value("User", current_user, "full_name") or current_user
            chat_text = f"{emoji} {reactor_name} reacted to your status"
            _store_chat_message(current_user, doc.owner, message=chat_text)
        except Exception:
            pass

    return {"ok": True, "reactions": reactions}


@frappe.whitelist()
def comment_on_status(status_name, text):
    """Add a text comment to a status."""
    if not text or not text.strip():
        frappe.throw(_("Comment text cannot be empty."))

    current_user = frappe.session.user
    doc = frappe.get_doc("User Status", status_name)

    row = doc.append("comments", {
        "commenter": current_user,
        "text": text.strip(),
        "timestamp": now_datetime(),
    })
    doc.save(ignore_permissions=True)
    frappe.db.commit()

    comment = {
        "commenter": current_user,
        "commenter_name": frappe.db.get_value("User", current_user, "full_name") or current_user,
        "text": row.text,
        "timestamp": str(row.timestamp),
    }

    frappe.publish_realtime(
        "status_commented",
        {"status_name": status_name, "comment": comment},
        user=doc.owner,
    )

    # Also send as a chat message to the status owner (if commenter != owner)
    if current_user != doc.owner:
        try:
            chat_text = f"💬 {text.strip()}"
            _store_chat_message(current_user, doc.owner, message=chat_text)
        except Exception:
            pass

    return comment


@frappe.whitelist()
def delete_status(status_name):
    """Delete own status and notify all users."""
    current_user = frappe.session.user
    doc = frappe.get_doc("User Status", status_name)

    if doc.owner != current_user:
        frappe.throw(_("You can only delete your own statuses."))

    frappe.delete_doc("User Status", status_name, ignore_permissions=True)
    frappe.db.commit()

    all_users = frappe.get_all(
        "User",
        filters={"name": ["not in", ["Guest"]], "enabled": 1},
        fields=["name"],
    )
    for u in all_users:
        frappe.publish_realtime(
            "status_deleted",
            {"status_name": status_name},
            user=u.name,
        )

    return {"ok": True, "status_name": status_name}


# ─── Chat Message Reactions ───────────────────────────────────────────────────

@frappe.whitelist()
def react_to_message(message_id, emoji):
    """Add or remove an emoji reaction on a chat message."""
    current_user = frappe.session.user
    message_name = str(message_id or "").strip()
    if not message_name:
        frappe.throw(_("Message ID is required."))

    msg_row = frappe.db.get_value("Chat Message", message_name, ["parent", "sender"], as_dict=True)
    if not msg_row:
        frappe.throw(_("Message not found."))

    conversation = frappe.get_doc("Conversation", msg_row.parent)
    participants = {conversation.user_1, conversation.user_2}
    if current_user not in participants:
        frappe.throw(_("Not allowed."))

    reactions = frappe.parse_json(
        frappe.db.get_value("Chat Message", message_name, "reactions") or "{}"
    )
    emoji = str(emoji or "").strip()
    if emoji:
        reactions[current_user] = emoji
    else:
        reactions.pop(current_user, None)

    frappe.db.set_value("Chat Message", message_name, "reactions", frappe.as_json(reactions), update_modified=False)
    frappe.db.commit()

    payload = {
        "event": "message_reacted",
        "data": {
            "message_id": message_name,
            "reactions": reactions,
            "sender": conversation.user_1,
            "receiver": conversation.user_2,
        },
    }
    for user in participants:
        frappe.publish_realtime("realtime", payload, user=user)

    return {"ok": True, "reactions": reactions}
