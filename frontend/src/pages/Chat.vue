<template>
  <div class="flex h-screen bg-gray-100 overflow-hidden">

    <!-- ── Left Sidebar ── -->
    <div class="w-80 flex flex-col bg-white border-r border-gray-200 flex-shrink-0">

      <!-- Header -->
      <div class="flex items-center justify-between px-4 py-4 bg-green-600">
        <div class="flex items-center gap-3">
          <div class="w-9 h-9 rounded-full bg-white/30 flex items-center justify-center text-white font-bold text-sm">
            {{ currentUserInitials }}
          </div>
          <span class="text-white font-semibold text-sm">{{ currentUserName }}</span>
        </div>
        <button @click="logout" class="text-white/80 hover:text-white text-xs">Logout</button>
      </div>

      <!-- Search -->
      <div class="px-3 py-2 bg-gray-50 border-b border-gray-100">
        <input
          v-model="search"
          type="text"
          placeholder="Search or start new chat"
          class="w-full bg-white border border-gray-200 rounded-full px-4 py-2 text-sm outline-none focus:ring-1 focus:ring-green-400"
        />
      </div>

      <!-- User list -->
      <div class="flex-1 overflow-y-auto">
        <div
          v-for="user in filteredUsers"
          :key="user.name"
          @click="selectUser(user)"
          class="flex items-center gap-3 px-4 py-3 cursor-pointer border-b border-gray-50 hover:bg-gray-50 transition-colors"
          :class="{ 'bg-green-50 border-l-4 border-l-green-500': selectedUser?.name === user.name }"
        >
          <div
            class="w-11 h-11 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-sm"
            :style="{ background: avatarColor(user.name) }"
          >
            {{ initials(user.full_name || user.first_name || user.name) }}
          </div>
          <div class="flex-1 min-w-0">
            <div class="flex justify-between items-baseline">
              <span class="font-medium text-gray-800 text-sm truncate">
                {{ user.name === session.user ? 'You' : (user.full_name || user.first_name || user.name) }}
              </span>
              <span v-if="lastMessageMap[user.name]?.timestamp" class="text-xs text-gray-400 flex-shrink-0 ml-1">
                {{ formatTime(lastMessageMap[user.name].timestamp) }}
              </span>
            </div>
            <p class="text-xs text-gray-400 truncate mt-0.5">
              {{ lastMessageMap[user.name]?.last_message || 'Start a conversation' }}
            </p>
          </div>
        </div>

        <div v-if="filteredUsers.length === 0" class="p-6 text-center text-gray-400 text-sm">
          No users found
        </div>
      </div>
    </div>

    <!-- ── Right Chat Window ── -->
    <div class="flex-1 flex flex-col">

      <!-- No chat selected -->
      <div v-if="!selectedUser" class="flex-1 flex flex-col items-center justify-center bg-gray-50">
        <div class="text-6xl mb-4">💬</div>
        <h2 class="text-xl font-semibold text-gray-600">FunChat</h2>
        <p class="text-gray-400 text-sm mt-2">Select a user to start chatting</p>
      </div>

      <!-- Chat active -->
      <template v-else>

        <!-- Chat Header -->
        <div class="flex items-center gap-3 px-4 py-3 bg-green-600 shadow-sm">
          <div
            class="w-9 h-9 rounded-full flex-shrink-0 flex items-center justify-center text-white font-bold text-sm"
            :style="{ background: avatarColor(selectedUser.name) }"
          >
            {{ initials(selectedUser.full_name || selectedUser.first_name || selectedUser.name) }}
          </div>
          <div>
            <p class="text-white font-semibold text-sm">
              {{ selectedUser.name === session.user ? 'You (Self)' : (selectedUser.full_name || selectedUser.first_name || selectedUser.name) }}
            </p>
            <p class="text-green-200 text-xs">{{ selectedUser.name }}</p>
          </div>
        </div>

        <!-- Messages Area -->
        <div
          ref="messagesContainer"
          class="flex-1 overflow-y-auto px-4 py-4"
          style="background-color: #e5ddd5;"
        >
          <div v-if="loadingMessages" class="text-center text-gray-400 text-sm py-8">
            Loading messages...
          </div>

          <template v-for="group in messageGroups" :key="group.conversation_name">

            <!-- Date Divider -->
            <div class="flex items-center gap-3 my-4">
              <div class="flex-1 h-px bg-gray-300/60"></div>
              <span class="text-xs text-gray-500 bg-white/80 px-3 py-1 rounded-full shadow-sm">
                {{ formatDateLabel(group.start_date) }}
              </span>
              <div class="flex-1 h-px bg-gray-300/60"></div>
            </div>

            <!-- Messages in this group -->
            <div
              v-for="(msg, idx) in group.messages"
              :key="idx"
              class="flex mb-1"
              :class="msg.sender === session.user ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-xs lg:max-w-md px-3 py-2 rounded-2xl shadow-sm text-sm"
                :class="msg.sender === session.user
                  ? 'bg-green-500 text-white rounded-br-sm'
                  : 'bg-white text-gray-800 rounded-bl-sm'"
              >
                <p class="whitespace-pre-wrap break-words">{{ msg.message }}</p>
                <p
                  class="text-xs mt-1 text-right"
                  :class="msg.sender === session.user ? 'text-green-100' : 'text-gray-400'"
                >
                  {{ formatTime(msg.timestamp) }}
                </p>
              </div>
            </div>

          </template>

          <div
            v-if="!loadingMessages && messageGroups.length === 0"
            class="text-center text-gray-400 text-sm py-16"
          >
            No messages yet. Say hello! 👋
          </div>
        </div>

        <!-- Input Bar -->
        <div class="flex items-end gap-3 px-4 py-3 bg-white border-t border-gray-200">
          <textarea
            v-model="newMessage"
            @keydown.enter.exact.prevent="sendMessage"
            placeholder="Type a message..."
            rows="1"
            class="flex-1 resize-none border border-gray-200 rounded-2xl px-4 py-2.5 text-sm outline-none focus:ring-1 focus:ring-green-400 max-h-32 overflow-y-auto"
          />
          <button
            @click="sendMessage"
            :disabled="!newMessage.trim() || sending"
            class="w-10 h-10 rounded-full bg-green-500 hover:bg-green-600 disabled:bg-gray-300 flex items-center justify-center text-white flex-shrink-0 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5 rotate-45" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { createResource } from 'frappe-ui'
import { session } from '@/data/session'
import { useSocket } from '@/socket'

// ── State ──────────────────────────────────────────────────────────────────

const search = ref('')
const allUsers = ref([])          // full user list from API
const selectedUser = ref(null)
const messageGroups = ref([])     // [{ conversation_name, start_date, messages: [...] }]
const newMessage = ref('')
const sending = ref(false)
const loadingMessages = ref(false)
const messagesContainer = ref(null)
const lastMessageMap = ref({})    // { peerEmail: { last_message, timestamp } }

// ── Derived ────────────────────────────────────────────────────────────────

const currentUserName = computed(() => {
  const u = allUsers.value.find(u => u.name === session.user)
  return u?.full_name || u?.first_name || session.user
})

const currentUserInitials = computed(() => initials(currentUserName.value))

// Sidebar shows self + all other users
const sidebarUsers = computed(() => {
  const self = { name: session.user, full_name: currentUserName.value, first_name: session.user }
  return [self, ...allUsers.value]
})

const filteredUsers = computed(() => {
  const q = search.value.toLowerCase().trim()
  if (!q) return sidebarUsers.value
  return sidebarUsers.value.filter(u =>
    (u.full_name || u.first_name || u.name).toLowerCase().includes(q)
  )
})

// ── Helpers ─────────────────────────────────────────────────────────────────

function initials(name) {
  if (!name) return '?'
  return name.trim().split(/\s+/).map(w => w[0]).slice(0, 2).join('').toUpperCase()
}

const COLORS = ['#25D366', '#128C7E', '#075E54', '#34B7F1', '#0084ff', '#7b68ee', '#ff6b6b', '#ffa500']
function avatarColor(name) {
  let hash = 0
  for (const c of (name || '')) hash = c.charCodeAt(0) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
}

function formatTime(ts) {
  if (!ts) return ''
  const d = new Date(ts)
  if (isNaN(d.getTime())) return ''
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatDateLabel(dateStr) {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return dateStr
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)
  if (d.toDateString() === today.toDateString()) return 'Today'
  if (d.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return d.toLocaleDateString([], { weekday: 'long', year: 'numeric', month: 'short', day: 'numeric' })
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}

// ── Resources ────────────────────────────────────────────────────────────────

createResource({
  url: 'fun.api.get_users',
  auto: true,
  onSuccess(data) {
    allUsers.value = data || []
  },
})

createResource({
  url: 'fun.api.get_conversations',
  auto: true,
  onSuccess(data) {
    const map = {}
    for (const c of (data || [])) {
      map[c.peer] = { last_message: c.last_message, timestamp: c.timestamp }
    }
    lastMessageMap.value = map
  },
})

const messagesResource = createResource({
  url: 'fun.api.get_messages',
  onSuccess(data) {
    messageGroups.value = data || []
    loadingMessages.value = false
    scrollToBottom()
  },
  onError() {
    loadingMessages.value = false
  },
})

const sendResource = createResource({
  url: 'fun.api.send_message',
  onSuccess(data) {
    // Append sent message directly to UI (don't wait for socket)
    appendMessage(data)
    sending.value = false
    // Update sidebar preview
    const peer = data.receiver === session.user ? data.sender : data.receiver
    lastMessageMap.value = {
      ...lastMessageMap.value,
      [peer]: { last_message: data.message, timestamp: data.timestamp },
    }
  },
  onError() {
    sending.value = false
  },
})

// ── Append message to messageGroups ──────────────────────────────────────────

function appendMessage(data) {
  const lastGroup = messageGroups.value[messageGroups.value.length - 1]
  if (lastGroup && lastGroup.conversation_name === data.conversation_name) {
    // Add to existing group
    lastGroup.messages.push({
      sender: data.sender,
      message: data.message,
      timestamp: data.timestamp,
    })
  } else {
    // New conversation window
    messageGroups.value.push({
      conversation_name: data.conversation_name,
      start_date: data.start_date,
      messages: [{
        sender: data.sender,
        message: data.message,
        timestamp: data.timestamp,
      }],
    })
  }
  scrollToBottom()
}

// ── Actions ──────────────────────────────────────────────────────────────────

function selectUser(user) {
  selectedUser.value = user
  messageGroups.value = []
  loadingMessages.value = true
  messagesResource.submit({ other_user: user.name })
}

function sendMessage() {
  const text = newMessage.value.trim()
  if (!text || sending.value || !selectedUser.value) return
  sending.value = true
  newMessage.value = ''
  sendResource.submit({ receiver: selectedUser.value.name, message: text })
}

// ── Socket: realtime for the receiver side ───────────────────────────────────

let socket = null

function handleIncomingMessage(data) {
  // This fires for BOTH sender (duplicate) and receiver
  // For sender: already appended in sendResource.onSuccess, skip
  if (data.sender === session.user) return

  // Update sidebar
  const peer = data.sender
  lastMessageMap.value = {
    ...lastMessageMap.value,
    [peer]: { last_message: data.message, timestamp: data.timestamp },
  }

  // Only update chat window if this conversation is open
  if (!selectedUser.value) return
  if (data.sender !== selectedUser.value.name && data.receiver !== selectedUser.value.name) return

  appendMessage(data)
}

onMounted(() => {
  socket = useSocket()
  if (socket) {
    socket.on('new_message', handleIncomingMessage)
  }
})

onUnmounted(() => {
  if (socket) {
    socket.off('new_message', handleIncomingMessage)
  }
})

// ── Logout ────────────────────────────────────────────────────────────────────

function logout() {
  session.logout.submit()
}
</script>
