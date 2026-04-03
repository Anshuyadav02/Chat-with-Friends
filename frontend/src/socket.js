import { io } from "socket.io-client"
import { socketio_port, webserver_port } from "../../../../sites/common_site_config.json"

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
		const currentPort = url.port || (url.protocol === "https:" ? "443" : "80")
		const configuredSocketPort = String(window.frappe?.boot?.socketio_port || socketio_port)
		const configuredWebPort = String(window.webserver_port || webserver_port || "")
		const isLocalHost =
			["localhost", "127.0.0.1"].includes(window.location.hostname) ||
			window.location.hostname.endsWith(".localhost")
		const shouldUseSocketPort =
			window.dev_server || isLocalHost || (configuredWebPort && currentPort === configuredWebPort)

		if (shouldUseSocketPort) {
			url.port = configuredSocketPort
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
		autoConnect: false,
	})

	socket.on('realtime', (data) => {
		if (!data?.event) return
		console.debug('[socket] realtime wrapper', data.event, data.message)
		dispatchRealtimeEvent(data.event, data.message)
	})

	socket.on('connect', () => {
		console.log('[socket] ✅ connected', { id: socket.id, siteName, url })
	})

	socket.on('connect_error', (error) => {
		console.error('[socket] ❌ connect_error', error)
	})

	socket.on('disconnect', (reason) => {
		console.warn('[socket] disconnected', reason)
	})

	socket.onAny((event, ...args) => {
		if (event === 'realtime') return
		console.log('[socket] incoming event:', event, ...args)
	})

	return socket
}

export function connectSocket() {
	const currentSocket = initSocket()
	if (!currentSocket.connected) {
		currentSocket.connect()
	}
	return currentSocket
}

export function disconnectSocket() {
	if (!socket) return
	socket.disconnect()
}

export function useSocket() {
	return socket
}
