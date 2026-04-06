import { userResource } from "@/data/user"
import { createRouter, createWebHistory } from "vue-router"
import { session } from "./data/session"

const routes = [
	{
		path: "/",
		name: "Chat",
		component: () => import("@/pages/Chat.vue"),
	},
	{
		name: "Login",
		path: "/login",
		component: () => import("@/pages/Login.vue"),
	},
	{
		name: "Signup",
		path: "/signup",
		component: () => import("@/pages/Signup.vue"),
	},
	{
		name: "Status",
		path: "/status",
		component: () => import("@/pages/status.vue"),
	},
]
const router = createRouter({
	history: createWebHistory("/frontend"),
	routes,
})

router.beforeEach(async (to, from, next) => {
	let isLoggedIn = session.isLoggedIn
	try {
		await userResource.promise
	} catch (error) {
		isLoggedIn = false
	}

	if (to.name === "Login" && isLoggedIn) {
		next({ name: "Chat" })
	} else if (to.name === "Signup" && isLoggedIn) {
		next({ name: "Chat" })
	} else if (to.name !== "Login" && to.name !== "Signup" && !isLoggedIn) {
		next({ name: "Login" })
	} else {
		next()
	}
})

export default router
