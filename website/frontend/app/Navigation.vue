<template>
  <el-menu default-active="/" mode="horizontal">
    <el-menu-item index="/" p="/" @click="s">Home</el-menu-item>
    <el-menu-item index="/settings" p="/settings" @click="s">Settings</el-menu-item>
  </el-menu>
</template>

<script>
export default {
  name: "Navigation",
  methods: {
    s(e) {
      // ugh
      const route = e.$el.attributes.p.nodeValue;
      this.$router.push(route);
    }
  }
}
</script>
