<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden">

    <!-- 🌈 Background Gradient -->
    <div class="absolute inset-0 bg-gradient-to-br from-green-300 via-emerald-200 to-green-400"></div>

    <!-- 🖼️ Background Image -->
    <img
      src="https://images.unsplash.com/photo-1611746872915-64382b5c76da"
      class="absolute inset-0 w-full h-full object-cover opacity-20"
    />

    <!-- 💬 Floating Chat Bubbles -->
    <div class="hidden sm:block absolute top-20 left-10 bg-white px-4 py-2 rounded-xl shadow animate-bounce">
      Hello 👋
    </div>
    <div class="hidden sm:block absolute bottom-20 right-10 bg-green-500 text-white px-4 py-2 rounded-xl shadow animate-pulse">
      Join Us 🚀
    </div>

    <!-- 🔥 Glass Card -->
    <Card class="relative z-10 w-full max-w-md mx-4 p-5 sm:p-8 rounded-3xl shadow-2xl bg-white/80 backdrop-blur-xl border border-white/40">

      <!-- Logo -->
      <div class="flex flex-col items-center mb-6">
        <div class="bg-gradient-to-r from-green-500 to-emerald-500 text-white w-16 h-16 flex items-center justify-center rounded-full text-3xl shadow-lg">
          💬
        </div>
        <h2 class="text-2xl sm:text-3xl font-bold mt-4 text-gray-800">Create Account</h2>
        <p class="text-gray-500 text-sm">Sign up and start chatting today</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="signup_page" class="flex flex-col gap-5">

        <!-- First & Last Name -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <input
              v-model="firstName"
              type="text"
              placeholder="First name"
              class="border rounded-xl p-3 w-full"
            />
            <p v-if="firstName_error" class="text-red-500 text-xs mt-1">Required</p>
          </div>
          <div>
            <input
              v-model="lastName"
              type="text"
              placeholder="Last name"
              class="border rounded-xl p-3 w-full"
            />
            <p v-if="lastName_error" class="text-red-500 text-xs mt-1">Required</p>
          </div>
        </div>

        <!-- Email -->
        <div>
          <input
            v-model="email"
            type="email"
            placeholder="Enter email"
            class="border rounded-xl p-3 w-full"
          />
          <p v-if="email_error" class="text-red-500 text-sm mt-1">Valid email is required</p>
        </div>

        <!-- Password -->
        <div class="relative">
          <input
            :type="showPassword ? 'text' : 'password'"
            v-model="password"
            placeholder="Enter password"
            class="border rounded-xl p-3 w-full pr-16"
          />
          <span
            @click="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-sm text-gray-500"
          >
            {{ showPassword ? "Hide" : "Show" }}
          </span>
        </div>
        <p v-if="password_error" class="text-red-500 text-sm -mt-4">Password is required</p>

        <!-- Confirm Password -->
        <div class="relative">
          <input
            :type="showConfirm ? 'text' : 'password'"
            v-model="confirmPassword"
            placeholder="Confirm password"
            class="border rounded-xl p-3 w-full pr-16"
          />
          <span
            @click="showConfirm = !showConfirm"
            class="absolute right-3 top-1/2 -translate-y-1/2 cursor-pointer text-sm text-gray-500"
          >
            {{ showConfirm ? "Hide" : "Show" }}
          </span>
        </div>
        <p v-if="confirm_error" class="text-red-500 text-sm -mt-4">Passwords do not match</p>

        <!-- Terms Checkbox -->
        <label class="flex items-center gap-2 cursor-pointer">
          <input v-model="agreedToTerms" type="checkbox" class="w-4 h-4 accent-green-500" />
          <span class="text-sm text-gray-500">
            I agree to the
            <span class="text-green-600 font-semibold hover:underline cursor-pointer">Terms & Privacy Policy</span>
          </span>
        </label>
        <p v-if="terms_error" class="text-red-500 text-sm -mt-4">You must agree to continue</p>

        <!-- Server Error -->
        <p v-if="serverError" class="text-red-500 text-sm text-center -mt-2">{{ serverError }}</p>

        <!-- Button -->
        <button
          :disabled="isFreezing"
          class="mt-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold rounded-xl py-3 transition-all duration-300 shadow-lg hover:scale-105 hover:shadow-xl disabled:opacity-50"
        >
          {{ isFreezing ? "Creating account..." : "🚀 Sign Up" }}
        </button>

      </form>

      <!-- Divider -->
      <div class="flex items-center gap-3 my-5">
        <div class="flex-1 h-px bg-gray-200"></div>
        <span class="text-xs text-gray-400">or sign up with</span>
        <div class="flex-1 h-px bg-gray-200"></div>
      </div>

      <!-- Social Buttons -->
      <div class="grid grid-cols-2 gap-3 mb-5">
        <button class="flex items-center justify-center gap-2 border rounded-xl py-2.5 text-sm text-gray-700 hover:border-green-400 transition-colors">
          🇬 Google
        </button>
        <button class="flex items-center justify-center gap-2 bg-blue-600 text-white rounded-xl py-2.5 text-sm hover:bg-blue-700 transition-colors">
          📘 Facebook
        </button>
      </div>

      <!-- Footer -->
      <p class="text-center text-sm text-gray-500">
        Already have an account?
        <router-link to="/login" class="text-green-600 font-semibold cursor-pointer hover:underline">
          Login
        </router-link>
      </p>

    </Card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { createResource } from 'frappe-ui'

const router = useRouter()

const firstName      = ref('')
const lastName       = ref('')
const email          = ref('')
const password       = ref('')
const confirmPassword = ref('')
const agreedToTerms  = ref(false)

const showPassword = ref(false)
const showConfirm  = ref(false)
const isFreezing   = ref(false)
const serverError  = ref('')

const firstName_error = ref(false)
const lastName_error  = ref(false)
const email_error     = ref(false)
const password_error  = ref(false)
const confirm_error   = ref(false)
const terms_error     = ref(false)

const signupResource = createResource({
  url: 'fun.api.signup',
  onSuccess() {
    router.replace('/chat')
  },
  onError(err) {
    serverError.value = err?.messages?.[0] || err?.message || 'Signup failed. Please try again.'
    isFreezing.value = false
  },
})

function signup_page() {
  serverError.value = ''

  firstName_error.value = !firstName.value.trim()
  lastName_error.value  = !lastName.value.trim()
  email_error.value     = !email.value.trim()
  password_error.value  = !password.value.trim()
  confirm_error.value   = password.value !== confirmPassword.value
  terms_error.value     = !agreedToTerms.value

  const hasError = [
    firstName_error.value,
    lastName_error.value,
    email_error.value,
    password_error.value,
    confirm_error.value,
    terms_error.value,
  ].some(Boolean)

  if (hasError) return

  isFreezing.value = true
  signupResource.submit({
    first_name: firstName.value.trim(),
    last_name: lastName.value.trim(),
    email: email.value.trim(),
    password: password.value,
  })
}
</script>