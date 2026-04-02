import { io } from "socket.io-client"
import { socketio_port } from "../../../../sites/common_site_config.json"

let socket = null

function dispatchRealtimeEvent(eventName, payload) {
	if (!socket || !eventName) return

	if (typeof socket.emitEvent === "function") {
		socket.emitEvent([eventName, payload])
		return
	}

	const callbacks = socket._callbacks?.[`$${eventName}`] || []
	for (const callback of callbacks) {
		callback(payload)
	}
}

function getSiteName() {
	return (
		window.sitename ||
		window.site_name ||
		window.frappe?.boot?.sitename ||
		window.location.hostname
	)
}

function getSocketHost() {
	try {
		const url = new URL(window.location.origin)
		if (window.dev_server || ["localhost", "127.0.0.1"].includes(window.location.hostname)) {
			url.port = String(window.frappe?.boot?.socketio_port || socketio_port)
		}
		return url.toString().replace(/\/$/, "")
	} catch {
		return window.location.origin
	}
}

export function initSocket() {
	if (socket) return socket

	const siteName = getSiteName()
	const host = getSocketHost()
	const url = `${host}/${siteName}`

	socket = io(url, {
		withCredentials: true,
		reconnectionAttempts: 5,
		transports: ["websocket", "polling"],
	})

	socket.on('realtime', (data) => {
		if (!data?.event) return
		console.debug('[socket] realtime wrapper', data.event, data.data)
		dispatchRealtimeEvent(data.event, data.data)
	})

	socket.on('connect', () => {
		console.debug('[socket] connected', { id: socket.id, siteName, url })
	})

	socket.on('connect_error', (error) => {
		console.error('[socket] connect_error', error)
	})

	socket.on('disconnect', (reason) => {
		console.warn('[socket] disconnected', reason)
	})

	socket.onAny((event, ...args) => {
		if (event === 'realtime') return
		console.debug('[socket] incoming', event, ...args)
	})

	return socket
}

export function useSocket() {
	return socket
}
