<template>
  <div class="flex h-screen overflow-hidden bg-gray-100">
    <Sidebar
      :call-logs="sidebarCallLogs"
      :call-summary="recentCallSummary"
      :clearing-call-logs="clearingCallLogs"
      :current-user-email="session.user || ''"
      :current-user-initials="currentUserInitials"
      :current-user-name="currentUserName"
      :deleting-call-id="deletingCallId"
      :deleting-selected-call-logs="deletingSelectedCallLogsState"
      :expanded="sidebarExpanded"
      :chat-open="!!selectedUser"
      @clear-logs="clearAllCallLogs"
      @delete-log="deleteCallLog"
      @delete-selected="deleteSelectedCallLogs"
      @logout="logout"
      @select-peer="focusPeer"
      @call-peer="({ peer, type }) => { focusPeer(peer); startCall(resolveUser(peer), type).catch(console.error) }"
      @toggle="sidebarExpanded = !sidebarExpanded"
    />

    <div class="flex flex-1 overflow-hidden md:pb-0" :class="selectedUser ? 'pb-0' : 'pb-16'">
      <div
        class="fixed z-20 flex w-full sm:w-72 transform flex-col border-r border-gray-200 bg-white transition-transform duration-300 md:w-80 md:relative md:translate-x-0 md:h-full"
        :style="{ height: selectedUser ? '100dvh' : 'calc(100dvh - 4rem)' }"
        :class="selectedUser ? '-translate-x-full md:translate-x-0' : 'translate-x-0'"
      >
        <div class="flex items-center justify-between bg-green-600 px-4 py-3">
          
          <!-- <div class="flex items-center gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-full bg-white/30 text-sm font-bold text-white">
              {{ currentUserInitials }}
            </div>
            <span class="max-w-[120px] truncate text-sm font-semibold text-white">
              {{ currentUserName }}
            </span> 
          </div> -->
          <span class="max-w-[120px] truncate text-sm font-semibold text-white">
              Chat With Friends
          </span>
        </div>

        <div class="border-b border-gray-100 bg-gray-50 px-3 py-2">
          <input
            v-model="search"
            type="text"
            placeholder="Search"
            class="w-full rounded-full border border-gray-200 bg-white px-4 py-2 text-sm outline-none focus:ring-1 focus:ring-green-400"
          />
        </div>

        <div class="flex-1 overflow-y-auto">
          <div
            v-for="user in filteredUsers"
            :key="user.name"
            class="relative flex cursor-pointer items-center gap-3 border-b px-3 py-3 hover:bg-gray-50 sm:px-4"
            :class="{ 'border-l-4 border-l-green-500 bg-green-50': selectedUser?.name === user.name }"
            @click="selectUser(user)"
          >
            <div class="relative">
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white sm:h-11 sm:w-11"
                :style="{ background: avatarColor(user.name) }"
              >
                {{ initials(user.full_name || user.first_name || user.name) }}
              </div>
              <div
                v-if="onlineUsers.includes(user.name)"
                class="absolute bottom-0 right-0 h-3 w-3 rounded-full border-2 border-white bg-green-500"
              ></div>
            </div>

            <div class="min-w-0 flex-1">
              <div class="flex justify-between gap-2">
                <span class="truncate text-sm font-medium text-gray-800">
                  {{ user.name === session.user ? 'You' : (user.full_name || user.first_name || user.name) }}
                </span>
                <div class="flex items-center gap-1">
                  <span class="text-xs text-gray-400">
                    {{ formatTime(lastMessageMap[user.name]?.timestamp) }}
                  </span>
                  <span
                    v-if="unreadCount[user.name]"
                    class="min-w-[18px] rounded-full bg-green-500 px-1 text-center text-xs text-white"
                  >
                    {{ unreadCount[user.name] }}
                  </span>
                </div>
              </div>
              <p class="truncate text-xs text-gray-400">
                {{ lastMessageMap[user.name]?.last_message || 'Start chat' }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="flex w-full flex-1 flex-col">
        <div v-if="!selectedUser" class="flex flex-1 items-center justify-center text-center">
          <div>
            <div class="mb-3 text-5xl">💬</div>
            <p class="text-gray-500">Select a chat</p>
          </div>
        </div>

        <template v-else>
          <div class="flex items-center gap-3 bg-green-600 px-3 py-3 sm:px-4">
            <button class="text-lg text-white md:hidden" @click="selectedUser = null">←</button>

            <div
              class="flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold text-white"
              :style="{ background: avatarColor(selectedUser.name) }"
            >
              {{ initials(selectedUser.full_name || selectedUser.name) }}
            </div>

            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-white">
                {{ selectedUser.full_name || selectedUser.name }}
              </p>
              <p class="truncate text-xs text-green-200">
                {{ typingUsers[selectedUser.name] ? 'typing...' : (onlineUsers.includes(selectedUser.name) ? 'online' : 'offline') }}
              </p>
            </div>

            <div class="ml-auto flex gap-2">
              <button class="text-lg text-white hover:text-green-200" title="Voice Call" @click="startVoiceCall">📞</button>
              <button class="text-lg text-white hover:text-green-200" title="Video Call" @click="startVideoCall">📹</button>
            </div>
          </div>

          <!-- <div class="border-b bg-white px-4 py-3">
            <div class="flex items-center justify-between gap-3">
              <div>
                <p class="text-xs font-semibold uppercase tracking-[0.24em] text-gray-400">Call History</p>
                <p class="text-sm text-gray-600">
                  {{ callSummary.call_count }} calls, {{ callSummary.missed_calls }} missed
                </p>
              </div>
              <p v-if="isInCall" class="rounded-full bg-green-50 px-3 py-1 text-xs font-medium text-green-700">
                {{ callStatusLabel }}
              </p>
            </div>

            <div v-if="callLogs.length" class="mt-3 flex gap-2 overflow-x-auto pb-1">
              <div
                v-for="log in callLogs"
                :key="log.call_id"
                class="min-w-[180px] rounded-2xl border border-gray-200 bg-gray-50 px-3 py-2"
              >
                <div class="flex items-center justify-between gap-2">
                  <span class="text-sm font-semibold text-gray-700">{{ log.call_type }}</span>
                  <span class="text-[11px] uppercase tracking-[0.2em] text-gray-400">{{ log.direction }}</span>
                </div>
                <p class="mt-1 text-xs text-gray-500">{{ log.status }}</p>
                <p class="mt-1 text-xs text-gray-400">
                  {{ log.duration || '00:00' }} · {{ formatTime(log.start_time || log.end_time) }}
                </p>
              </div>
            </div>
            <p v-else class="mt-3 text-sm text-gray-400">No calls with this user yet.</p>
          </div> -->

          <div ref="messagesContainer" class="flex-1 overflow-y-auto px-2 py-3 sm:px-4" style="background:#e5ddd5">
            <div v-for="group in messageGroups" :key="group.conversation_name">
              <div class="my-3 text-center text-xs text-gray-500">
                {{ formatDateLabel(group.start_date) }}
              </div>

              <div
                v-for="(msg, index) in group.messages"
                :key="msg.id || `${group.conversation_name}-${index}`"
                class="mb-3 flex flex-col"
                :class="isOwnMessage(msg) ? 'items-end' : 'items-start'"
              >
                <div class="group relative w-full max-w-[85%] sm:max-w-md">

                  <!-- ── Hover action bar ── -->
                  <div
                    v-if="msg.id && !msg.deleted_for_everyone"
                    class="absolute -top-9 z-30 flex items-center gap-0.5 rounded-full border border-gray-200 bg-white/95 px-1.5 py-1 shadow-lg backdrop-blur transition-all duration-150"
                    :class="[
                      isOwnMessage(msg) ? 'right-0' : 'left-0',
                      activeMessageMenuId === msg.id ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto',
                    ]"
                    @click.stop
                  >
                    <!-- Quick reaction emojis -->
                    <button v-for="emoji in quickReactions" :key="emoji" type="button"
                      class="flex h-7 w-7 items-center justify-center rounded-full text-base transition hover:bg-gray-100 hover:scale-125"
                      @click.stop="sendReaction(msg, emoji)"
                    >{{ emoji }}</button>

                    <!-- More reactions -->
                    <button type="button"
                      class="flex h-7 w-7 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100"
                      @click.stop="openReactionPicker(msg)"
                      title="More reactions"
                    >
                      <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm1-11h-2v3H8v2h3v3h2v-3h3v-2h-3z"/>
                      </svg>
                    </button>

                    <div class="mx-1 h-5 w-px bg-gray-200"></div>

                    <!-- Reply button -->
                    <button type="button"
                      class="flex h-7 w-7 items-center justify-center rounded-full text-gray-500 transition hover:bg-gray-100 hover:text-green-600"
                      title="Reply"
                      @click.stop="startReply(msg)"
                    >
                      <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                        <path d="M10 9V5l-7 7 7 7v-4.1c5 0 8.5 1.6 11 5.1-1-5-4-10-11-11z"/>
                      </svg>
                    </button>

                    <!-- 3-dot menu button -->
                    <button type="button"
                      class="flex h-7 w-7 items-center justify-center rounded-full text-gray-500 transition hover:bg-gray-100"
                      :class="activeMessageMenuId === msg.id ? 'bg-gray-100 text-gray-700' : ''"
                      title="More options"
                      @click.stop="toggleMessageMenu(msg.id)"
                    >
                      <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                        <circle cx="5" cy="12" r="1.7"/><circle cx="12" cy="12" r="1.7"/><circle cx="19" cy="12" r="1.7"/>
                      </svg>
                    </button>
                  </div>

                  <!-- ── Reaction picker popup ── -->
                  <div
                    v-if="reactionPickerMsgId === msg.id"
                    class="absolute -top-[120px] z-40 w-72 rounded-2xl border border-gray-200 bg-white p-2 shadow-2xl"
                    :class="isOwnMessage(msg) ? 'right-0' : 'left-0'"
                    @click.stop
                  >
                    <div class="grid grid-cols-10 gap-0.5 max-h-32 overflow-y-auto">
                      <button v-for="emoji in reactionEmojis" :key="emoji" type="button"
                        class="flex h-7 w-7 items-center justify-center rounded-lg text-base transition hover:bg-gray-100 hover:scale-125"
                        @click.stop="sendReaction(msg, emoji); reactionPickerMsgId = ''"
                      >{{ emoji }}</button>
                    </div>
                  </div>

                  <div
                    class="relative overflow-hidden rounded-[26px] px-3 py-2 pr-12 text-sm shadow"
                    :class="messageBubbleClass(msg)"
                  >
                    <p
                      v-if="msg.forwarded && !msg.deleted_for_everyone"
                      class="mb-2 text-[11px] font-semibold uppercase tracking-[0.2em]"
                      :class="isOwnMessage(msg) ? 'text-white/70' : 'text-gray-400'"
                    >
                      Forwarded
                    </p>

                    <template v-if="msg.deleted_for_everyone">
                      <div class="flex items-center gap-2 text-sm italic">
                        <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M6 12h12" stroke-linecap="round" />
                          <path d="M9 7h6m-6 10h6" stroke-linecap="round" opacity=".55" />
                        </svg>
                        <span>{{ deletedMessageLabel(msg) }}</span>
                      </div>
                    </template>

                    <template v-else>
                      <template v-if="msg.attachment">
                        <img
                          v-if="isImageMessage(msg)"
                          :src="msg.attachment.file_url"
                          :alt="msg.attachment.file_name || 'Image attachment'"
                          class="max-h-72 w-full rounded-2xl object-cover"
                        />
                        <video
                          v-else-if="isVideoMessage(msg)"
                          :src="msg.attachment.file_url"
                          controls
                          preload="metadata"
                          class="max-h-72 w-full rounded-2xl bg-black"
                        ></video>
                        <audio
                          v-else-if="isAudioMessage(msg)"
                          :src="msg.attachment.file_url"
                          controls
                          preload="metadata"
                          class="w-full min-w-[220px]"
                        ></audio>
                        <a
                          v-else
                          :href="msg.attachment.file_url"
                          :download="msg.attachment.file_name || 'attachment'"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="flex min-w-[220px] items-center gap-3 rounded-2xl border px-3 py-2 transition hover:opacity-90"
                          :class="attachmentCardClass(msg)"
                        >
                          <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-black/10 text-lg font-semibold">
                            {{ fileExtensionLabel(msg.attachment) }}
                          </div>
                          <div class="min-w-0 flex-1">
                            <p class="truncate font-medium">{{ msg.attachment.file_name || 'Attachment' }}</p>
                            <p class="text-xs" :class="attachmentMetaClass(msg)">
                              {{ buildAttachmentPreviewLabel(msg.attachment) }}
                              <span v-if="msg.attachment.file_size"> · {{ formatFileSize(msg.attachment.file_size) }}</span>
                            </p>
                          </div>
                        </a>
                      </template>

                      <div
                        v-if="msg.attachment && showsInlineAttachmentActions(msg)"
                        class="mt-2 flex items-center justify-between gap-3 text-[11px]"
                        :class="attachmentMetaClass(msg)"
                      >
                        <span class="min-w-0 truncate">
                          {{ msg.attachment.file_name || buildAttachmentPreviewLabel(msg.attachment) }}
                        </span>
                        <button
                          type="button"
                          class="shrink-0 rounded-full border px-2.5 py-1 font-medium transition"
                          :class="isOwnMessage(msg) ? 'border-white/25 text-white hover:bg-white/10' : 'border-gray-300 text-gray-600 hover:bg-gray-100'"
                          @click.stop="downloadAttachment(msg.attachment)"
                        >
                          Download
                        </button>
                      </div>

                      <div v-if="editingMessageId === msg.id" class="mt-2 space-y-2">
                        <textarea
                          v-model="editingMessageText"
                          rows="3"
                          class="w-full resize-none rounded-2xl border border-black/10 bg-white/90 px-3 py-2 text-sm text-gray-800 outline-none focus:ring-2 focus:ring-green-400"
                          placeholder="Update your message"
                          @keydown.esc.prevent="cancelEditingMessage"
                          @keydown.ctrl.enter.prevent="saveEditedMessage(msg)"
                        />
                        <div class="flex justify-end gap-2">
                          <button
                            type="button"
                            class="rounded-full border border-black/10 px-3 py-1.5 text-xs font-medium text-gray-600 transition hover:bg-black/5"
                            @click="cancelEditingMessage"
                          >
                            Cancel
                          </button>
                          <button
                            type="button"
                            class="rounded-full bg-green-500 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-green-600 disabled:cursor-not-allowed disabled:opacity-60"
                            :disabled="isMessageActionBusy(msg.id) || (!editingMessageText.trim() && !msg.attachment)"
                            @click="saveEditedMessage(msg)"
                          >
                            Save
                          </button>
                        </div>
                      </div>

                      <p v-else-if="msg.message" class="whitespace-pre-wrap break-words" :class="msg.attachment ? 'mt-2' : ''">
                        {{ msg.message }}
                      </p>
                    </template>
                  </div>

                  <div
                    v-if="activeMessageMenuId === msg.id"
                    class="absolute top-12 z-30 w-56 overflow-hidden rounded-2xl border border-gray-200 bg-white/95 p-1 shadow-2xl backdrop-blur"
                    :class="isOwnMessage(msg) ? 'right-0' : 'left-0'"
                    @click.stop
                  >
                    <button
                      v-if="canEditMessage(msg)"
                      type="button"
                      class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-gray-700 transition hover:bg-gray-100"
                      @click="startEditingMessage(msg)"
                    >
                      <span class="text-base">✏️</span>
                      <span>Edit message</span>
                    </button>
                    <button
                      v-if="canForwardMessage(msg)"
                      type="button"
                      class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-gray-700 transition hover:bg-gray-100"
                      @click="openForwardModal(msg)"
                    >
                      <span class="text-base">↗</span>
                      <span>Forward</span>
                    </button>
                    <button
                      v-if="canDownloadAttachment(msg)"
                      type="button"
                      class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-gray-700 transition hover:bg-gray-100"
                      @click="downloadAttachment(msg.attachment)"
                    >
                      <span class="text-base">⤓</span>
                      <span>Download</span>
                    </button>
                    <button
                      v-if="canDeleteForMe(msg)"
                      type="button"
                      class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-rose-600 transition hover:bg-rose-50"
                      @click="deleteMessageForMeAction(msg)"
                    >
                      <span class="text-base">🗑</span>
                      <span>Delete for me</span>
                    </button>
                    <button
                      v-if="canDeleteForEveryone(msg)"
                      type="button"
                      class="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-left text-sm text-rose-600 transition hover:bg-rose-50"
                      @click="deleteMessageForEveryoneAction(msg)"
                    >
                      <span class="text-base">⛔</span>
                      <span>Delete for everyone</span>
                    </button>
                  </div>
                </div>
                <!-- Reactions display -->
                <div
                  v-if="messageReactions[msg.id] && Object.keys(messageReactions[msg.id]).length"
                  class="mt-1 flex flex-wrap gap-1 px-1"
                  :class="isOwnMessage(msg) ? 'justify-end' : 'justify-start'"
                >
                  <button
                    v-for="(users, emoji) in messageReactions[msg.id]"
                    :key="emoji"
                    type="button"
                    class="flex items-center gap-1 rounded-full border bg-white px-2 py-0.5 text-xs shadow-sm transition hover:bg-gray-50"
                    :class="users.includes(session.user) ? 'border-green-300 bg-green-50' : 'border-gray-200'"
                    @click.stop="sendReaction(msg, emoji)"
                  >
                    <span class="text-sm">{{ emoji }}</span>
                    <span class="font-medium text-gray-600">{{ users.length }}</span>
                  </button>
                </div>

                <div
                  class="mt-1 px-1 text-[10px]"
                  :class="isOwnMessage(msg) ? 'text-right text-gray-500' : 'text-left text-gray-500'"
                >
                  {{ formatTime(msg.timestamp) }}<span v-if="msg.edited"> · edited</span>
                </div>
              </div>
            </div>
          </div>

          <div class="border-t bg-white px-2 py-2 sm:px-4">
            <input ref="fileInputRef" type="file" class="hidden" @change="handleAttachmentSelection" />

            <!-- Reply preview strip -->
            <div v-if="replyingTo" class="mb-2 flex items-center gap-2 rounded-xl border-l-4 border-green-500 bg-green-50 px-3 py-2">
              <div class="min-w-0 flex-1">
                <p class="text-[11px] font-semibold text-green-700">
                  {{ replyingTo.sender === session.user ? 'You' : (selectedUser?.full_name || selectedUser?.name) }}
                </p>
                <p class="truncate text-xs text-gray-500">
                  {{ replyingTo.attachment ? '📎 ' + (replyingTo.attachment.file_name || 'Attachment') : replyingTo.message }}
                </p>
              </div>
              <button
                type="button"
                class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-200 hover:text-gray-600"
                @click="replyingTo = null"
              >
                <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="m6 6 12 12M18 6 6 18" stroke-linecap="round"/>
                </svg>
              </button>
            </div>

            <div v-if="uploadingAttachment || pendingAttachment" class="mb-2 flex items-center justify-between gap-3 rounded-2xl border border-gray-200 bg-gray-50 px-3 py-2">
              <div class="min-w-0">
                <p class="truncate text-sm font-medium text-gray-700">
                  {{ uploadingAttachment ? 'Uploading file...' : (pendingAttachment?.file_name || 'Attachment ready') }}
                </p>
                <p class="text-xs text-gray-500">
                  {{ uploadingAttachment ? 'Please wait before sending' : buildPendingAttachmentMeta() }}
                </p>
              </div>

              <button
                v-if="pendingAttachment && !uploadingAttachment"
                type="button"
                class="flex h-8 w-8 items-center justify-center rounded-full border border-gray-200 text-gray-500 transition hover:border-rose-300 hover:text-rose-500"
                @click="removePendingAttachment"
              >
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m6 6 12 12M18 6 6 18" stroke-linecap="round" />
                </svg>
              </button>
            </div>

            <div class="relative flex gap-2 items-center">

              <!-- ── 3-dot button (mobile only) ── -->
              <div class="relative sm:hidden">
                <button
                  type="button"
                  class="flex h-10 w-10 items-center justify-center rounded-full border border-gray-300 bg-white text-gray-600 transition hover:border-green-400 hover:text-green-600 disabled:cursor-not-allowed disabled:opacity-50"
                  :disabled="!selectedUser || sending || uploadingAttachment"
                  @click.stop="showMoreMenu = !showMoreMenu"
                >
                  <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                    <circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/>
                  </svg>
                </button>

                <!-- Popup with icons -->
                <transition
                  enter-active-class="transition duration-150 ease-out"
                  enter-from-class="translate-y-2 opacity-0"
                  enter-to-class="translate-y-0 opacity-100"
                  leave-active-class="transition duration-100 ease-in"
                  leave-from-class="translate-y-0 opacity-100"
                  leave-to-class="translate-y-2 opacity-0"
                >
                  <div
                    v-if="showMoreMenu"
                    class="absolute bottom-14 left-0 z-50 flex gap-3 rounded-2xl border border-gray-200 bg-white px-4 py-3 shadow-2xl"
                    @click.stop
                  >
                    <!-- Attach file -->
                    <button
                      type="button"
                      class="flex flex-col items-center gap-1"
                      @click="openAttachmentPicker(); showMoreMenu = false"
                    >
                      <span class="flex h-11 w-11 items-center justify-center rounded-full bg-purple-100 text-purple-600">
                        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
                          <path d="M21.44 11.05 12.25 20a6 6 0 1 1-8.49-8.48l9.19-8.95a4 4 0 0 1 5.66 5.65l-9.2 8.95a2 2 0 1 1-2.82-2.83l8.49-8.24" stroke-linecap="round" stroke-linejoin="round"/>
                        </svg>
                      </span>
                      <span class="text-[10px] text-gray-500">File</span>
                    </button>

                    <!-- Camera / Image -->
                    <button
                      type="button"
                      class="flex flex-col items-center gap-1"
                      @click="openImagePicker(); showMoreMenu = false"
                    >
                      <span class="flex h-11 w-11 items-center justify-center rounded-full bg-pink-100 text-pink-600">
                        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                          <path d="M20 5h-3.17L15 3H9L7.17 5H4a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2zm-8 13a5 5 0 1 1 0-10 5 5 0 0 1 0 10zm0-8a3 3 0 1 0 0 6 3 3 0 0 0 0-6z"/>
                        </svg>
                      </span>
                      <span class="text-[10px] text-gray-500">Photo</span>
                    </button>

                    <!-- Audio -->
                    <button
                      type="button"
                      class="flex flex-col items-center gap-1"
                      @click="openAudioPicker(); showMoreMenu = false"
                    >
                      <span class="flex h-11 w-11 items-center justify-center rounded-full bg-orange-100 text-orange-600">
                        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                          <path d="M12 3a4 4 0 0 1 4 4v5a4 4 0 0 1-8 0V7a4 4 0 0 1 4-4zm7 9a1 1 0 0 1 2 0 9 9 0 0 1-8 8.94V22h2a1 1 0 0 1 0 2H9a1 1 0 0 1 0-2h2v-1.06A9 9 0 0 1 3 12a1 1 0 0 1 2 0 7 7 0 0 0 14 0z"/>
                        </svg>
                      </span>
                      <span class="text-[10px] text-gray-500">Audio</span>
                    </button>

                    <!-- Video -->
                    <button
                      type="button"
                      class="flex flex-col items-center gap-1"
                      @click="openVideoPicker(); showMoreMenu = false"
                    >
                      <span class="flex h-11 w-11 items-center justify-center rounded-full bg-blue-100 text-blue-600">
                        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                          <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                        </svg>
                      </span>
                      <span class="text-[10px] text-gray-500">Video</span>
                    </button>

                    <!-- Document -->
                    <button
                      type="button"
                      class="flex flex-col items-center gap-1"
                      @click="openDocPicker(); showMoreMenu = false"
                    >
                      <span class="flex h-11 w-11 items-center justify-center rounded-full bg-green-100 text-green-600">
                        <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/>
                        </svg>
                      </span>
                      <span class="text-[10px] text-gray-500">Doc</span>
                    </button>
                  </div>
                </transition>
              </div>

              <!-- ── Attach button (desktop only) ── -->
              <button
                type="button"
                class="hidden sm:flex h-10 w-10 items-center justify-center rounded-full border border-gray-300 bg-white text-gray-600 transition hover:border-green-400 hover:text-green-600 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!selectedUser || sending || uploadingAttachment"
                @click="openAttachmentPicker"
              >
                <svg viewBox="0 0 24 24" class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21.44 11.05 12.25 20a6 6 0 1 1-8.49-8.48l9.19-8.95a4 4 0 0 1 5.66 5.65l-9.2 8.95a2 2 0 1 1-2.82-2.83l8.49-8.24" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </button>

              <!-- ── Textarea ── -->
              <div class="relative flex-1">
                <textarea
                  v-model="newMessage"
                  rows="1"
                  placeholder="Type..."
                  class="w-full resize-none rounded-full border px-4 py-2 pr-10 text-sm focus:ring-1 focus:ring-green-400"
                  @keydown.enter.exact.prevent="sendMessage"
                  @input="onTyping"
                  @blur="stopTyping"
                />

                <!-- Emoji button inside textarea -->
                <div class="absolute right-2 top-1/2 -translate-y-1/2">
                  <button
                    type="button"
                    class="flex h-7 w-7 items-center justify-center rounded-full text-gray-400 transition hover:bg-gray-100 hover:text-yellow-500"
                    @click.stop="showEmojiPicker = !showEmojiPicker"
                  >
                    <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 8 15.5 8 14 8.67 14 9.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 8 8.5 8 7 8.67 7 9.5 7.67 11 8.5 11zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z"/>
                    </svg>
                  </button>

                  <!-- Emoji Popup -->
                  <transition
                    enter-active-class="transition duration-150 ease-out"
                    enter-from-class="translate-y-2 opacity-0 scale-95"
                    enter-to-class="translate-y-0 opacity-100 scale-100"
                    leave-active-class="transition duration-100 ease-in"
                    leave-from-class="translate-y-0 opacity-100 scale-100"
                    leave-to-class="translate-y-2 opacity-0 scale-95"
                  >
                    <div
                      v-if="showEmojiPicker"
                      class="absolute bottom-10 right-0 z-50 w-72 rounded-2xl border border-gray-200 bg-white p-3 shadow-2xl"
                      @click.stop
                    >
                      <div class="mb-2 flex flex-wrap gap-1 border-b pb-2">
                        <button
                          v-for="cat in emojiCategories"
                          :key="cat.name"
                          type="button"
                          class="rounded-lg px-2 py-1 text-sm transition"
                          :class="activeEmojiCategory === cat.name ? 'bg-green-100 text-green-700' : 'hover:bg-gray-100'"
                          @click="activeEmojiCategory = cat.name"
                        >{{ cat.icon }}</button>
                      </div>
                      <div class="grid grid-cols-8 gap-0.5 max-h-48 overflow-y-auto">
                        <button
                          v-for="emoji in currentEmojis"
                          :key="emoji"
                          type="button"
                          class="flex h-8 w-8 items-center justify-center rounded-lg text-xl transition hover:bg-gray-100"
                          @click="insertEmoji(emoji)"
                        >{{ emoji }}</button>
                      </div>
                    </div>
                  </transition>
                </div>
              </div>

              <!-- ── Send button ── -->
              <button
                type="button"
                class="flex h-10 w-10 items-center justify-center rounded-full bg-green-500 text-white transition hover:bg-green-600 disabled:cursor-not-allowed disabled:opacity-50"
                :disabled="!canSendMessage"
                @click="sendMessage"
              >
                <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                  <path d="M3.4 20.4 21 12 3.4 3.6 3.3 10l12.2 2-12.2 2 .1 6.4z" />
                </svg>
              </button>
            </div>
          </div>
        </template>
      </div>

      <CallUI
        v-if="currentCall && !isVideoCall"
        :call="currentCall"
        :duration-text="durationText"
        :incoming="Boolean(incomingCall && !activeCall)"
        :media-state="mediaState"
        :status="callStatus"
        @accept="acceptIncomingCall"
        @end="endCurrentCall"
        @reject="rejectIncomingCall"
        @toggle-mute="toggleMute"
        @toggle-speaker="toggleSpeaker"
        @toggle-camera="toggleCamera"
      />

      <div
        v-if="incomingCall && !activeCall"
        class="fixed right-4 top-4 z-50 w-[calc(100vw-2rem)] max-w-[340px] rounded-3xl border border-emerald-200 bg-white p-4 shadow-2xl"
      >
        <p class="text-xs font-semibold uppercase tracking-[0.22em] text-green-600">Incoming Call</p>
        <p class="mt-2 text-lg font-semibold text-gray-900">{{ incomingCall.remoteName }}</p>
        <p class="mt-1 text-sm text-gray-500">
          {{ incomingCall.callType === 'video' ? 'Video call' : 'Audio call' }} ready to answer
        </p>
        <div class="mt-4 flex gap-2">
          <button class="flex-1 rounded-full bg-green-500 px-4 py-2 text-sm font-semibold text-white" @click="acceptIncomingCall">
            Accept
          </button>
          <button class="flex-1 rounded-full bg-rose-500 px-4 py-2 text-sm font-semibold text-white" @click="rejectIncomingCall">
            Reject
          </button>
        </div>
      </div>

      <VideoCallUI
        v-if="currentCall && isVideoCall"
        :call="currentCall"
        :duration-text="durationText"
        :incoming="Boolean(incomingCall && !activeCall)"
        :local-stream="localStream"
        :media-state="mediaState"
        :remote-stream="remoteStream"
        :status="callStatus"
        @accept="acceptIncomingCall"
        @end="endCurrentCall"
        @reject="rejectIncomingCall"
        @toggle-camera="toggleCamera"
        @toggle-mute="toggleMute"
        @toggle-screen-share="toggleScreenShare"
        @toggle-speaker="toggleSpeaker"
      />

      <div
        v-if="forwardingMessage"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/35 p-4 backdrop-blur-sm"
        @click="closeForwardModal"
      >
        <div class="w-full max-w-md rounded-[28px] bg-white p-5 shadow-2xl" @click.stop>
          <div class="flex items-start justify-between gap-3">
            <div>
              <p class="text-xs font-semibold uppercase tracking-[0.24em] text-green-600">Forward Message</p>
              <p class="mt-1 text-sm text-gray-500">Choose who should receive this message.</p>
            </div>
            <button
              type="button"
              class="flex h-9 w-9 items-center justify-center rounded-full border border-gray-200 text-gray-500 transition hover:border-rose-300 hover:text-rose-500"
              :disabled="forwardingState"
              @click="closeForwardModal"
            >
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m6 6 12 12M18 6 6 18" stroke-linecap="round" />
              </svg>
            </button>
          </div>

          <div class="mt-4 rounded-2xl border border-gray-200 bg-gray-50 px-4 py-3">
            <p class="text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-400">Preview</p>
            <p class="mt-2 text-sm text-gray-700">{{ forwardMessagePreview(forwardingMessage) }}</p>
          </div>

          <input
            v-model="forwardSearch"
            type="text"
            placeholder="Search user"
            class="mt-4 w-full rounded-2xl border border-gray-200 px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-green-400"
          />

          <div class="mt-4 max-h-72 space-y-2 overflow-y-auto pr-1">
            <button
              v-for="user in forwardTargets"
              :key="user.name"
              type="button"
              class="flex w-full items-center gap-3 rounded-2xl border border-gray-200 px-3 py-3 text-left transition hover:border-green-300 hover:bg-green-50 disabled:cursor-not-allowed disabled:opacity-60"
              :disabled="forwardingState"
              @click="forwardSelectedMessage(user)"
            >
              <div
                class="flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white"
                :style="{ background: avatarColor(user.name) }"
              >
                {{ initials(user.full_name || user.first_name || user.name) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-sm font-medium text-gray-800">
                  {{ user.full_name || user.first_name || user.name }}
                </p>
                <p class="truncate text-xs text-gray-400">{{ user.name }}</p>
              </div>
              <span class="rounded-full bg-gray-100 px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-gray-500">
                Send
              </span>
            </button>

            <div v-if="!forwardTargets.length" class="rounded-2xl border border-dashed border-gray-200 px-4 py-5 text-center text-sm text-gray-400">
              No matching users found.
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from 'vue'
import { createResource, frappeRequest } from 'frappe-ui'
import { useToast } from 'vue-toastification'

import CallUI from '@/Components/CallUI.vue'
import VideoCallUI from '@/Components/VideoCallUI.vue'
import { useCallManager } from '@/composables/useCallManager'
import { session } from '@/data/session'
import { connectSocket } from '@/socket'
import Sidebar from '../Components/sidebar.vue'

// Connect socket early so useCallManager can register its listeners
const socket = connectSocket()

const SELECTED_USER_KEY = 'selectedUserName'

const search = ref('')
const allUsers = ref([])
const selectedUser = ref(null)
const messageGroups = ref([])
const newMessage = ref('')
const sending = ref(false)
const loadingMessages = ref(false)
const uploadingAttachment = ref(false)
const messagesContainer = ref(null)
const fileInputRef = ref(null)
const lastMessageMap = ref({})
const lastOutgoingDraft = ref(null)
const pendingAttachment = ref(null)
const activeMessageMenuId = ref('')
const editingMessageId = ref('')
const editingMessageText = ref('')
const forwardingMessage = ref(null)
const forwardingState = ref(false)
const forwardSearch = ref('')
const messageActionBusyId = ref('')
const typingUsers = ref({})
const onlineUsers = ref([])
const showMoreMenu = ref(false)
const showEmojiPicker = ref(false)
const activeEmojiCategory = ref('smileys')
const replyingTo = ref(null)
const reactionPickerMsgId = ref('')
const messageReactions = ref({})  // { msgId: { '👍': ['user1','user2'], '❤️': ['user3'] } }

const quickReactions = ['👍', '❤️', '😆', '😮', '😢']
const reactionEmojis = ['👍','👎','❤️','🔥','😆','😮','😢','🙏','😍','🎉','👏','😂','🤔','💯','✅','😊','🥰','😭','😱','🤣','😅','😎','🤩','😇','🥳','😜','😋','😉','🤗','😴']

const emojiCategories = [
  { name: 'smileys', icon: '😀', emojis: ['😀','😃','😄','😁','😆','😅','😂','🤣','😊','😇','🙂','🙃','😉','😌','😍','🥰','😘','😗','😙','😚','😋','😛','😝','😜','🤪','🤨','🧐','🤓','😎','🤩','🥳','😏','😒','😞','😔','😟','😕','🙁','☹️','😣','😖','😫','😩','🥺','😢','😭','😤','😠','😡','🤬','🤯','😳','🥵','🥶','😱','😨','😰','😥','😓','🤗','🤔','🤭','🤫','🤥','😶','😐','😑','😬','🙄','😯','😦','😧','😮','😲','🥱','😴','🤤','😪','😵','🤐','🥴','🤢','🤮','🤧','😷','🤒','🤕'] },
  { name: 'hearts', icon: '❤️', emojis: ['❤️','🧡','💛','💚','💙','💜','🖤','🤍','🤎','💔','❣️','💕','💞','💓','💗','💖','💘','💝','💟','☮️','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','🖕','👇','☝️','👍','👎','✊','👊','🤛','🤜','👏','🙌','👐','🤲','🤝','🙏'] },
  { name: 'people', icon: '👋', emojis: ['👋','🤚','🖐️','✋','🖖','👌','🤌','🤏','✌️','🤞','🤟','🤘','🤙','👈','👉','👆','👇','☝️','👍','👎','✊','👊','🤛','🤜','👏','🙌','🫶','🤝','🙏','💪','🦾','🦿','🦵','🦶','👂','🦻','👃','🫀','🫁','🧠','🦷','🦴','👀','👁️','👅','👄','💋'] },
  { name: 'nature', icon: '🐶', emojis: ['🐶','🐱','🐭','🐹','🐰','🦊','🐻','🐼','🐻‍❄️','🐨','🐯','🦁','🐮','🐷','🐸','🐵','🙈','🙉','🙊','🐔','🐧','🐦','🐤','🦆','🦅','🦉','🦇','🐺','🐗','🐴','🦄','🐝','🪱','🐛','🦋','🐌','🐞','🐜','🪲','🦟','🦗','🪳','🦂','🐢','🐍','🦎','🦖','🦕','🐙','🦑','🦐','🦞','🦀','🐡','🐠','🐟','🐬','🐳','🐋','🦈','🐊','🐅','🐆','🦓','🦍','🦧','🦣','🐘','🦛','🦏','🐪','🐫','🦒','🦘','🦬','🐃','🐂','🐄','🐎','🐖','🐏','🐑','🦙','🐐','🦌','🐕','🐩','🦮','🐈','🪶','🐓','🦃','🦤','🦚','🦜','🦢','🦩','🕊️','🐇','🦝','🦨','🦡','🦫','🦦','🦥','🐁','🐀','🐿️','🦔'] },
  { name: 'food', icon: '🍕', emojis: ['🍕','🍔','🌮','🌯','🥗','🍜','🍝','🍛','🍲','🥘','🥫','🍱','🍣','🍤','🍙','🍚','🍘','🥟','🦪','🍦','🍧','🍨','🍩','🍪','🎂','🍰','🧁','🥧','🍫','🍬','🍭','🍮','🍯','🍼','🥛','☕','🍵','🧃','🥤','🧋','🍶','🍺','🍻','🥂','🍷','🥃','🍸','🍹','🧉','🍾','🧊','🥄','🍴','🍽️','🥢','🧂'] },
  { name: 'activity', icon: '⚽', emojis: ['⚽','🏀','🏈','⚾','🥎','🎾','🏐','🏉','🥏','🎱','🏓','🏸','🏒','🏑','🥍','🏏','🪃','🥅','⛳','🪁','🏹','🎣','🤿','🥊','🥋','🎽','🛹','🛼','🛷','⛸️','🥌','🎿','⛷️','🏂','🪂','🏋️','🤼','🤸','🤺','🏇','⛹️','🤾','🏌️','🏄','🚣','🧗','🚵','🚴','🏆','🥇','🥈','🥉','🏅','🎖️','🏵️','🎗️','🎫','🎟️','🎪','🤹','🎭','🩰','🎨','🎬','🎤','🎧','🎼','🎹','🥁','🪘','🎷','🎺','🎸','🪕','🎻','🎲','♟️','🎯','🎳','🎮','🎰','🧩'] },
  { name: 'travel', icon: '✈️', emojis: ['✈️','🚀','🛸','🚁','🛺','🚂','🚃','🚄','🚅','🚆','🚇','🚈','🚉','🚊','🚝','🚞','🚋','🚌','🚍','🚎','🚐','🚑','🚒','🚓','🚔','🚕','🚖','🚗','🚘','🚙','🛻','🚚','🚛','🚜','🏎️','🏍️','🛵','🦽','🦼','🛺','🚲','🛴','🛹','🛼','🚏','🛣️','🛤️','⛽','🚨','🚥','🚦','🛑','🚧','⚓','🪝','⛵','🚤','🛥️','🛳️','⛴️','🚢','🛟','🪂','💺','🚁','🛸','🪐','🌍','🌎','🌏','🗺️','🧭','🏔️','⛰️','🌋','🗻','🏕️','🏖️','🏜️','🏝️','🏞️','🏟️','🏛️','🏗️','🧱','🪨','🪵'] },
]

const currentEmojis = computed(() => {
  return emojiCategories.find(c => c.name === activeEmojiCategory.value)?.emojis || []
})

function insertEmoji(emoji) {
  newMessage.value += emoji
}

function openImagePicker() {
  if (!fileInputRef.value) return
  fileInputRef.value.accept = 'image/*'
  fileInputRef.value.click()
}

function openAudioPicker() {
  if (!fileInputRef.value) return
  fileInputRef.value.accept = 'audio/*'
  fileInputRef.value.click()
}

function openVideoPicker() {
  if (!fileInputRef.value) return
  fileInputRef.value.accept = 'video/*'
  fileInputRef.value.click()
}

function openDocPicker() {
  if (!fileInputRef.value) return
  fileInputRef.value.accept = '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar'
  fileInputRef.value.click()
}

function startReply(msg) {
  replyingTo.value = msg
  activeMessageMenuId.value = ''
  // focus textarea
  nextTick(() => {
    const ta = document.querySelector('textarea[placeholder="Type..."]')
    if (ta) ta.focus()
  })
}

function openReactionPicker(msg) {
  reactionPickerMsgId.value = reactionPickerMsgId.value === msg.id ? '' : msg.id
}

function sendReaction(msg, emoji) {
  if (!msg.id) return
  const reactions = messageReactions.value[msg.id] || {}
  const users = reactions[emoji] ? [...reactions[emoji]] : []
  const idx = users.indexOf(session.user)
  if (idx === -1) {
    users.push(session.user)
  } else {
    users.splice(idx, 1)
  }
  const updated = { ...reactions, [emoji]: users }
  // remove emoji key if no users
  if (!updated[emoji].length) delete updated[emoji]
  messageReactions.value = { ...messageReactions.value, [msg.id]: updated }
}
const lastSeen = ref(JSON.parse(localStorage.getItem('lastSeen') || '{}'))
const selectedUserName = ref(localStorage.getItem(SELECTED_USER_KEY) || '')
const recentCallLogs = ref([])
const recentCallSummary = ref({ call_count: 0, missed_calls: 0 })
const sidebarExpanded = ref(false)
const deletingCallId = ref('')
const deletingSelectedCallLogsState = ref(false)
const clearingCallLogs = ref(false)
const toast = useToast()

const currentUserName = computed(() => {
  const user = allUsers.value.find(entry => entry.name === session.user)
  if (user?.full_name) return user.full_name
  if (user?.first_name) return user.first_name
  return session.user ? session.user.split('@')[0] : 'User'
})

const currentUserInitials = computed(() => initials(currentUserName.value))
const canSendMessage = computed(
  () => Boolean(selectedUser.value)
    && !sending.value
    && !uploadingAttachment.value
    && Boolean(newMessage.value.trim() || pendingAttachment.value)
)

const unreadCount = computed(() => {
  const counts = {}
  for (const user of allUsers.value) {
    const lastSeenTime = lastSeen.value[user.name] || 0
    const lastMessageTime = Date.parse(lastMessageMap.value[user.name]?.timestamp || 0) || 0
    if (lastMessageTime > lastSeenTime && user.name !== selectedUser.value?.name) {
      counts[user.name] = 1
    }
  }
  return counts
})

const sidebarUsers = computed(() => {
  const self = {
    name: session.user,
    full_name: currentUserName.value,
    first_name: currentUserName.value,
  }
  return [self, ...allUsers.value]
})

const filteredUsers = computed(() => {
  const query = search.value.toLowerCase().trim()
  const users = [...sidebarUsers.value]

  const filtered = query
    ? users.filter(user =>
        (user.full_name || user.first_name || user.name).toLowerCase().includes(query)
      )
    : users

  return filtered.sort((left, right) => {
    const leftTime = Date.parse(lastMessageMap.value[left.name]?.timestamp || 0) || 0
    const rightTime = Date.parse(lastMessageMap.value[right.name]?.timestamp || 0) || 0
    return rightTime - leftTime
  })
})

const sidebarCallLogs = computed(() =>
  recentCallLogs.value.map(log => {
    const peer = resolveUser(log.peer)
    return {
      ...log,
      peer_name: peer.full_name || peer.first_name || peer.name || log.peer,
    }
  })
)

const forwardTargets = computed(() => {
  const query = forwardSearch.value.toLowerCase().trim()

  return allUsers.value
    .filter(user => {
      if (!user?.name || user.name === session.user) return false
      if (!query) return true
      return [user.full_name, user.first_name, user.name]
        .filter(Boolean)
        .some(value => value.toLowerCase().includes(query))
    })
    .sort((left, right) => {
      const leftLabel = (left.full_name || left.first_name || left.name || '').toLowerCase()
      const rightLabel = (right.full_name || right.first_name || right.name || '').toLowerCase()
      return leftLabel.localeCompare(rightLabel)
    })
})

function resolveUser(userId) {
  return (
    allUsers.value.find(entry => entry.name === userId) || {
      name: userId,
      full_name: userId,
      first_name: userId,
    }
  )
}

const {
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
} = useCallManager({
  resolveUser,
  onCallStateChange: () => {
    refreshSidebarCallLogs().catch(() => null)
    if (selectedUser.value?.name) {
      refreshCallLogs(selectedUser.value.name).catch(() => null)
    }
  },
  onIncomingCall: call => {
    if (call?.remoteUser) {
      focusPeer(call.remoteUser)
    }
  },
})

const callStatusLabel = computed(() => {
  if (callStatus.value === 'connected') return `Connected · ${durationText.value}`
  if (callStatus.value === 'connecting') return 'Connecting'
  if (callStatus.value === 'incoming') return 'Incoming call'
  if (callStatus.value === 'ringing') return 'Ringing'
  return 'Idle'
})

function initials(name) {
  if (!name) return '?'
  return name
    .trim()
    .split(/\s+/)
    .map(part => part[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

const COLORS = ['#25D366', '#128C7E', '#075E54', '#34B7F1', '#0084ff', '#7b68ee', '#ff6b6b', '#ffa500']

function avatarColor(name) {
  let hash = 0
  for (const char of name || '') hash = char.charCodeAt(0) + ((hash << 5) - hash)
  return COLORS[Math.abs(hash) % COLORS.length]
}

function formatTime(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatDateLabel(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value

  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  if (date.toDateString() === today.toDateString()) return 'Today'
  if (date.toDateString() === yesterday.toDateString()) return 'Yesterday'
  return date.toLocaleDateString([], {
    weekday: 'long',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function guessAttachmentKind(attachment) {
  const mimeType = (attachment?.mime_type || '').toLowerCase()
  if (mimeType.startsWith('image/')) return 'image'
  if (mimeType.startsWith('video/')) return 'video'
  if (mimeType.startsWith('audio/')) return 'audio'
  return attachment?.media_kind || 'file'
}

function normalizeAttachment(attachment) {
  if (!attachment?.file_url) return null

  return {
    file_name: attachment.file_name || attachment.file_url.split('/').pop() || 'Attachment',
    file_size: Number(attachment.file_size) || 0,
    file_url: attachment.file_url,
    media_kind: guessAttachmentKind(attachment),
    mime_type: attachment.mime_type || '',
  }
}

function buildAttachmentPreviewLabel(attachment) {
  if (!attachment) return ''
  if (attachment.media_kind === 'image') return 'Photo'
  if (attachment.media_kind === 'video') return 'Video'
  if (attachment.media_kind === 'audio') return 'Audio'
  return attachment.file_name || 'File'
}

function formatFileSize(size) {
  const bytes = Number(size) || 0
  if (!bytes) return '0 B'
  if (bytes >= 1024 * 1024) {
    return `${(bytes / (1024 * 1024)).toFixed(bytes >= 10 * 1024 * 1024 ? 0 : 1)} MB`
  }
  if (bytes >= 1024) {
    return `${Math.round(bytes / 1024)} KB`
  }
  return `${bytes} B`
}

function formatMessagePreview(data) {
  const attachment = normalizeAttachment(data?.attachment)
  const text = typeof data?.message === 'string' ? data.message.trim() : ''
  return text || buildAttachmentPreviewLabel(attachment)
}

function normalizeMessageData(data) {
  const attachment = normalizeAttachment(data?.attachment)
  const message = typeof data?.message === 'string' ? data.message : ''

  return {
    attachment,
    deleted_for_everyone: Boolean(data?.deleted_for_everyone),
    edited: Boolean(data?.edited),
    edited_at: data?.edited_at || '',
    forwarded: Boolean(data?.forwarded),
    id: data?.id || '',
    message,
    message_type: data?.message_type || (attachment ? (message ? 'mixed' : 'attachment') : 'text'),
    preview_text: typeof data?.preview_text === 'string' && data.preview_text.trim()
      ? data.preview_text
      : formatMessagePreview({ attachment, message }),
    sender: data?.sender || '',
    timestamp: data?.timestamp || '',
  }
}

function normalizeMessageGroups(groups) {
  return (groups || []).map(group => ({
    ...group,
    messages: (group.messages || []).map(normalizeMessageData),
  }))
}

function isOwnMessage(message) {
  return message?.sender === session.user
}

function messageBubbleClass(message) {
  if (message?.deleted_for_everyone) {
    return isOwnMessage(message)
      ? 'border border-emerald-200 bg-emerald-50 text-emerald-800'
      : 'border border-gray-200 bg-white/95 text-gray-500'
  }
  return isOwnMessage(message) ? 'bg-green-500 text-white' : 'bg-white text-gray-800'
}

function attachmentCardClass(message) {
  return isOwnMessage(message)
    ? 'border-white/20 bg-white/10 text-white'
    : 'border-gray-200 bg-gray-50 text-gray-800'
}

function attachmentMetaClass(message) {
  return isOwnMessage(message) ? 'text-white/70' : 'text-gray-500'
}

function fileExtensionLabel(attachment) {
  const extension = (attachment?.file_name || '').split('.').pop()
  if (!extension || extension === attachment?.file_name) return 'FI'
  return extension.slice(0, 2).toUpperCase()
}

function isImageMessage(message) {
  return message?.attachment?.media_kind === 'image'
}

function isVideoMessage(message) {
  return message?.attachment?.media_kind === 'video'
}

function isAudioMessage(message) {
  return message?.attachment?.media_kind === 'audio'
}

function showsInlineAttachmentActions(message) {
  return Boolean(message?.attachment) && (isImageMessage(message) || isVideoMessage(message) || isAudioMessage(message))
}

function deletedMessageLabel(message) {
  return isOwnMessage(message) ? 'You deleted this message' : 'This message was deleted'
}

function canEditMessage(message) {
  return Boolean(message?.id) && isOwnMessage(message) && !message?.deleted_for_everyone
}

function canDeleteForMe(message) {
  return Boolean(message?.id)
}

function canDeleteForEveryone(message) {
  return Boolean(message?.id) && isOwnMessage(message) && !message?.deleted_for_everyone
}

function canForwardMessage(message) {
  return Boolean(message?.id) && !message?.deleted_for_everyone
}

function canDownloadAttachment(message) {
  return Boolean(message?.attachment?.file_url) && !message?.deleted_for_everyone
}

function isMessageActionBusy(messageId) {
  return messageActionBusyId.value === messageId
}

function toggleMessageMenu(messageId) {
  if (!messageId) return
  activeMessageMenuId.value = activeMessageMenuId.value === messageId ? '' : messageId
}

function closeMessageMenu() {
  activeMessageMenuId.value = ''
}

function startEditingMessage(message) {
  if (!canEditMessage(message)) return
  editingMessageId.value = message.id
  editingMessageText.value = message.message || ''
  closeMessageMenu()
}

function cancelEditingMessage() {
  editingMessageId.value = ''
  editingMessageText.value = ''
}

function openForwardModal(message) {
  if (!canForwardMessage(message)) return
  forwardingMessage.value = {
    ...message,
    attachment: message.attachment ? { ...message.attachment } : null,
  }
  forwardSearch.value = ''
  closeMessageMenu()
}

function closeForwardModal(force = false) {
  if (forwardingState.value && !force) return
  forwardingMessage.value = null
  forwardSearch.value = ''
}

function resetMessageUiState() {
  closeMessageMenu()
  cancelEditingMessage()
  closeForwardModal(true)
}

function forwardMessagePreview(message) {
  if (!message) return ''
  if (message.deleted_for_everyone) return 'Deleted message'

  const attachmentLabel = buildAttachmentPreviewLabel(message.attachment)
  if (message.message && attachmentLabel) {
    return `${attachmentLabel} · ${message.message}`
  }

  return message.message || attachmentLabel || 'Message'
}

function buildPendingAttachmentMeta() {
  if (!pendingAttachment.value) return ''
  const previewLabel = buildAttachmentPreviewLabel(pendingAttachment.value)
  const fileSize = pendingAttachment.value.file_size ? ` · ${formatFileSize(pendingAttachment.value.file_size)}` : ''
  return `${previewLabel}${fileSize}`
}

function extractErrorMessage(error, fallback) {
  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message
  }

  if (Array.isArray(error?.messages) && error.messages.length) {
    return error.messages[0]
  }

  if (typeof error?._server_messages === 'string') {
    try {
      const serverMessages = JSON.parse(error._server_messages)
      const firstMessage = serverMessages[0]
      if (typeof firstMessage === 'string') {
        try {
          const parsedMessage = JSON.parse(firstMessage)
          if (typeof parsedMessage?.message === 'string' && parsedMessage.message.trim()) {
            return parsedMessage.message
          }
        } catch {
          if (firstMessage.trim()) return firstMessage
        }
      }
    } catch {
      // no-op
    }
  }

  return fallback
}

async function refreshSidebarCallLogs() {
  try {
    const response = await frappeRequest({
      url: 'fun.api.get_call_logs',
      params: { limit: 10 },
    })

    recentCallLogs.value = response.logs || []
    recentCallSummary.value = response.summary || { call_count: 0, missed_calls: 0 }
  } catch (error) {
    console.error('[chat] failed to refresh sidebar call logs', error)
  }
}

async function refreshConversationPreviews() {
  try {
    const conversations = await frappeRequest({
      url: 'fun.api.get_conversations',
    })

    const nextMap = {}
    for (const conversation of conversations || []) {
      nextMap[conversation.peer] = {
        last_message: conversation.last_message,
        timestamp: conversation.timestamp,
      }
    }
    lastMessageMap.value = nextMap
  } catch (error) {
    console.error('[chat] failed to refresh conversation previews', error)
  }
}

function refreshCurrentChat() {
  if (!selectedUser.value?.name) return
  messagesResource.submit({ other_user: selectedUser.value.name })
}

async function deleteCallLog(callId) {
  if (!callId || deletingCallId.value || clearingCallLogs.value || deletingSelectedCallLogsState.value) return

  if (!window.confirm('Delete this call log?')) return

  deletingCallId.value = callId

  try {
    await frappeRequest({
      url: 'fun.api.delete_call_log',
      params: { call_id: callId },
    })

    await refreshSidebarCallLogs()
    if (selectedUser.value?.name) {
      await refreshCallLogs(selectedUser.value.name).catch(() => null)
    }
    toast.success('Call log deleted')
  } catch (error) {
    console.error('[chat] failed to delete call log', error)
    toast.error(extractErrorMessage(error, 'Unable to delete call log'))
  } finally {
    deletingCallId.value = ''
  }
}

async function deleteSelectedCallLogs(callIds) {
  const normalizedCallIds = Array.isArray(callIds)
    ? [...new Set(callIds.filter(Boolean))]
    : []

  if (!normalizedCallIds.length || deletingSelectedCallLogsState.value || clearingCallLogs.value || deletingCallId.value) {
    return
  }

  const confirmationMessage = normalizedCallIds.length === 1
    ? 'Delete 1 selected call log?'
    : `Delete ${normalizedCallIds.length} selected call logs?`

  if (!window.confirm(confirmationMessage)) return

  deletingSelectedCallLogsState.value = true

  try {
    let deletedCount = 0
    let skippedActiveCount = 0
    let failedCount = 0
    let lastError = null

    for (const callId of normalizedCallIds) {
      try {
        await frappeRequest({
          url: 'fun.api.delete_call_log',
          params: { call_id: callId },
        })
        deletedCount += 1
      } catch (error) {
        const message = extractErrorMessage(error, '')
        if (/active calls cannot be deleted/i.test(message)) {
          skippedActiveCount += 1
        } else {
          failedCount += 1
          lastError = error
        }
      }
    }

    await refreshSidebarCallLogs()
    if (selectedUser.value?.name) {
      await refreshCallLogs(selectedUser.value.name).catch(() => null)
    }

    if (deletedCount) {
      toast.success(
        deletedCount === 1
          ? '1 call log deleted'
          : `${deletedCount} call logs deleted`
      )
    } else {
      toast.info('No call logs were deleted')
    }

    if (skippedActiveCount) {
      toast.info(
        skippedActiveCount === 1
          ? '1 active call log was skipped'
          : `${skippedActiveCount} active call logs were skipped`
      )
    }

    if (failedCount) {
      toast.error(
        failedCount === 1
          ? extractErrorMessage(lastError, '1 call log could not be deleted')
          : `${failedCount} call logs could not be deleted`
      )
    }
  } catch (error) {
    console.error('[chat] failed to delete selected call logs', error)
    toast.error(extractErrorMessage(error, 'Unable to delete selected call logs'))
  } finally {
    deletingSelectedCallLogsState.value = false
  }
}

async function clearAllCallLogs() {
  if (!recentCallLogs.value.length || clearingCallLogs.value || deletingCallId.value || deletingSelectedCallLogsState.value) return

  if (!window.confirm('Delete all call logs?')) return

  clearingCallLogs.value = true

  try {
    const response = await frappeRequest({
      url: 'fun.api.clear_call_logs',
      params: {},
    })

    await refreshSidebarCallLogs()
    if (selectedUser.value?.name) {
      await refreshCallLogs(selectedUser.value.name).catch(() => null)
    }

    if (response?.deleted_count) {
      toast.success(
        response.deleted_count === 1
          ? '1 call log deleted'
          : `${response.deleted_count} call logs deleted`
      )
    } else {
      toast.info('No call logs were deleted')
    }

    if (response?.skipped_active_count) {
      toast.info(
        response.skipped_active_count === 1
          ? '1 active call log was skipped'
          : `${response.skipped_active_count} active call logs were skipped`
      )
    }
  } catch (error) {
    console.error('[chat] failed to clear call logs', error)
    toast.error(extractErrorMessage(error, 'Unable to clear call logs'))
  } finally {
    clearingCallLogs.value = false
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
  }
}


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
    for (const conversation of data || []) {
      map[conversation.peer] = {
        last_message: conversation.last_message,
        timestamp: conversation.timestamp,
      }
    }
    lastMessageMap.value = map
  },
})

const messagesResource = createResource({
  url: 'fun.api.get_messages',
  onSuccess(data) {
    messageGroups.value = normalizeMessageGroups(data || [])
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
    const normalizedMessage = normalizeMessageData(data)
    appendMessage(normalizedMessage, data)
    sending.value = false
    lastOutgoingDraft.value = null
    const peer = data.receiver === session.user ? data.sender : data.receiver
    lastMessageMap.value = {
      ...lastMessageMap.value,
      [peer]: { last_message: normalizedMessage.preview_text, timestamp: data.timestamp },
    }
  },
  onError(error) {
    sending.value = false
    if (lastOutgoingDraft.value) {
      newMessage.value = lastOutgoingDraft.value.message
      pendingAttachment.value = lastOutgoingDraft.value.attachment
      lastOutgoingDraft.value = null
    }
    toast.error(extractErrorMessage(error, 'Unable to send message'))
  },
})

function appendMessage(data, source = data) {
  const groups = JSON.parse(JSON.stringify(messageGroups.value))
  const lastGroup = groups[groups.length - 1]
  const nextMessage = normalizeMessageData(data)

  if (lastGroup && lastGroup.conversation_name === source.conversation_name) {
    const alreadyPresent = lastGroup.messages.some(
      message => (
        (message.id && nextMessage.id && message.id === nextMessage.id) || (
          message.sender === nextMessage.sender &&
          message.message === nextMessage.message &&
          JSON.stringify(message.attachment || null) === JSON.stringify(nextMessage.attachment || null) &&
          message.timestamp === nextMessage.timestamp
        )
      )
    )

    if (alreadyPresent) {
      messageGroups.value = groups
      scrollToBottom()
      return
    }

    lastGroup.messages = [
      ...lastGroup.messages,
      nextMessage,
    ]
  } else {
    groups.push({
      conversation_name: source.conversation_name,
      start_date: source.start_date,
      messages: [nextMessage],
    })
  }

  messageGroups.value = groups
  scrollToBottom()
}

function persistSelectedUser(userName = '') {
  selectedUserName.value = userName
  if (userName) {
    localStorage.setItem(SELECTED_USER_KEY, userName)
  } else {
    localStorage.removeItem(SELECTED_USER_KEY)
  }
}

function updateLastSeen(userName) {
  if (!userName) return
  lastSeen.value = { ...lastSeen.value, [userName]: Date.now() }
  localStorage.setItem('lastSeen', JSON.stringify(lastSeen.value))
}

function loadSelectedChat(userName) {
  if (!userName) {
    messageGroups.value = []
    loadingMessages.value = false
    return
  }

  messageGroups.value = []
  loadingMessages.value = true
  messagesResource.submit({ other_user: userName })
  refreshCallLogs(userName).catch(() => null)
  updateLastSeen(userName)
}

function focusPeer(userName) {
  if (!userName) return
  const nextUser = resolveUser(userName)
  selectedUser.value = nextUser
  persistSelectedUser(nextUser.name)
}

function selectUser(user) {
  if (!user?.name) return
  focusPeer(user.name)
}

async function uploadChatFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch('/api/method/fun.api.upload_chat_file', {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'X-Frappe-CSRF-Token': window.csrf_token || '',
      'X-Requested-With': 'XMLHttpRequest',
    },
    credentials: 'include',
    body: formData,
  })

  const payload = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw payload
  }

  return normalizeAttachment(payload.message || payload)
}

function openAttachmentPicker() {
  if (!selectedUser.value || sending.value || uploadingAttachment.value) return
  fileInputRef.value?.click()
}

function removePendingAttachment() {
  pendingAttachment.value = null
  if (fileInputRef.value) {
    fileInputRef.value.value = ''
  }
}

async function handleAttachmentSelection(event) {
  const selectedFile = event.target?.files?.[0]
  if (!selectedFile) return

  uploadingAttachment.value = true

  try {
    pendingAttachment.value = await uploadChatFile(selectedFile)
  } catch (error) {
    console.error('[chat] failed to upload attachment', error)
    toast.error(extractErrorMessage(error, 'Unable to upload file'))
  } finally {
    uploadingAttachment.value = false
    if (event.target) {
      event.target.value = ''
    }
  }
}

function downloadAttachment(attachment) {
  if (!attachment?.file_url) return

  const link = document.createElement('a')
  link.href = attachment.file_url
  link.download = attachment.file_name || 'attachment'
  link.rel = 'noopener noreferrer'
  document.body.appendChild(link)
  link.click()
  link.remove()
}

async function saveEditedMessage(message) {
  if (!canEditMessage(message) || isMessageActionBusy(message.id)) return

  const nextMessage = editingMessageText.value.trim()
  if (!nextMessage && !message.attachment) {
    toast.error('Message cannot be empty')
    return
  }

  messageActionBusyId.value = message.id

  try {
    await frappeRequest({
      url: 'fun.api.edit_message',
      params: {
        message: nextMessage,
        message_id: message.id,
      },
    })

    cancelEditingMessage()
    closeMessageMenu()
    refreshCurrentChat()
    await refreshConversationPreviews()
    toast.success('Message updated')
  } catch (error) {
    console.error('[chat] failed to edit message', error)
    toast.error(extractErrorMessage(error, 'Unable to edit message'))
  } finally {
    messageActionBusyId.value = ''
  }
}

async function deleteMessageForMeAction(message) {
  if (!canDeleteForMe(message) || isMessageActionBusy(message.id)) return
  closeMessageMenu()

  if (!window.confirm('Delete this message only for you?')) return

  messageActionBusyId.value = message.id

  try {
    if (editingMessageId.value === message.id) {
      cancelEditingMessage()
    }

    await frappeRequest({
      url: 'fun.api.delete_message_for_me',
      params: { message_id: message.id },
    })

    refreshCurrentChat()
    await refreshConversationPreviews()
    toast.success('Message deleted for you')
  } catch (error) {
    console.error('[chat] failed to delete message for me', error)
    toast.error(extractErrorMessage(error, 'Unable to delete message'))
  } finally {
    messageActionBusyId.value = ''
  }
}

async function deleteMessageForEveryoneAction(message) {
  if (!canDeleteForEveryone(message) || isMessageActionBusy(message.id)) return
  closeMessageMenu()

  if (!window.confirm('Delete this message for everyone?')) return

  messageActionBusyId.value = message.id

  try {
    if (editingMessageId.value === message.id) {
      cancelEditingMessage()
    }

    await frappeRequest({
      url: 'fun.api.delete_message_for_everyone',
      params: { message_id: message.id },
    })

    refreshCurrentChat()
    await refreshConversationPreviews()
    toast.success('Message deleted for everyone')
  } catch (error) {
    console.error('[chat] failed to delete message for everyone', error)
    toast.error(extractErrorMessage(error, 'Unable to delete message'))
  } finally {
    messageActionBusyId.value = ''
  }
}

async function forwardSelectedMessage(user) {
  if (!forwardingMessage.value?.id || !user?.name || forwardingState.value) return

  forwardingState.value = true

  try {
    await frappeRequest({
      url: 'fun.api.forward_message',
      params: {
        message_id: forwardingMessage.value.id,
        receiver: user.name,
      },
    })

    closeForwardModal(true)
    await refreshConversationPreviews()
    toast.success(`Message forwarded to ${user.full_name || user.first_name || user.name}`)
  } catch (error) {
    console.error('[chat] failed to forward message', error)
    toast.error(extractErrorMessage(error, 'Unable to forward message'))
  } finally {
    forwardingState.value = false
  }
}

function sendMessage() {
  let text = newMessage.value.trim()
  const attachment = pendingAttachment.value ? { ...pendingAttachment.value } : null

  // prepend reply quote
  if (replyingTo.value && (text || attachment)) {
    const quoted = replyingTo.value.attachment
      ? `📎 ${replyingTo.value.attachment.file_name || 'Attachment'}`
      : (replyingTo.value.message || '')
    const senderLabel = replyingTo.value.sender === session.user
      ? 'You'
      : (selectedUser.value?.full_name || selectedUser.value?.name || replyingTo.value.sender)
    text = `> ${senderLabel}: ${quoted}\n${text}`
  }

  if ((!text && !attachment) || sending.value || uploadingAttachment.value || !selectedUser.value) return

  sending.value = true
  lastOutgoingDraft.value = {
    attachment,
    message: newMessage.value,
  }
  newMessage.value = ''
  pendingAttachment.value = null
  replyingTo.value = null
  stopTyping()

  const payload = {
    receiver: selectedUser.value.name,
    message: text,
  }
  if (attachment) {
    payload.attachment = JSON.stringify(attachment)
  }
  sendResource.submit(payload)
}

let typingTimeout = null
function handleWindowClick() {
  closeMessageMenu()
  showMoreMenu.value = false
  showEmojiPicker.value = false
  reactionPickerMsgId.value = ''
}

function handleWindowKeydown(event) {
  if (event.key !== 'Escape') return

  closeMessageMenu()
  showMoreMenu.value = false
  showEmojiPicker.value = false
  reactionPickerMsgId.value = ''
  replyingTo.value = null
  if (editingMessageId.value) {
    cancelEditingMessage()
  } else if (forwardingMessage.value) {
    closeForwardModal()
  }
}

const onTypingEvent = data => {
  typingUsers.value = { ...typingUsers.value, [data.from]: true }
}
const onStopTypingEvent = data => {
  typingUsers.value = { ...typingUsers.value, [data.from]: false }
}
const onUserOnline = data => {
  if (!onlineUsers.value.includes(data.user)) {
    onlineUsers.value = [...onlineUsers.value, data.user]
  }
}
const onUserOffline = data => {
  onlineUsers.value = onlineUsers.value.filter(user => user !== data.user)
}

function onTyping() {
  if (!selectedUser.value || !socket) return
  socket.emit('typing', { to: selectedUser.value.name })
  window.clearTimeout(typingTimeout)
  typingTimeout = window.setTimeout(stopTyping, 2000)
}

function stopTyping() {
  if (!selectedUser.value || !socket) return
  socket.emit('stop_typing', { to: selectedUser.value.name })
  window.clearTimeout(typingTimeout)
}

async function handleIncomingMessage(data) {
  if (!data?.sender) {
    return
  }
  const normalizedMessage = normalizeMessageData(data)
  const peer = data.sender === session.user ? data.receiver : data.sender
  lastMessageMap.value = {
    ...lastMessageMap.value,
    [peer]: { last_message: normalizedMessage.preview_text, timestamp: data.timestamp },
  }

  if (!selectedUser.value) {
    return
  }
  if (peer !== selectedUser.value.name) {
    return
  }

  messagesResource.submit({ other_user: peer })
}

function handleChatMessageUpdated(data) {
  if (!data?.sender) return

  const peer = data.sender === session.user ? data.receiver : data.sender
  if (selectedUser.value?.name === peer) {
    refreshCurrentChat()
  }
  refreshConversationPreviews().catch(() => null)
}

function handleRealtimeEnvelope(data) {
  if (!data?.event) return

  if (data.event === 'chat_message_updated') {
    handleChatMessageUpdated(data.data)
    return
  }

  if (data.event === 'new_message') {
    handleIncomingMessage(data.message)
    return
  }

  if (data.event === 'typing') {
    onTypingEvent(data.data)
    return
  }

  if (data.event === 'stop_typing') {
    onStopTypingEvent(data.data)
  }
}

function startVoiceCall() {
  if (!selectedUser.value) return
  startCall(selectedUser.value, 'audio').catch(console.error)
}

function startVideoCall() {
  if (!selectedUser.value) return
  startCall(selectedUser.value, 'video').catch(console.error)
}

function logout() {
  session.logout.submit()
}

watch(
  () => selectedUser.value?.name,
  userName => {
    resetMessageUiState()
    if (userName) {
      loadSelectedChat(userName)
    } else {
      messageGroups.value = []
      loadingMessages.value = false
    }
  },
  { immediate: true }
)

watch(
  allUsers,
  users => {
    const savedUserName = selectedUserName.value
    if (!savedUserName) {
      if (selectedUser.value?.name && !users.some(user => user.name === selectedUser.value.name)) {
        selectedUser.value = null
      }
      return
    }

    const matchedUser = users.find(user => user.name === savedUserName)
    if (!matchedUser) {
      if (users.length) {
        selectedUser.value = null
        persistSelectedUser('')
      }
      return
    }

    if (selectedUser.value?.name !== matchedUser.name) {
      selectedUser.value = matchedUser
      return
    }

    selectedUser.value = matchedUser
  },
  { immediate: true }
)

onMounted(() => {
  refreshSidebarCallLogs().catch(() => null)
  window.addEventListener('click', handleWindowClick)
  window.addEventListener('keydown', handleWindowKeydown)
  if (!socket) return

  socket.on('new_message', handleIncomingMessage)
  socket.on('realtime', handleRealtimeEnvelope)
  socket.on('typing', onTypingEvent)
  socket.on('stop_typing', onStopTypingEvent)
  socket.on('user_online', onUserOnline)
  socket.on('user_offline', onUserOffline)
})

onUnmounted(() => {
  window.removeEventListener('click', handleWindowClick)
  window.removeEventListener('keydown', handleWindowKeydown)
  if (socket) {
    socket.off('new_message', handleIncomingMessage)
    socket.off('realtime', handleRealtimeEnvelope)
    socket.off('typing', onTypingEvent)
    socket.off('stop_typing', onStopTypingEvent)
    socket.off('user_online', onUserOnline)
    socket.off('user_offline', onUserOffline)
  }
})
</script>
