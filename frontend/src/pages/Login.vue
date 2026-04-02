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
    <div class="absolute top-20 left-10 bg-white px-4 py-2 rounded-xl shadow animate-bounce">
      Hi 👋
    </div>
    <div class="absolute bottom-20 right-10 bg-green-500 text-white px-4 py-2 rounded-xl shadow animate-pulse">
      Welcome 🚀
    </div>

    <!-- 🔥 Glass Card -->
    <Card class="relative z-10 w-full max-w-md p-8 rounded-3xl shadow-2xl bg-white/80 backdrop-blur-xl border border-white/40">

      <!-- Logo -->
      <div class="flex flex-col items-center mb-6">
        <div class="bg-gradient-to-r from-green-500 to-emerald-500 text-white w-16 h-16 flex items-center justify-center rounded-full text-3xl shadow-lg">
          💬
        </div>
        <h2 class="text-3xl font-bold mt-4 text-gray-800">Chat Login</h2>
        <p class="text-gray-500 text-sm">Start chatting instantly</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="login_page" class="flex flex-col gap-5">

        <input
          v-model="email"
          type="text"
          placeholder="Enter email"
          class="border rounded-xl p-3"
        />
        <p v-if="email_error" class="text-red-500 text-sm -mt-7">Email is required</p>

        <div class="relative">
          <input
            :type="showPassword ? 'text' : 'password'"
            v-model="password"
            placeholder="Enter password"
            class="border rounded-xl p-3 w-full"
          />
          <span
            @click="togglePassword"
            class="absolute right-3 top-5 cursor-pointer text-sm text-gray-500"
          >
            {{ showPassword ? "Hide" : "Show" }}
          </span>
        </div>
        <p v-if="password_error" class="text-red-500 text-sm">Password is required</p>

        <!-- Button -->
        <button
          :disabled="isFreezing"
          class="mt-2 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-semibold rounded-xl py-3 transition-all duration-300 shadow-lg hover:scale-105 hover:shadow-xl disabled:opacity-50"
        >
          {{ isFreezing ? "Logging in..." : "🚀 Login" }}
        </button>

      </form>

      <!-- Footer -->
      <p class="text-center text-sm text-gray-500 mt-6">
        Don’t have an account?
        <router-link to="/signup" class="text-green-600 font-semibold cursor-pointer hover:underline">
          Sign Up
        </router-link>
      </p>

    </Card>

  </div>
</template>

<script setup>
import { ref } from "vue";
import router from "../router"
import { useToast } from "vue-toastification";

const toast = useToast();

const email = ref("");
const password = ref("");

const email_error = ref(false);
const password_error = ref(false);
const showPassword = ref(false);
const isFreezing = ref(false);

const togglePassword = () => {
  showPassword.value = !showPassword.value;
};

const login_page = async () => {

  email_error.value = !email.value;
  password_error.value = !password.value;

  if (email_error.value || password_error.value) return;

  isFreezing.value = true;

  try {
    const response = await fetch("/login", {
      method: "POST",
      headers: {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest",
      },
      credentials: "include",
      body: new URLSearchParams({
        cmd: "login",
        usr: email.value,
        pwd: password.value,
      }),
    });

    const data = await response.json();

    if (data.message === "Logged In" || data.message === "No App") {
      window.location.href = "/";
    } else {
      toast.error("Invalid login credentials");
      isFreezing.value = false;
    }

  } catch (error) {
    console.error("Login failed:", error);
    toast.error("Server error, please try again");
    isFreezing.value = false;
  }
};
</script>