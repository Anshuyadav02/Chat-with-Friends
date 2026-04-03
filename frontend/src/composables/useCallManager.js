import { computed, onUnmounted, ref } from 'vue'
import { frappeRequest } from 'frappe-ui'

import { session } from '@/data/session'
import { useSocket } from '@/socket'

const CALL_TIMEOUT_MS = 30000
const RTC_CONFIGURATION = {
  iceServers: [{ urls: ['stun:stun.l.google.com:19302'] }],
}

function createDefaultMediaState() {
  return {
    muted: false,
    speakerOn: true,
    cameraOn: true,
    screenSharing: false,
  }
}

export function useCallManager(options = {}) {
  const socket = useSocket()
  const activeCall = ref(null)
  const incomingCall = ref(null)
  const callStatus = ref('idle')
  const localStream = ref(null)
  const remoteStream = ref(null)
  const mediaState = ref(createDefaultMediaState())
  const callLogs = ref([])
  const callSummary = ref({ call_count: 0, missed_calls: 0 })
  const callSeconds = ref(0)

  const peerConnection = ref(null)
  const pendingIceCandidates = ref([])
  const remoteAudio = typeof Audio !== 'undefined' ? new Audio() : null

  let callTimer = null
  let unansweredTimer = null
  let ringtoneContext = null
  let toneInterval = null
  let toneTimeout = null

  if (remoteAudio) {
    remoteAudio.autoplay = true
  }

  const currentCall = computed(() => activeCall.value || incomingCall.value)
  const isInCall = computed(() => Boolean(activeCall.value || incomingCall.value))
  const isVideoCall = computed(() => currentCall.value?.callType === 'video')
  const durationText = computed(() => {
    const minutes = String(Math.floor(callSeconds.value / 60)).padStart(2, '0')
    const seconds = String(callSeconds.value % 60).padStart(2, '0')
    return `${minutes}:${seconds}`
  })

  function resolveUser(userId) {
    const resolved = options.resolveUser?.(userId)
    if (resolved) return resolved
    return {
      name: userId,
      full_name: userId,
    }
  }

  function buildCall(payload, direction) {
    const remoteUser = payload.caller === session.user ? payload.receiver : payload.caller
    const remote = resolveUser(remoteUser)

    return {
      callId: payload.call_id,
      remoteUser,
      remoteName: remote.full_name || remote.first_name || remote.name || remoteUser,
      callerName: resolveUser(payload.caller)?.full_name || payload.caller,
      callType: (payload.call_type || 'Audio').toLowerCase(),
      direction,
    }
  }

  async function request(method, params = {}) {
    return frappeRequest({
      url: `fun.api.${method}`,
      params,
    })
  }

  function startCallTimer() {
    stopCallTimer()
    callTimer = window.setInterval(() => {
      callSeconds.value += 1
    }, 1000)
  }

  function stopCallTimer() {
    if (callTimer) {
      window.clearInterval(callTimer)
      callTimer = null
    }
  }

  function clearUnansweredTimer() {
    if (unansweredTimer) {
      window.clearTimeout(unansweredTimer)
      unansweredTimer = null
    }
  }

  function scheduleUnansweredTimeout(callId) {
    clearUnansweredTimer()
    unansweredTimer = window.setTimeout(async () => {
      if (activeCall.value?.callId !== callId || callStatus.value !== 'ringing') return
      await request('timeout_call', { call_id: callId }).catch(() => null)
      resetCallState()
      options.onCallStateChange?.()
    }, CALL_TIMEOUT_MS)
  }

  async function ensureLocalStream(callType) {
    const wantsVideo = callType === 'video'
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: true,
      video: wantsVideo ? { facingMode: 'user' } : false,
    })

    stopTracks(localStream.value)
    localStream.value = stream
    mediaState.value = {
      ...createDefaultMediaState(),
      cameraOn: wantsVideo,
    }
    syncRemoteAudio()
  }

  async function createPeerConnection(call) {
    closePeerConnection()

    const peer = new RTCPeerConnection(RTC_CONFIGURATION)
    pendingIceCandidates.value = []

    if (localStream.value) {
      for (const track of localStream.value.getTracks()) {
        peer.addTrack(track, localStream.value)
      }
    }

    peer.onicecandidate = event => {
      if (!event.candidate || !activeCall.value) return
      request('relay_call_signal', {
        call_id: activeCall.value.callId,
        receiver: activeCall.value.remoteUser,
        signal_type: 'ice',
        payload: { candidate: event.candidate.toJSON() },
      }).catch(() => null)
    }

    peer.ontrack = event => {
      remoteStream.value = event.streams[0]
      syncRemoteAudio()
    }

    peer.onconnectionstatechange = () => {
      if (!peerConnection.value) return

      if (peer.connectionState === 'connected') {
        callStatus.value = 'connected'
        callSeconds.value = 0
        startCallTimer()
        clearUnansweredTimer()
        stopTone()
        syncRemoteAudio()
        options.onCallStateChange?.()
      }

      if (['failed', 'disconnected', 'closed'].includes(peer.connectionState)) {
        resetCallState()
        options.onCallStateChange?.()
      }
    }

    peerConnection.value = peer
    return peer
  }

  async function flushPendingIce() {
    if (!peerConnection.value?.remoteDescription) return

    const queue = [...pendingIceCandidates.value]
    pendingIceCandidates.value = []
    for (const candidate of queue) {
      await peerConnection.value.addIceCandidate(candidate)
    }
  }

  function closePeerConnection() {
    if (peerConnection.value) {
      peerConnection.value.onicecandidate = null
      peerConnection.value.ontrack = null
      peerConnection.value.onconnectionstatechange = null
      peerConnection.value.close()
      peerConnection.value = null
    }
  }

  function syncRemoteAudio() {
    if (!remoteAudio) return
    remoteAudio.srcObject = remoteStream.value || null
    remoteAudio.muted = !mediaState.value.speakerOn || activeCall.value?.callType === 'video'
  }

  function stopTracks(stream) {
    if (!stream) return
    for (const track of stream.getTracks()) {
      track.stop()
    }
  }

  function cleanupMedia() {
    stopTracks(localStream.value)
    localStream.value = null
    remoteStream.value = null
    pendingIceCandidates.value = []
    closePeerConnection()
    if (remoteAudio) {
      remoteAudio.pause()
      remoteAudio.srcObject = null
    }
    mediaState.value = createDefaultMediaState()
  }

  function resetCallState() {
    stopTone()
    stopCallTimer()
    clearUnansweredTimer()
    cleanupMedia()
    activeCall.value = null
    incomingCall.value = null
    callStatus.value = 'idle'
    callSeconds.value = 0
  }

  function ensureRingtoneContext() {
    if (!ringtoneContext) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext
      ringtoneContext = AudioContextClass ? new AudioContextClass() : null
    }
    return ringtoneContext
  }

  // Teams-style ringtone: ascending 4-note chime pattern
  // incoming: E5→G#5→B5→E6 soft chime, repeats every 3.2s
  // outgoing: C5→E5→G5 short pattern, repeats every 4s
  function playNote(context, frequency, startTime, duration, volume = 0.08) {
    const osc = context.createOscillator()
    const gain = context.createGain()

    osc.type = 'sine'
    osc.frequency.value = frequency

    // Smooth attack + decay envelope (Teams warm tone)
    gain.gain.setValueAtTime(0, startTime)
    gain.gain.linearRampToValueAtTime(volume, startTime + 0.03)
    gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration)

    osc.connect(gain)
    gain.connect(context.destination)
    osc.start(startTime)
    osc.stop(startTime + duration + 0.05)
  }

  function playTeamsChime(context, type) {
    const now = context.currentTime

    if (type === 'incoming') {
      // Teams incoming: E5 G#5 B5 E6 — ascending warm chime
      const notes = [659.25, 830.61, 987.77, 1318.51]
      const noteDuration = 0.38
      const gap = 0.12
      notes.forEach((freq, i) => {
        playNote(context, freq, now + i * (noteDuration - gap), noteDuration, 0.07)
      })
    } else {
      // Teams outgoing: C5 E5 G5 — short dialing pattern
      const notes = [523.25, 659.25, 783.99]
      const noteDuration = 0.28
      const gap = 0.08
      notes.forEach((freq, i) => {
        playNote(context, freq, now + i * (noteDuration - gap), noteDuration, 0.05)
      })
    }
  }

  function playTone(type = 'incoming') {
    stopTone()
    const context = ensureRingtoneContext()
    if (!context) return

    const repeatInterval = type === 'incoming' ? 3200 : 4000

    context.resume?.().catch(() => null)
    playTeamsChime(context, type)
    toneInterval = window.setInterval(() => {
      context.resume?.().catch(() => null)
      playTeamsChime(context, type)
    }, repeatInterval)
  }

  function stopTone() {
    if (toneInterval) {
      window.clearInterval(toneInterval)
      toneInterval = null
    }
    if (toneTimeout) {
      window.clearTimeout(toneTimeout)
      toneTimeout = null
    }
  }

  async function startCall(user, type) {
    if (!user?.name || isInCall.value) return

    const callType = type === 'video' ? 'Video' : 'Audio'

    try {
      const payload = await request('initiate_call', {
        receiver: user.name,
        call_type: callType,
      })

      activeCall.value = buildCall(payload, 'outgoing')
      callStatus.value = 'ringing'
      playTone('outgoing')

      try {
        await ensureLocalStream(activeCall.value.callType)
      } catch (mediaError) {
        console.warn('[call] media access failed, retrying with audio only', mediaError)
        await ensureLocalStream('audio')
      }

      scheduleUnansweredTimeout(activeCall.value.callId)
      options.onCallStateChange?.()
    } catch (error) {
      console.error('[call] startCall failed', error)
      resetCallState()
      options.onCallStateChange?.()
    }
  }

  async function acceptIncomingCall() {
    if (!incomingCall.value) return

    const acceptedCall = { ...incomingCall.value }
    stopTone()

    try {
      await ensureLocalStream(acceptedCall.callType)
    } catch (mediaError) {
      console.warn('[call] media access failed, retrying with audio only', mediaError)
      try {
        await ensureLocalStream('audio')
      } catch (audioError) {
        console.error('[call] audio access also failed', audioError)
        resetCallState()
        options.onCallStateChange?.()
        return
      }
    }

    activeCall.value = acceptedCall
    incomingCall.value = null
    callStatus.value = 'connecting'

    try {
      await createPeerConnection(acceptedCall)
      await request('accept_call', { call_id: acceptedCall.callId })
      options.onCallStateChange?.()
    } catch (error) {
      console.error('[call] accept failed', error)
      resetCallState()
      options.onCallStateChange?.()
    }
  }

  async function rejectIncomingCall() {
    if (!incomingCall.value) return
    const callId = incomingCall.value.callId
    stopTone()
    await request('reject_call', { call_id: callId }).catch(() => null)
    resetCallState()
    options.onCallStateChange?.()
  }

  async function endCurrentCall() {
    const callId = activeCall.value?.callId
    if (!callId) {
      resetCallState()
      return
    }

    await request('end_call', { call_id: callId }).catch(() => null)
    resetCallState()
    options.onCallStateChange?.()
  }

  async function handleCallAccepted(payload) {
    stopTone()
    clearUnansweredTimer()
    console.debug('[call] accepted event', payload)

    if (payload.accepted_by === session.user) return
    if (activeCall.value?.callId !== payload.call_id) return

    callStatus.value = 'connecting'
    await ensureLocalStream(activeCall.value.callType)
    const peer = await createPeerConnection(activeCall.value)
    const offer = await peer.createOffer()
    await peer.setLocalDescription(offer)
    await request('relay_call_signal', {
      call_id: activeCall.value.callId,
      receiver: activeCall.value.remoteUser,
      signal_type: 'offer',
      payload: { offer },
    })
  }

  async function handleSignal(message) {
    console.debug('[call] signal', message)
    const knownCall =
      activeCall.value?.callId === message.call_id
        ? activeCall.value
        : incomingCall.value?.callId === message.call_id
          ? incomingCall.value
          : null

    if (!knownCall || message.from === session.user) return

    if (!peerConnection.value && activeCall.value?.callId === message.call_id) {
      await createPeerConnection(activeCall.value)
    }

    if (!peerConnection.value) return

    if (message.signal_type === 'offer') {
      await peerConnection.value.setRemoteDescription(
        new RTCSessionDescription(message.payload.offer)
      )
      await flushPendingIce()
      const answer = await peerConnection.value.createAnswer()
      await peerConnection.value.setLocalDescription(answer)
      await request('relay_call_signal', {
        call_id: knownCall.callId,
        receiver: knownCall.remoteUser,
        signal_type: 'answer',
        payload: { answer },
      })
      callStatus.value = 'connecting'
      return
    }

    if (message.signal_type === 'answer') {
      await peerConnection.value.setRemoteDescription(
        new RTCSessionDescription(message.payload.answer)
      )
      await flushPendingIce()
      return
    }

    if (message.signal_type === 'ice' && message.payload?.candidate) {
      const candidate = new RTCIceCandidate(message.payload.candidate)
      if (peerConnection.value.remoteDescription) {
        await peerConnection.value.addIceCandidate(candidate)
      } else {
        pendingIceCandidates.value.push(candidate)
      }
    }
  }

  async function replaceVideoTrack(track, stream) {
    const sender = peerConnection.value
      ?.getSenders()
      .find(entry => entry.track?.kind === 'video')

    if (sender) {
      await sender.replaceTrack(track)
    } else if (peerConnection.value) {
      peerConnection.value.addTrack(track, stream)
    }

    const audioTracks = localStream.value?.getAudioTracks() || []
    for (const existingTrack of localStream.value?.getVideoTracks() || []) {
      existingTrack.stop()
    }
    const nextStream = new MediaStream([...audioTracks, track].filter(Boolean))
    localStream.value = nextStream
    syncRemoteAudio()
  }

  async function toggleMute() {
    if (!localStream.value) return
    const nextMuted = !mediaState.value.muted
    for (const track of localStream.value.getAudioTracks()) {
      track.enabled = !nextMuted
    }
    mediaState.value = { ...mediaState.value, muted: nextMuted }
  }

  async function toggleCamera() {
    if (!activeCall.value) return

    // Audio call → upgrade to video by adding camera track
    if (activeCall.value.callType !== 'video') {
      try {
        const cameraStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user' },
          audio: false,
        })
        const videoTrack = cameraStream.getVideoTracks()[0]

        if (peerConnection.value) {
          peerConnection.value.addTrack(videoTrack, localStream.value)
          // Renegotiate so the remote peer gets the video track
          const offer = await peerConnection.value.createOffer()
          await peerConnection.value.setLocalDescription(offer)
          await request('relay_call_signal', {
            call_id: activeCall.value.callId,
            receiver: activeCall.value.remoteUser,
            signal_type: 'offer',
            payload: { offer },
          })
        }

        // Merge video track into local stream
        const audioTracks = localStream.value?.getAudioTracks() || []
        localStream.value = new MediaStream([...audioTracks, videoTrack])

        // Upgrade call type so VideoCallUI renders
        activeCall.value = { ...activeCall.value, callType: 'video' }
        mediaState.value = { ...mediaState.value, cameraOn: true }
      } catch (err) {
        console.error('[call] camera upgrade failed', err)
      }
      return
    }

    // Already a video call — toggle camera on/off
    const videoTrack = localStream.value?.getVideoTracks?.()[0]
    if (!videoTrack) {
      const cameraStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
      const nextTrack = cameraStream.getVideoTracks()[0]
      await replaceVideoTrack(nextTrack, cameraStream)
      mediaState.value = { ...mediaState.value, cameraOn: true, screenSharing: false }
      return
    }

    const nextCameraOn = !mediaState.value.cameraOn
    videoTrack.enabled = nextCameraOn
    mediaState.value = { ...mediaState.value, cameraOn: nextCameraOn }
  }

  async function toggleScreenShare() {
    if (!activeCall.value || activeCall.value.callType !== 'video') return

    if (mediaState.value.screenSharing) {
      const cameraStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
      const cameraTrack = cameraStream.getVideoTracks()[0]
      await replaceVideoTrack(cameraTrack, cameraStream)
      mediaState.value = { ...mediaState.value, screenSharing: false, cameraOn: true }
      return
    }

    const displayStream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: false })
    const displayTrack = displayStream.getVideoTracks()[0]
    displayTrack.onended = () => {
      if (mediaState.value.screenSharing) {
        toggleScreenShare().catch(() => null)
      }
    }
    await replaceVideoTrack(displayTrack, displayStream)
    mediaState.value = { ...mediaState.value, screenSharing: true, cameraOn: true }
  }

  function toggleSpeaker() {
    mediaState.value = { ...mediaState.value, speakerOn: !mediaState.value.speakerOn }
    syncRemoteAudio()
  }

  async function refreshCallLogs(otherUser) {
    const response = await request('get_call_logs', {
      other_user: otherUser || undefined,
      limit: 8,
    })
    callLogs.value = response.logs || []
    callSummary.value = response.summary || { call_count: 0, missed_calls: 0 }
  }

  async function onCallInitiated(payload) {
    if (payload.caller === session.user) return
    if (isInCall.value) return

    incomingCall.value = buildCall(payload, 'incoming')
    options.onIncomingCall?.(incomingCall.value, payload)
    callStatus.value = 'incoming'
    playTone('incoming')
    console.debug('[call] incoming event', payload)
    options.onCallStateChange?.()
  }

  function onCallRejected() {
    stopTone()
    resetCallState()
    options.onCallStateChange?.()
  }

  function onCallEnded() {
    stopTone()
    resetCallState()
    options.onCallStateChange?.()
  }

  function handleRealtimeEnvelope(message) {
    if (!message?.event) return
    console.debug('[call] realtime envelope', message)

    if (message.event === 'call_initiated') {
      onCallInitiated(message.data)
      return
    }

    if (message.event === 'call_accepted') {
      handleCallAccepted(message.data)
      return
    }

    if (message.event === 'call_rejected') {
      onCallRejected()
      return
    }

    if (message.event === 'call_ended') {
      onCallEnded()
      return
    }

    if (['call_log_deleted', 'call_logs_cleared'].includes(message.event)) {
      options.onCallStateChange?.()
      return
    }

    if (message.event === 'call_signal') {
      handleSignal(message.data)
    }
  }

  if (socket) {
    socket.on('call_initiated', onCallInitiated)
    socket.on('call_accepted', handleCallAccepted)
    socket.on('call_rejected', onCallRejected)
    socket.on('call_ended', onCallEnded)
    socket.on('call_signal', handleSignal)
    socket.on('realtime', handleRealtimeEnvelope)
  }

  onUnmounted(() => {
    if (socket) {
      socket.off('call_initiated', onCallInitiated)
      socket.off('call_accepted', handleCallAccepted)
      socket.off('call_rejected', onCallRejected)
      socket.off('call_ended', onCallEnded)
      socket.off('call_signal', handleSignal)
      socket.off('realtime', handleRealtimeEnvelope)
    }
    resetCallState()
  })

  return {
    activeCall,
    callLogs,
    callStatus,
    callSummary,
    currentCall,
    durationText,
    incomingCall,
    isInCall,
    isVideoCall,
    localStream,
    mediaState,
    remoteStream,
    acceptIncomingCall,
    endCurrentCall,
    refreshCallLogs,
    rejectIncomingCall,
    startCall,
    toggleCamera,
    toggleMute,
    toggleScreenShare,
    toggleSpeaker,
  }
}
