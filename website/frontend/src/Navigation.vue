<template>
  <el-menu :default-active="activeLink" mode="horizontal">
    <el-menu-item index="/" p="/" @click="s">Home</el-menu-item>
    <el-menu-item index="/settings" p="/settings" @click="s">Settings</el-menu-item>
    <el-menu-item index="/profile" p="/profile" @click="s">Profile</el-menu-item>
  </el-menu>
</template>

<script>
export default {
  name: "Navigation",
  data() {
    return {
      activeLink: null
    }
  },
  created() {
    this.activeLink = this.$route.path
  },
  methods: {
    s(e) {
      // ugh
      const route = e.$el.attributes.p.nodeValue;
      this.$router.push(route);
    }
  },
  watch: {
    $route(to, from) {
      this.activeLink = to.path;
    }
  }
}
</script>
