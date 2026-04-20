<template>
  <!-- ════ DESKTOP SIDEBAR (md+) ════ -->
  <aside
    class="wa-sidebar relative z-30 hidden md:flex h-screen shrink-0 overflow-visible transition-[width] duration-300 ease-in-out"
    :class="expanded ? 'w-[340px]' : 'w-[60px]'"
  >
    <!-- ── Icon Rail ─────────────────────────────────────────────── -->
    <div class="wa-rail flex w-[60px] shrink-0 flex-col items-between justify-between py-3">

      <div class="flex flex-col items-center gap-1 pt-1">
        <!-- Chats -->
        <RailIcon :active="activeView === 'chats'" label="Chats" @click="openPanel('chats')">
          <svg viewBox="0 0 24 24" class="h-[22px] w-[22px]" fill="currentColor">
            <path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zm-2 10H6v-2h12v2zm0-3H6V7h12v2z"/>
          </svg>
        </RailIcon>

        <!-- Calls -->
        <RailIcon :active="activeView === 'calls'" label="Calls" @click="openPanel('calls')">
          <svg viewBox="0 0 24 24" class="h-[22px] w-[22px]" fill="currentColor">
            <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
          </svg>
        </RailIcon>


        <!-- <RailIcon :active="activeView === 'contacts'" label="Contacts" @click="openPanel('contacts')">
          <svg viewBox="0 0 24 24" height="24" width="24" preserveAspectRatio="xMidYMid meet" class="" fill="none"><title>status-refreshed</title><path d="M13.5628 3.13661C13.6587 2.59272 14.1794 2.22464 14.711 2.37436C15.7905 2.6784 16.8135 3.16254 17.736 3.80856C18.9323 4.64623 19.9305 5.73573 20.6606 7.00048C21.3907 8.26524 21.8349 9.67455 21.962 11.1294C22.0601 12.2513 21.9677 13.3794 21.6911 14.4662C21.5549 15.0014 20.9758 15.2682 20.4568 15.0792C19.9378 14.8903 19.677 14.317 19.7998 13.7785C19.9843 12.9693 20.0422 12.1343 19.9696 11.3035C19.8679 10.1396 19.5126 9.01217 18.9285 8.00036C18.3444 6.98856 17.5458 6.11696 16.5888 5.44682C15.9057 4.96842 15.1536 4.60099 14.3606 4.35609C13.8329 4.19312 13.4669 3.6805 13.5628 3.13661Z" fill="currentColor"></path><path d="M18.8944 17.785C19.3175 18.14 19.3759 18.7749 18.9804 19.1604C18.1774 19.9433 17.2466 20.5872 16.2259 21.0631C14.9023 21.6802 13.4597 22 11.9993 21.9999C10.5389 21.9998 9.09633 21.6798 7.77287 21.0625C6.7522 20.5864 5.82149 19.9424 5.01855 19.1594C4.62314 18.7739 4.68167 18.1389 5.10479 17.784C5.52792 17.4291 6.15484 17.4898 6.55976 17.8654C7.16828 18.4298 7.86245 18.8974 8.61829 19.25C9.67707 19.7438 10.8312 19.9998 11.9994 19.9999C13.1677 20 14.3218 19.7442 15.3807 19.2505C16.1366 18.898 16.8308 18.4304 17.4394 17.8661C17.8444 17.4906 18.4713 17.43 18.8944 17.785Z" fill="currentColor"></path><path d="M3.54277 15.0781C3.02379 15.267 2.4447 15.0001 2.30857 14.4649C2.03215 13.3781 1.9399 12.2501 2.03806 11.1283C2.16533 9.6736 2.60965 8.26443 3.33978 6.99982C4.06991 5.73521 5.06815 4.64585 6.26432 3.8083C7.1868 3.16239 8.20975 2.67832 9.28915 2.37433C9.82075 2.22461 10.3414 2.59269 10.4373 3.13659C10.5332 3.68048 10.1672 4.1931 9.6395 4.35605C8.84657 4.60092 8.09458 4.9683 7.41146 5.44662C6.45452 6.11666 5.65593 6.98815 5.07183 7.99983C4.48772 9.01152 4.13226 10.1389 4.03045 11.3026C3.95776 12.1334 4.01559 12.9683 4.19998 13.7774C4.3227 14.3159 4.06175 14.8892 3.54277 15.0781Z" fill="currentColor"></path><path fill-rule="evenodd" clip-rule="evenodd" d="M12.0001 16C14.2092 16 16.0001 14.2091 16.0001 12C16.0001 9.79086 14.2092 8 12.0001 8C9.79092 8 8.00006 9.79086 8.00006 12C8.00006 14.2091 9.79092 16 12.0001 16ZM12.0001 18C15.3138 18 18.0001 15.3137 18.0001 12C18.0001 8.68629 15.3138 6 12.0001 6C8.68635 6 6.00006 8.68629 6.00006 12C6.00006 15.3137 8.68635 18 12.0001 18Z" fill="currentColor"></path></svg>
        </RailIcon> -->

        <!-- Status -->
        <RailIcon :active="route.path === '/status'" label="Status" @click="goToStatus">
          <svg viewBox="0 0 24 24" height="24" width="24" preserveAspectRatio="xMidYMid meet" class="" fill="none"><title>status-refreshed</title><path d="M13.5628 3.13661C13.6587 2.59272 14.1794 2.22464 14.711 2.37436C15.7905 2.6784 16.8135 3.16254 17.736 3.80856C18.9323 4.64623 19.9305 5.73573 20.6606 7.00048C21.3907 8.26524 21.8349 9.67455 21.962 11.1294C22.0601 12.2513 21.9677 13.3794 21.6911 14.4662C21.5549 15.0014 20.9758 15.2682 20.4568 15.0792C19.9378 14.8903 19.677 14.317 19.7998 13.7785C19.9843 12.9693 20.0422 12.1343 19.9696 11.3035C19.8679 10.1396 19.5126 9.01217 18.9285 8.00036C18.3444 6.98856 17.5458 6.11696 16.5888 5.44682C15.9057 4.96842 15.1536 4.60099 14.3606 4.35609C13.8329 4.19312 13.4669 3.6805 13.5628 3.13661Z" fill="currentColor"></path><path d="M18.8944 17.785C19.3175 18.14 19.3759 18.7749 18.9804 19.1604C18.1774 19.9433 17.2466 20.5872 16.2259 21.0631C14.9023 21.6802 13.4597 22 11.9993 21.9999C10.5389 21.9998 9.09633 21.6798 7.77287 21.0625C6.7522 20.5864 5.82149 19.9424 5.01855 19.1594C4.62314 18.7739 4.68167 18.1389 5.10479 17.784C5.52792 17.4291 6.15484 17.4898 6.55976 17.8654C7.16828 18.4298 7.86245 18.8974 8.61829 19.25C9.67707 19.7438 10.8312 19.9998 11.9994 19.9999C13.1677 20 14.3218 19.7442 15.3807 19.2505C16.1366 18.898 16.8308 18.4304 17.4394 17.8661C17.8444 17.4906 18.4713 17.43 18.8944 17.785Z" fill="currentColor"></path><path d="M3.54277 15.0781C3.02379 15.267 2.4447 15.0001 2.30857 14.4649C2.03215 13.3781 1.9399 12.2501 2.03806 11.1283C2.16533 9.6736 2.60965 8.26443 3.33978 6.99982C4.06991 5.73521 5.06815 4.64585 6.26432 3.8083C7.1868 3.16239 8.20975 2.67832 9.28915 2.37433C9.82075 2.22461 10.3414 2.59269 10.4373 3.13659C10.5332 3.68048 10.1672 4.1931 9.6395 4.35605C8.84657 4.60092 8.09458 4.9683 7.41146 5.44662C6.45452 6.11666 5.65593 6.98815 5.07183 7.99983C4.48772 9.01152 4.13226 10.1389 4.03045 11.3026C3.95776 12.1334 4.01559 12.9683 4.19998 13.7774C4.3227 14.3159 4.06175 14.8892 3.54277 15.0781Z" fill="currentColor"></path><path fill-rule="evenodd" clip-rule="evenodd" d="M12.0001 16C14.2092 16 16.0001 14.2091 16.0001 12C16.0001 9.79086 14.2092 8 12.0001 8C9.79092 8 8.00006 9.79086 8.00006 12C8.00006 14.2091 9.79092 16 12.0001 16ZM12.0001 18C15.3138 18 18.0001 15.3137 18.0001 12C18.0001 8.68629 15.3138 6 12.0001 6C8.68635 6 6.00006 8.68629 6.00006 12C6.00006 15.3137 8.68635 18 12.0001 18Z" fill="currentColor"></path></svg>
        </RailIcon>
      </div>

      <!-- Bottom: profile avatar -->
      <div ref="profileMenuRef" class="relative flex justify-center">
        <transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="translate-y-2 opacity-0"
          enter-to-class="translate-y-0 opacity-100"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="translate-y-0 opacity-100"
          leave-to-class="translate-y-2 opacity-0"
        >
          <div
            v-if="showProfileMenu"
            class="wa-profile-popup absolute -bottom-1 left-[310%] z-50 w-60 -translate-x-1/2 rounded-2xl p-3 shadow-2xl"
            @click.stop
          >
            <p class="wa-profile-popup-title">Profile</p>
            <div class="wa-profile-popup-card mt-3 flex items-center gap-3 rounded-2xl px-3 py-3">
              <div
                class="flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold text-white"
                :style="{ background: avatarBg }"
              >
                {{ currentUserInitials }}
              </div>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold" style="color:#e9edef">{{ currentUserName }}</p>
                <p class="truncate text-xs" style="color:#8696a0">{{ currentUserEmail }}</p>
              </div>
            </div>
            <button
              type="button"
              class="wa-logout-btn mt-3 flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition"
              @click="handleLogout"
            >
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
              </svg>
              Logout
            </button>
          </div>
        </transition>

        <button
          type="button"
          class="wa-avatar-top mb-3 flex h-10 w-10 items-center justify-center rounded-full text-sm font-bold text-white"
          :style="{ background: avatarBg }"
          @click.stop="toggleProfileMenu"
          title="Profile"
        >
          {{ currentUserInitials }}
        </button>
      </div>
    </div>

    <!-- ── Expanded Panel ─────────────────────────────────────────── -->
    <div
      class="wa-panel flex min-w-0 flex-1 flex-col overflow-hidden transition-opacity duration-200"
      :class="expanded ? 'opacity-100' : 'pointer-events-none opacity-0'"
    >
      <!-- ══ CALLS PANEL ══ -->
      <template v-if="activeView === 'calls'">
        <!-- Header -->
        <div class="wa-panel-header flex items-center justify-between px-4 py-3">
          <h2 class="text-[19px] font-semibold wa-title">Calls</h2>
          <div class="flex items-center gap-1">
            <button type="button" class="wa-icon-btn" title="Search" @click="searchOpen = !searchOpen">
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                <path d="M15.5 14h-.79l-.28-.27A6.5 6.5 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
            </button>
            <div ref="callMenuRef" class="relative">
              <button
                type="button"
                class="wa-icon-btn"
                title="More options"
                :disabled="selectingCallLogs || !filteredLogs.length || callLogActionDisabled"
                @click.stop="toggleCallMenu"
              >
                <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                  <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                </svg>
              </button>
              <transition
                enter-active-class="transition duration-150 ease-out"
                enter-from-class="translate-y-1 opacity-0"
                enter-to-class="translate-y-0 opacity-100"
                leave-active-class="transition duration-100 ease-in"
                leave-from-class="translate-y-0 opacity-100"
                leave-to-class="translate-y-1 opacity-0"
              >
                <div
                  v-if="showCallMenu"
                  class="wa-menu-dropdown absolute right-0 top-11 z-30 min-w-[140px] rounded-xl py-2"
                  @click.stop
                >
                  <button
                    type="button"
                    class="wa-menu-item flex w-full items-center gap-2 px-3 py-2 text-left text-sm"
                    @click.stop="openDeleteSelection"
                  >
                    <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M3 6h18" stroke-linecap="round" />
                      <path d="M8 6V4h8v2" stroke-linecap="round" stroke-linejoin="round" />
                      <path d="M19 6l-1 14H6L5 6" stroke-linecap="round" stroke-linejoin="round" />
                      <path d="M10 11v6M14 11v6" stroke-linecap="round" />
                    </svg>
                    Delete
                  </button>
                </div>
              </transition>
            </div>
          </div>
        </div>

        <!-- Search bar -->
        <div v-if="searchOpen" class="wa-search-wrap px-3 pb-2">
          <div class="wa-search-bar flex items-center gap-2 rounded-lg px-3 py-2">
            <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0 wa-search-icon" fill="currentColor">
              <path d="M15.5 14h-.79l-.28-.27A6.5 6.5 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
            </svg>
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search in calls"
              class="wa-search-input flex-1 bg-transparent text-sm outline-none"
            />
          </div>
        </div>

        <!-- Stats row -->
        <div class="wa-stats-row mx-3 mb-2 mt-1 grid grid-cols-2 gap-2">
          <div class="wa-stat-card flex items-center gap-2.5 rounded-xl px-3 py-2.5">
            <div class="wa-stat-icon-wrap flex h-8 w-8 items-center justify-center rounded-full">
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
              </svg>
            </div>
            <div>
              <p class="wa-stat-label">Total</p>
              <p class="wa-stat-num">{{ callSummary.call_count || 0 }}</p>
            </div>
          </div>
          <div class="wa-stat-card missed flex items-center gap-2.5 rounded-xl px-3 py-2.5">
            <div class="wa-stat-icon-wrap missed flex h-8 w-8 items-center justify-center rounded-full">
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
              </svg>
            </div>
            <div>
              <p class="wa-stat-label missed">Missed</p>
              <p class="wa-stat-num missed">{{ callSummary.missed_calls || 0 }}</p>
            </div>
          </div>
        </div>

        <!-- Section label -->
        <div class="wa-section-label flex items-center justify-between px-4 py-1.5">
          <template v-if="selectingCallLogs">
            <button
              type="button"
              class="wa-select-toggle"
              :disabled="!visibleCallLogIds.length || callLogActionDisabled"
              @click.stop="toggleSelectAll"
            >
              <span class="wa-select-box" :class="{ 'is-selected': allVisibleSelected }">
                <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="3">
                  <path d="m5 12 4 4L19 6" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </span>
              <span>Select all</span>
              <span class="wa-selected-count">{{ selectedCount }} selected</span>
            </button>
            <div class="flex items-center gap-2">
              <button
                v-if="selectedCount"
                type="button"
                class="wa-header-delete-btn flex h-8 w-8 items-center justify-center rounded-full"
                :disabled="callLogActionDisabled"
                @click.stop="deleteSelectedCallLogs"
              >
                <svg v-if="deletingSelectedCallLogs" viewBox="0 0 24 24" class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 12a9 9 0 1 1-6.2-8.56" stroke-linecap="round" />
                </svg>
                <svg v-else viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18" stroke-linecap="round" />
                  <path d="M8 6V4h8v2" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M19 6l-1 14H6L5 6" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M10 11v6M14 11v6" stroke-linecap="round" />
                </svg>
              </button>
              <button type="button" class="wa-icon-btn" @click.stop="exitDeleteSelection">
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m6 6 12 12M18 6 6 18" stroke-linecap="round" />
                </svg>
              </button>
            </div>
          </template>
          <template v-else>
            <span>Recent</span>
            <span class="wa-section-count">{{ filteredLogs.length }}</span>
          </template>
        </div>

        <!-- Call log list -->
        <div class="flex-1 overflow-y-auto wa-scroll">
          <template v-if="filteredLogs.length">
            <button
              v-for="log in filteredLogs"
              :key="log.call_id"
              type="button"
              class="wa-call-row group relative flex w-full items-center gap-3 px-4 py-3 text-left"
              :class="{
                'wa-call-row-missed': isMissedCall(log),
                'wa-call-row-selected': selectingCallLogs && isCallLogSelected(log.call_id),
              }"
              @click="handleCallRowClick(log)"
            >
              <div v-if="selectingCallLogs" class="wa-checkbox-wrap flex h-5 w-5 shrink-0 items-center justify-center">
                <span class="wa-select-box" :class="{ 'is-selected': isCallLogSelected(log.call_id) }">
                  <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="3">
                    <path d="m5 12 4 4L19 6" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
              </div>
              <div
                class="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-semibold text-white"
                :style="{ background: avatarColor(log.peer) }"
              >
                {{ initials(log.peer_name || log.peer) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="truncate text-[15px] font-medium wa-call-name" :class="isMissedCall(log) ? 'wa-missed-text' : ''">
                  {{ log.peer_name || log.peer }}
                </p>
                <div class="mt-0.5 flex items-center gap-1">
                  <svg viewBox="0 0 24 24" class="h-3.5 w-3.5 shrink-0" :class="directionIconClass(log)" fill="currentColor">
                    <path v-if="log.direction === 'outgoing'" d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"/>
                    <path v-else d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"/>
                  </svg>
                  <span class="text-xs wa-call-meta" :class="isMissedCall(log) ? 'wa-missed-text' : ''">{{ callTypeLabel(log) }}</span>
                  <span class="text-xs wa-call-meta">· {{ formatTime(log.start_time || log.end_time) }}</span>
                  <span v-if="log.duration && log.status === 'Completed'" class="text-xs wa-call-meta">· {{ log.duration }}</span>
                </div>
              </div>
              <div v-if="!selectingCallLogs" class="flex items-center gap-1">
                <span
                  class="wa-cb-btn flex h-8 w-8 items-center justify-center rounded-full"
                  :class="log.call_type === 'Video' ? 'wa-cb-video' : 'wa-cb-audio'"
                  @click.stop="emit('call-peer', { peer: log.peer, type: log.call_type === 'Video' ? 'video' : 'audio' })"
                >
                  <svg v-if="log.call_type === 'Video'" viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                    <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                  </svg>
                  <svg v-else viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                    <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
                  </svg>
                </span>
              </div>
              <div class="wa-row-divider absolute bottom-0 left-[64px] right-0 h-px"></div>
            </button>
          </template>
          <div v-else class="flex flex-col items-center justify-center py-16 text-center">
            <div class="wa-empty-icon mb-4 flex h-16 w-16 items-center justify-center rounded-full">
              <svg viewBox="0 0 24 24" class="h-7 w-7" fill="currentColor" style="color:#8696a0">
                <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
              </svg>
            </div>
            <p class="text-[15px] font-medium" style="color:#e9edef">No recent calls</p>
            <p class="mt-1 text-sm" style="color:#8696a0">Call a contact to get started</p>
          </div>
        </div>
      </template>
    </div>
  </aside>

  <!-- ════ MOBILE BOTTOM NAV + PANEL (< md) ════ -->
  <div v-if="!chatOpen" class="md:hidden">

    <!-- Slide-up Panel Overlay -->
    <transition
      enter-active-class="transition duration-250 ease-out"
      enter-from-class="translate-y-full"
      enter-to-class="translate-y-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="translate-y-0"
      leave-to-class="translate-y-full"
    >
      <div
        v-if="mobileExpanded"
        class="fixed inset-0 z-40 flex flex-col overflow-hidden"
        style="background:#111b21; padding-bottom:64px"
      >
        <!-- Panel Header with back button -->
        <div class="wa-panel-header flex items-center gap-2 px-3 py-3">
          <button type="button" class="wa-icon-btn shrink-0" @click="closeMobilePanel">
            <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
              <path d="M20 11H7.83l5.59-5.59L12 4l-8 8 8 8 1.41-1.41L7.83 13H20v-2z"/>
            </svg>
          </button>
          <h2 class="wa-title flex-1 text-[18px] font-semibold">
            {{ mobileView === 'calls' ? 'Calls' : 'Contacts' }}
          </h2>

          <!-- Calls header actions -->
          <template v-if="mobileView === 'calls'">
            <button type="button" class="wa-icon-btn" @click="searchOpen = !searchOpen">
              <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                <path d="M15.5 14h-.79l-.28-.27A6.5 6.5 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
            </button>
            <div ref="callMenuRef" class="relative">
              <button
                type="button"
                class="wa-icon-btn"
                :disabled="selectingCallLogs || !filteredLogs.length || callLogActionDisabled"
                @click.stop="toggleCallMenu"
              >
                <svg viewBox="0 0 24 24" class="h-5 w-5" fill="currentColor">
                  <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"/>
                </svg>
              </button>
              <transition
                enter-active-class="transition duration-150 ease-out"
                enter-from-class="translate-y-1 opacity-0"
                enter-to-class="translate-y-0 opacity-100"
                leave-active-class="transition duration-100 ease-in"
                leave-from-class="translate-y-0 opacity-100"
                leave-to-class="translate-y-1 opacity-0"
              >
                <div
                  v-if="showCallMenu"
                  class="wa-menu-dropdown absolute right-0 top-11 z-30 min-w-[140px] rounded-xl py-2"
                  @click.stop
                >
                  <button
                    type="button"
                    class="wa-menu-item flex w-full items-center gap-2 px-3 py-2 text-left text-sm"
                    @click.stop="openDeleteSelection"
                  >
                    <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M3 6h18" stroke-linecap="round" />
                      <path d="M8 6V4h8v2" stroke-linecap="round" stroke-linejoin="round" />
                      <path d="M19 6l-1 14H6L5 6" stroke-linecap="round" stroke-linejoin="round" />
                      <path d="M10 11v6M14 11v6" stroke-linecap="round" />
                    </svg>
                    Delete
                  </button>
                </div>
              </transition>
            </div>
          </template>
        </div>

        <!-- Calls Panel Content -->
        <template v-if="mobileView === 'calls'">
          <!-- Search bar -->
          <div v-if="searchOpen" class="wa-search-wrap px-3 pb-2">
            <div class="wa-search-bar flex items-center gap-2 rounded-lg px-3 py-2">
              <svg viewBox="0 0 24 24" class="h-4 w-4 shrink-0 wa-search-icon" fill="currentColor">
                <path d="M15.5 14h-.79l-.28-.27A6.5 6.5 0 0 0 16 9.5 6.5 6.5 0 1 0 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search in calls"
                class="wa-search-input flex-1 bg-transparent text-sm outline-none"
              />
            </div>
          </div>

          <!-- Stats row -->
          <div class="wa-stats-row mx-3 mb-2 mt-1 grid grid-cols-2 gap-2">
            <div class="wa-stat-card flex items-center gap-2.5 rounded-xl px-3 py-2.5">
              <div class="wa-stat-icon-wrap flex h-8 w-8 items-center justify-center rounded-full">
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                  <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
                </svg>
              </div>
              <div>
                <p class="wa-stat-label">Total</p>
                <p class="wa-stat-num">{{ callSummary.call_count || 0 }}</p>
              </div>
            </div>
            <div class="wa-stat-card missed flex items-center gap-2.5 rounded-xl px-3 py-2.5">
              <div class="wa-stat-icon-wrap missed flex h-8 w-8 items-center justify-center rounded-full">
                <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                  <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
                </svg>
              </div>
              <div>
                <p class="wa-stat-label missed">Missed</p>
                <p class="wa-stat-num missed">{{ callSummary.missed_calls || 0 }}</p>
              </div>
            </div>
          </div>

          <!-- Section label -->
          <div class="wa-section-label flex items-center justify-between px-4 py-1.5">
            <template v-if="selectingCallLogs">
              <button
                type="button"
                class="wa-select-toggle"
                :disabled="!visibleCallLogIds.length || callLogActionDisabled"
                @click.stop="toggleSelectAll"
              >
                <span class="wa-select-box" :class="{ 'is-selected': allVisibleSelected }">
                  <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="3">
                    <path d="m5 12 4 4L19 6" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <span>Select all</span>
                <span class="wa-selected-count">{{ selectedCount }} selected</span>
              </button>
              <div class="flex items-center gap-2">
                <button
                  v-if="selectedCount"
                  type="button"
                  class="wa-header-delete-btn flex h-8 w-8 items-center justify-center rounded-full"
                  :disabled="callLogActionDisabled"
                  @click.stop="deleteSelectedCallLogs"
                >
                  <svg v-if="deletingSelectedCallLogs" viewBox="0 0 24 24" class="h-4 w-4 animate-spin" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 12a9 9 0 1 1-6.2-8.56" stroke-linecap="round" />
                  </svg>
                  <svg v-else viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M3 6h18" stroke-linecap="round" />
                    <path d="M8 6V4h8v2" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M19 6l-1 14H6L5 6" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M10 11v6M14 11v6" stroke-linecap="round" />
                  </svg>
                </button>
                <button type="button" class="wa-icon-btn" @click.stop="exitDeleteSelection">
                  <svg viewBox="0 0 24 24" class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="m6 6 12 12M18 6 6 18" stroke-linecap="round" />
                  </svg>
                </button>
              </div>
            </template>
            <template v-else>
              <span>Recent</span>
              <span class="wa-section-count">{{ filteredLogs.length }}</span>
            </template>
          </div>

          <!-- Call log list -->
          <div class="flex-1 overflow-y-auto wa-scroll">
            <template v-if="filteredLogs.length">
              <button
                v-for="log in filteredLogs"
                :key="log.call_id"
                type="button"
                class="wa-call-row group relative flex w-full items-center gap-3 px-4 py-3 text-left"
                :class="{
                  'wa-call-row-missed': isMissedCall(log),
                  'wa-call-row-selected': selectingCallLogs && isCallLogSelected(log.call_id),
                }"
                @click="handleCallRowClick(log)"
              >
                <div v-if="selectingCallLogs" class="wa-checkbox-wrap flex h-5 w-5 shrink-0 items-center justify-center">
                  <span class="wa-select-box" :class="{ 'is-selected': isCallLogSelected(log.call_id) }">
                    <svg viewBox="0 0 24 24" class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="3">
                      <path d="m5 12 4 4L19 6" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                  </span>
                </div>
                <div
                  class="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-full text-sm font-semibold text-white"
                  :style="{ background: avatarColor(log.peer) }"
                >
                  {{ initials(log.peer_name || log.peer) }}
                </div>
                <div class="min-w-0 flex-1">
                  <p class="truncate text-[15px] font-medium wa-call-name" :class="isMissedCall(log) ? 'wa-missed-text' : ''">
                    {{ log.peer_name || log.peer }}
                  </p>
                  <div class="mt-0.5 flex items-center gap-1">
                    <svg viewBox="0 0 24 24" class="h-3.5 w-3.5 shrink-0" :class="directionIconClass(log)" fill="currentColor">
                      <path v-if="log.direction === 'outgoing'" d="M4 12l1.41 1.41L11 7.83V20h2V7.83l5.58 5.59L20 12l-8-8-8 8z"/>
                      <path v-else d="M20 12l-1.41-1.41L13 16.17V4h-2v12.17l-5.58-5.59L4 12l8 8 8-8z"/>
                    </svg>
                    <span class="text-xs wa-call-meta" :class="isMissedCall(log) ? 'wa-missed-text' : ''">
                      {{ callTypeLabel(log) }}
                    </span>
                    <span class="text-xs wa-call-meta">· {{ formatTime(log.start_time || log.end_time) }}</span>
                    <span v-if="log.duration && log.status === 'Completed'" class="text-xs wa-call-meta">· {{ log.duration }}</span>
                  </div>
                </div>
                <div v-if="!selectingCallLogs" class="flex items-center gap-1">
                  <span
                    class="wa-cb-btn flex h-8 w-8 items-center justify-center rounded-full"
                    :class="log.call_type === 'Video' ? 'wa-cb-video' : 'wa-cb-audio'"
                    @click.stop="emit('call-peer', { peer: log.peer, type: log.call_type === 'Video' ? 'video' : 'audio' })"
                  >
                    <svg v-if="log.call_type === 'Video'" viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                      <path d="M17 10.5V7c0-.55-.45-1-1-1H4c-.55 0-1 .45-1 1v10c0 .55.45 1 1 1h12c.55 0 1-.45 1-1v-3.5l4 4v-11l-4 4z"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                      <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
                    </svg>
                  </span>
                </div>
                <div class="wa-row-divider absolute bottom-0 left-[64px] right-0 h-px"></div>
              </button>
            </template>
            <div v-else class="flex flex-col items-center justify-center py-16 text-center">
              <div class="wa-empty-icon mb-4 flex h-16 w-16 items-center justify-center rounded-full">
                <svg viewBox="0 0 24 24" class="h-7 w-7" fill="currentColor" style="color:#8696a0">
                  <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
                </svg>
              </div>
              <p class="text-[15px] font-medium" style="color:#e9edef">No recent calls</p>
              <p class="mt-1 text-sm" style="color:#8696a0">Call a contact to get started</p>
            </div>
          </div>
        </template>

        <!-- Contacts placeholder -->
        <template v-else-if="mobileView === 'contacts'">
          <div class="flex flex-1 flex-col items-center justify-center gap-3 text-center">
            <div class="wa-empty-icon flex h-16 w-16 items-center justify-center rounded-full">
              <svg viewBox="0 0 24 24" class="h-7 w-7" fill="currentColor" style="color:#8696a0">
                <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
              </svg>
            </div>
            <p class="text-[15px] font-medium" style="color:#e9edef">Contacts</p>
            <p class="text-sm" style="color:#8696a0">Coming soon</p>
          </div>
        </template>
      </div>
    </transition>

    <!-- ── Fixed Bottom Nav Bar ──────────────────────────────────── -->
    <nav
      class="fixed bottom-0 left-0 right-0 z-50 flex h-16 items-center justify-around"
      style="background:#202c33; border-top:1px solid rgba(255,255,255,0.07)"
    >
      <!-- Chats -->
      <button
        type="button"
        class="flex flex-col items-center gap-0.5 px-3 py-1 transition-colors"
        :style="{ color: !mobileExpanded ? '#00a884' : '#8696a0' }"
        @click="closeMobilePanel"
      >
        <svg viewBox="0 0 24 24" class="h-6 w-6" fill="currentColor">
          <path d="M20 2H4a2 2 0 0 0-2 2v18l4-4h14a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zm-2 10H6v-2h12v2zm0-3H6V7h12v2z"/>
        </svg>
        <span class="text-[10px] font-medium">Chats</span>
      </button>

      <!-- Calls -->
      <button
        type="button"
        class="flex flex-col items-center gap-0.5 px-3 py-1 transition-colors"
        :style="{ color: mobileExpanded && mobileView === 'calls' ? '#00a884' : '#8696a0' }"
        @click="openMobilePanel('calls')"
      >
        <svg viewBox="0 0 24 24" class="h-6 w-6" fill="currentColor">
          <path d="M6.6 10.8c1.4 2.8 3.8 5.1 6.6 6.6l2.2-2.2c.3-.3.7-.4 1-.2 1.1.4 2.3.6 3.6.6.6 0 1 .4 1 1V20c0 .6-.4 1-1 1C10.6 21 3 13.4 3 4c0-.6.4-1 1-1h3.5c.6 0 1 .4 1 1 0 1.3.2 2.5.6 3.6.1.3 0 .7-.2 1L6.6 10.8z"/>
        </svg>
        <span class="text-[10px] font-medium">Calls</span>
      </button>

      <!-- Contacts -->
      <button
        type="button"
        class="flex flex-col items-center gap-0.5 px-3 py-1 transition-colors"
        :style="{ color: mobileExpanded && mobileView === 'contacts' ? '#00a884' : '#8696a0' }"
        @click="openMobilePanel('contacts')"
      >
        <svg viewBox="0 0 24 24" class="h-6 w-6" fill="currentColor">
          <path d="M12 12c2.7 0 4.8-2.1 4.8-4.8S14.7 2.4 12 2.4 7.2 4.5 7.2 7.2 9.3 12 12 12zm0 2.4c-3.2 0-9.6 1.6-9.6 4.8v2.4h19.2v-2.4c0-3.2-6.4-4.8-9.6-4.8z"/>
        </svg>
        <span class="text-[10px] font-medium">Contacts</span>
      </button>

      <!-- Status -->
      <button
        type="button"
        class="flex flex-col items-center gap-0.5 px-3 py-1 transition-colors"
        :style="{ color: route.path === '/status' ? '#00a884' : '#8696a0' }"
        @click="goToStatusMobile"
      >
        <svg viewBox="0 0 24 24" class="h-6 w-6" fill="currentColor">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
        </svg>
        <span class="text-[10px] font-medium">Status</span>
      </button>

      <!-- Profile Avatar -->
      <div ref="mobileProfileRef" class="relative px-3 py-1">
        <transition
          enter-active-class="transition duration-150 ease-out"
          enter-from-class="translate-y-2 opacity-0"
          enter-to-class="translate-y-0 opacity-100"
          leave-active-class="transition duration-100 ease-in"
          leave-from-class="translate-y-0 opacity-100"
          leave-to-class="translate-y-2 opacity-0"
        >
          <div
            v-if="mobileProfileOpen"
            class="wa-profile-popup absolute bottom-full right-0 z-50 mb-2 w-60 rounded-2xl p-3 shadow-2xl"
            @click.stop
          >
            <p class="wa-profile-popup-title">Profile</p>
            <div class="wa-profile-popup-card mt-3 flex items-center gap-3 rounded-2xl px-3 py-3">
              <div
                class="flex h-11 w-11 items-center justify-center rounded-full text-sm font-bold text-white"
                :style="{ background: avatarBg }"
              >
                {{ currentUserInitials }}
              </div>
              <div class="min-w-0">
                <p class="truncate text-sm font-semibold" style="color:#e9edef">{{ currentUserName }}</p>
                <p class="truncate text-xs" style="color:#8696a0">{{ currentUserEmail }}</p>
              </div>
            </div>
            <button
              type="button"
              class="wa-logout-btn mt-3 flex w-full items-center justify-center gap-2 rounded-xl py-3 text-sm font-semibold transition"
              @click="handleLogout"
            >
              <svg viewBox="0 0 24 24" class="h-4 w-4" fill="currentColor">
                <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5-5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z"/>
              </svg>
              Logout
            </button>
          </div>
        </transition>

        <button
          type="button"
          class="wa-avatar-top flex h-9 w-9 items-center justify-center rounded-full text-sm font-bold text-white"
          :style="{ background: avatarBg }"
          @click.stop="toggleMobileProfile"
        >
          {{ currentUserInitials }}
        </button>
      </div>
    </nav>
  </div>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// ── Inline RailIcon component ────────────────────────────────────────
const RailIcon = defineComponent({
  props: { active: Boolean, label: String },
  emits: ['click'],
  setup(props, { emit, slots }) {
    return () =>
      h('button', {
        type: 'button',
        title: props.label,
        class: ['wa-rail-btn flex h-10 w-10 items-center justify-center rounded-full transition-all duration-150',
          props.active ? 'wa-rail-active' : 'wa-rail-inactive'],
        onClick: () => emit('click'),
      }, slots.default?.())
  },
})

// ── Props / Emits ────────────────────────────────────────────────────
const props = defineProps({
  callLogs:           { type: Array,  default: () => [] },
  callSummary:        { type: Object, default: () => ({ call_count: 0, missed_calls: 0 }) },
  currentUserEmail:   { type: String, default: '' },
  currentUserInitials:{ type: String, default: '?' },
  currentUserName:    { type: String, default: 'User' },
  deletingCallId:     { type: String, default: '' },
  deletingSelectedCallLogs: { type: Boolean, default: false },
  clearingCallLogs:   { type: Boolean, default: false },
  expanded:           { type: Boolean, default: false },
  chatOpen:           { type: Boolean, default: false },
})

// ── State ────────────────────────────────────────────────────────────
const activeView  = ref('calls')
const searchOpen  = ref(false)
const searchQuery = ref('')
const showProfileMenu = ref(false)
const profileMenuRef  = ref(null)
const showCallMenu    = ref(false)
const callMenuRef     = ref(null)
const selectingCallLogs  = ref(false)
const selectedCallIds    = ref([])

// Router
const router = useRouter()
const route  = useRoute()
function goToStatus() { router.push('/status') }
function goToStatusMobile() { closeMobilePanel(); router.push('/status') }

// Mobile state
const mobileExpanded    = ref(false)
const mobileView        = ref('calls')
const mobileProfileOpen = ref(false)
const mobileProfileRef  = ref(null)

// ── Computed ─────────────────────────────────────────────────────────
const avatarBg = computed(() => avatarColor(props.currentUserName))

const filteredLogs = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  if (!q) return props.callLogs
  return props.callLogs.filter(l =>
    (l.peer_name || l.peer || '').toLowerCase().includes(q)
  )
})

const visibleCallLogIds = computed(() =>
  filteredLogs.value.map(log => log.call_id).filter(Boolean)
)

const allVisibleSelected = computed(
  () => visibleCallLogIds.value.length > 0
    && visibleCallLogIds.value.every(callId => selectedCallIds.value.includes(callId))
)

const selectedCount = computed(() => selectedCallIds.value.length)
const callLogActionDisabled = computed(
  () => props.clearingCallLogs || Boolean(props.deletingCallId) || props.deletingSelectedCallLogs
)

const emit = defineEmits(['logout', 'select-peer', 'call-peer', 'toggle', 'delete-log', 'delete-selected', 'clear-logs'])

// ── Desktop Methods ──────────────────────────────────────────────────
function openPanel(view) {
  closeCallMenu()
  exitDeleteSelection()
  closeProfileMenu()
  if (props.expanded && activeView.value === view) {
    emit('toggle')
    return
  }
  activeView.value  = view
  searchOpen.value  = false
  searchQuery.value = ''
  if (!props.expanded) emit('toggle')
}

function closeProfileMenu() { showProfileMenu.value = false }

function toggleProfileMenu() {
  closeCallMenu()
  showProfileMenu.value = !showProfileMenu.value
}

function handleLogout() {
  closeCallMenu()
  closeProfileMenu()
  closeMobileProfile()
  emit('logout')
}

function closeCallMenu() { showCallMenu.value = false }

function toggleCallMenu() {
  if (selectingCallLogs.value || !filteredLogs.value.length || callLogActionDisabled.value) return
  closeProfileMenu()
  showCallMenu.value = !showCallMenu.value
}

function openDeleteSelection() {
  if (!filteredLogs.value.length || callLogActionDisabled.value) return
  closeCallMenu()
  selectedCallIds.value = []
  selectingCallLogs.value = true
}

function exitDeleteSelection() {
  closeCallMenu()
  selectingCallLogs.value = false
  selectedCallIds.value = []
}

function isCallLogSelected(callId) {
  return selectedCallIds.value.includes(callId)
}

function toggleCallSelection(callId) {
  if (!callId || callLogActionDisabled.value) return
  if (isCallLogSelected(callId)) {
    selectedCallIds.value = selectedCallIds.value.filter(id => id !== callId)
    return
  }
  selectedCallIds.value = [...selectedCallIds.value, callId]
}

function toggleSelectAll() {
  if (!visibleCallLogIds.value.length || callLogActionDisabled.value) return
  if (allVisibleSelected.value) {
    selectedCallIds.value = selectedCallIds.value.filter(id => !visibleCallLogIds.value.includes(id))
    return
  }
  const nextSelectedIds = new Set(selectedCallIds.value)
  visibleCallLogIds.value.forEach(callId => nextSelectedIds.add(callId))
  selectedCallIds.value = [...nextSelectedIds]
}

function handleCallRowClick(log) {
  if (selectingCallLogs.value) {
    toggleCallSelection(log.call_id)
    return
  }
  emit('select-peer', log.peer)
}

function deleteSelectedCallLogs() {
  if (!selectedCount.value || callLogActionDisabled.value) return
  emit('delete-selected', selectedCallIds.value.slice())
}

// ── Mobile Methods ───────────────────────────────────────────────────
function openMobilePanel(view) {
  mobileView.value = view
  mobileExpanded.value = true
  searchOpen.value  = false
  searchQuery.value = ''
  closeCallMenu()
}

function closeMobilePanel() {
  mobileExpanded.value = false
}

function toggleMobileProfile() {
  mobileProfileOpen.value = !mobileProfileOpen.value
}

function closeMobileProfile() {
  mobileProfileOpen.value = false
}

// ── Document click handler ───────────────────────────────────────────
function handleDocumentClick(event) {
  if (!profileMenuRef.value?.contains(event.target)) closeProfileMenu()
  if (!callMenuRef.value?.contains(event.target)) closeCallMenu()
  if (!mobileProfileRef.value?.contains(event.target)) closeMobileProfile()
}

// ── Watchers ─────────────────────────────────────────────────────────
watch(
  () => props.expanded,
  expanded => {
    if (expanded) { closeProfileMenu(); closeCallMenu() }
  }
)

watch(
  () => props.callLogs,
  logs => {
    const availableCallIds = new Set(logs.map(log => log.call_id))
    selectedCallIds.value = selectedCallIds.value.filter(callId => availableCallIds.has(callId))
    if (!logs.length) { closeCallMenu(); exitDeleteSelection() }
  },
  { deep: true }
)

watch(
  () => props.deletingSelectedCallLogs,
  isDeleting => {
    if (!isDeleting && selectingCallLogs.value && !selectedCallIds.value.length) exitDeleteSelection()
  }
)

onMounted(() => { document.addEventListener('click', handleDocumentClick) })
onUnmounted(() => { document.removeEventListener('click', handleDocumentClick) })

// ── Helpers ──────────────────────────────────────────────────────────
function initials(name) {
  return (name || '?').trim().split(/\s+/).map(p => p[0]).slice(0, 2).join('').toUpperCase()
}

function avatarColor(name) {
  const p = ['#1da462','#0b7dda','#7b3ff2','#e67e22','#e91e63','#00bcd4','#ff5722']
  let h = 0
  for (const c of name || '') h = c.charCodeAt(0) + ((h << 5) - h)
  return p[Math.abs(h) % p.length]
}

function isMissedCall(log)   { return log?.status === 'Missed' }
function isReceivedCall(log) {
  return log?.direction === 'incoming' && !['Missed','Rejected','Ringing'].includes(log?.status)
}

function callTypeLabel(log) {
  const type = log?.call_type === 'Video' ? 'Video call' : 'Voice call'
  if (isMissedCall(log))   return `Missed ${type.toLowerCase()}`
  if (isReceivedCall(log)) return type
  if (log?.direction === 'outgoing' && log?.status === 'Completed') return `Outgoing ${type.toLowerCase()}`
  return type
}

function directionIconClass(log) {
  if (isMissedCall(log))   return 'text-red-400'
  if (isReceivedCall(log)) return 'text-green-400'
  return 'text-slate-400'
}

function formatTime(value) {
  if (!value) return ''
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return ''
  const now = new Date()
  if (d.toDateString() === now.toDateString())
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  return d.toLocaleDateString([], { day: '2-digit', month: 'short' })
}
</script>

<style scoped>
/* ── Root ────────────────────────────────────────────────────────── */
.wa-sidebar {
  background: #111b21;
  border-right: 1px solid rgba(255,255,255,0.07);
}

/* ── Rail ────────────────────────────────────────────────────────── */
.wa-rail {
  background: #202c33;
  border-right: 1px solid rgba(255,255,255,0.05);
}

.wa-avatar-top {
  box-shadow: 0 0 0 2px rgba(0,168,132,0.35);
}

.wa-rail-btn { color: #8696a0; }
.wa-rail-inactive:hover { background: rgba(255,255,255,0.08); color: #e9edef; }
.wa-rail-active { color: #00a884; background: rgba(0,168,132,0.12); }

/* ── Panel ───────────────────────────────────────────────────────── */
.wa-panel { background: #111b21; }

.wa-panel-header {
  background: #202c33;
  border-bottom: 1px solid rgba(255,255,255,0.05);
  min-height: 56px;
  display: flex;
  align-items: center;
}

.wa-title { color: #e9edef; }

.wa-icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 34px;
  width: 34px;
  border-radius: 9999px;
  color: #8696a0;
  transition: background 0.15s, color 0.15s;
}
.wa-icon-btn:hover { background: rgba(255,255,255,0.08); color: #e9edef; }
.wa-icon-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.wa-menu-dropdown {
  background: rgba(32, 44, 51, 0.98);
  border: 1px solid rgba(255,255,255,0.08);
  box-shadow: 0 18px 40px rgba(0,0,0,0.28);
}

.wa-menu-item { color: #e9edef; transition: background 0.15s, color 0.15s; }
.wa-menu-item:hover { background: rgba(255,255,255,0.08); }

/* Search bar */
.wa-search-wrap { background: #202c33; padding-bottom: 8px; }
.wa-search-bar { background: #2a3942; border-radius: 8px; }
.wa-search-icon { color: #8696a0; }
.wa-search-input { color: #d1d7db; }
.wa-search-input::placeholder { color: #8696a0; }

/* Stats */
.wa-stats-row { margin-top: 10px; }
.wa-stat-card {
  background: #202c33;
  border: 1px solid rgba(255,255,255,0.06);
}
.wa-stat-card.missed { border-color: rgba(241,92,109,0.2); background: rgba(241,92,109,0.07); }

.wa-stat-icon-wrap { background: rgba(0,168,132,0.12); color: #00a884; }
.wa-stat-icon-wrap.missed { background: rgba(241,92,109,0.15); color: #f15c6d; }

.wa-stat-label {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  color: #8696a0;
}
.wa-stat-label.missed { color: #f15c6d; }
.wa-stat-num { font-size: 1.35rem; font-weight: 700; color: #e9edef; line-height: 1; margin-top: 2px; }
.wa-stat-num.missed { color: #f15c6d; }

/* Section label */
.wa-section-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #8696a0;
  background: #111b21;
  padding: 8px 16px 4px;
}

.wa-section-count {
  font-size: 0.72rem;
  letter-spacing: 0;
  text-transform: none;
  color: #8696a0;
}

.wa-select-toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0;
  text-transform: none;
  color: #e9edef;
  transition: opacity 0.15s;
}

.wa-select-toggle:disabled { opacity: 0.45; cursor: not-allowed; }

.wa-select-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(17,27,33,0.75);
  color: transparent;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.wa-select-box.is-selected {
  background: #00a884;
  border-color: #00c79a;
  color: #111b21;
}

.wa-selected-count { color: #8696a0; }

.wa-header-delete-btn {
  color: #fca5a5;
  background: rgba(241,92,109,0.08);
  border: 1px solid rgba(241,92,109,0.18);
  transition: background 0.15s, color 0.15s, opacity 0.15s;
}
.wa-header-delete-btn:hover { background: rgba(241,92,109,0.18); color: #ffffff; }
.wa-header-delete-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ── Call rows ───────────────────────────────────────────────────── */
.wa-call-row { background: #111b21; transition: background 0.12s; }
.wa-call-row:hover { background: #202c33; }
.wa-call-row-selected { background: rgba(0,168,132,0.14); }
.wa-call-row-selected:hover { background: rgba(0,168,132,0.18); }

.wa-call-name { color: #e9edef; }
.wa-call-meta { color: #8696a0; }
.wa-missed-text { color: #f15c6d !important; }
.wa-row-divider { background: rgba(255,255,255,0.05); }

/* Callback button */
.wa-cb-btn {
  opacity: 0.5;
  transition: opacity 0.15s, background 0.15s;
  cursor: pointer;
}
.wa-call-row:hover .wa-cb-btn { opacity: 1; }
.wa-cb-audio { color: #00a884; background: rgba(0,168,132,0.1); }
.wa-cb-audio:hover { background: rgba(0,168,132,0.2); }
.wa-cb-video { color: #00a884; background: rgba(0,168,132,0.1); }
.wa-cb-video:hover { background: rgba(0,168,132,0.2); }

/* Empty state */
.wa-empty-icon { background: #202c33; }

/* Scrollbar */
.wa-scroll::-webkit-scrollbar { width: 4px; }
.wa-scroll::-webkit-scrollbar-track { background: transparent; }
.wa-scroll::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 99px; }

/* ── Profile ─────────────────────────────────────────────────────── */
.wa-profile-hero { background: #202c33; border-bottom: 1px solid rgba(255,255,255,0.05); }

.wa-profile-popup {
  background: rgba(17, 27, 33, 0.96);
  border: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(14px);
}

.wa-profile-popup-title {
  font-size: 0.65rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #8696a0;
}

.wa-profile-popup-card {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.06);
}

.wa-logout-btn {
  background: rgba(241,92,109,0.1);
  border: 1px solid rgba(241,92,109,0.2);
  color: #f15c6d;
}
.wa-logout-btn:hover { background: rgba(241,92,109,0.18); color: #fff; }
</style>
