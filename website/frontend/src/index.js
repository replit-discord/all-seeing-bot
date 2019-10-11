import Vue from "vue";

import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';

import App from "./App";
import router from "./router";
router.beforeEach((to, from, next) => {
  if(to.meta?.requiresAuth) {
    fetch("/is-authenticated", {
      method: "GET"
    })
      .then(res => {
        return res.json();
      })
      .then(json => {
        console.log("body here: ", json);
        if(json.isAuthenticated) {
          return next();
        }
        next({
          path: "/sign-in",
        });

      })
      .catch(err => {
        console.log(err);
      })

  }
  else {
    next();
  }
});

Vue.use(ElementUI);

Vue.config.productionTip = false;

new Vue({
  el: "#app",
  router,
  render: h => h(App)
});
