import Vue from "vue";
import VueRouter from "vue-router";

import Home from "./views/Home";
import Settings from "./views/Settings";
import Profile from "./views/Profile";
import SignIn from "./views/SignIn";
import Page404 from "./views/Page404"

Vue.use(VueRouter);

export default new VueRouter({
  mode: "history",
  routes: [
    {
      path: "/",
      component: Home
    },
    {
      path: "/settings",
      component: Settings,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/profile",
      component: Profile,
      meta: {
        requiresAuth: true
      }
    },
    {
      path: "/sign-in",
      component: SignIn
    },
    {
      path: "/404",
      component: Page404
    },
    {
      path: "*",
      redirect: "/404"
    }
  ]
});
