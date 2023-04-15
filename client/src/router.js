/*
 * Vue router to register new pages on the web application
 */
import Vue from "vue";
import store from "@/store"
import Router from "vue-router";
import About from "./views/AboutPage.vue"
import AHJSearchPage from "./views/AHJSearchPage.vue";
import DataVis from "./views/DataVis.vue";
import UserProfile from "./views/UserAccounts/UserProfile";
import UserProgress from "./views/UserAccounts/UserProgress";
import UserSettings from "./views/UserAccounts/UserSettings";
import AHJPage from "./views/AHJPage.vue";
import LoginPage from "./views/UserAccounts/LoginPage.vue";
import EmailVerified from "./views/UserAccounts/EmailVerified.vue";
import PasswordReset from "./views/UserAccounts/PasswordReset.vue";
import PasswordResetConfirm from "./views/UserAccounts/PasswordResetConfirm.vue";
import RegisterPage from "./views/UserAccounts/RegisterPage.vue";
import Logout from "./components/UserAccounts/Auth/Logout.vue";
import NotFound from "./components/NotFound.vue";

Vue.use(Router);

let router = new Router({
  routes: [
    { path: "/", redirect: "/ahj-search"},
    {
      path: "/about",
      name: "about",
      component: About
    },
    {
      path: "/ahj-search",
      name: "ahj-search",
      component: AHJSearchPage
    },
    {
      path: "/user",
      name: "user",
      component: UserProfile
    },
    {
      path: "/view-ahj/:AHJID",
      name: "view-ahj",
      component: AHJPage
    },
    {
      path: "/user/:username",
      name: "view-profile",
      component: UserProfile
    },
    {
      path: "/progress",
      name: "user-progress",
      component: UserProgress
    },
    {
      path: "/settings",
      name: "settings",
      component: UserSettings,
      meta: { isAuth: true}
    },
    {
      path: "/login",
      name: "login",
      component: LoginPage,
      meta: { notAuth: true}
    },
    {
      path: "/register",
      name: "register",
      component: RegisterPage,
      meta: { notAuth: true},
      props: true
    },
    {
      path: "/logout",
      name: "logout",
      component: Logout
    },
    {
      path: "/data-vis",
      name: "data-vis",
      component: DataVis
    },
    {
      path: "/activate/:uid/:token",
      name: "activate",
      component: EmailVerified
    },
    {
      path: "/password_reset",
      name: "password_reset",
      component: PasswordReset
    },
    {
      path: "/password_reset_confirm/:uid/:token",
      name: "password_reset_confirm",
      component: PasswordResetConfirm
    },
    {
      path: "/not-found",
      name: "not-found",
      component: NotFound
    },
    {
      path: '*',
      name: "not-found-default",
      component: NotFound
    }
  ]
});

// Routine performed before changing pages
// May redirect page changes based on if the user is logged in
router.beforeEach((to, from, next) => {
  // If we are going to the same type of page but with different params, reload page (Used for user profiles)
  if (to.name == from.name && from.name !== "not-found-default"){
    location.reload();
  }
  // Restrict access to pages that should only be accessed by users not logged in
  if (to.meta.notAuth){
    if (store.getters.loggedIn){
      next({
        name: "ahj-search"
      });
    }
    else{
      next();
    }
  }
  // Restrict access to pages that should only be accessed by users that are logged in
  else if (to.meta.isAuth) {
    if (!store.getters.loggedIn){
      next({
        name: "ahj-search"
      });
    }
    else{
      next();
    }
  }
  else {
    next();
  }
})

export default router;
