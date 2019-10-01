import Vue from "vue";
import VueRouter from "vue-router";

import Home from "./views/Home";
import Settings from "./views/Settings";

Vue.use(VueRouter);

export default new VueRouter({
  routes: [
    {
      path: "/",
      component: Home
    },
    {
      path: "/settings",
      component: Settings
    }
  ]
});
