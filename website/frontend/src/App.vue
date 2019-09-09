<template>
  <el-container>
    <el-header>
      <navigation></navigation>
    </el-header>
    <el-main>
      <router-view></router-view>
    </el-main>
  </el-container>
</template>

<script lang="ts">
import Navigation from "./Navigation";

export default {
  name: "App",
  components: {
    "navigation": Navigation
  }
};
</script>

<style lang="postcss">
* {
  margin: 0;
  padding: 0;
  border: 0 none;
  font-family: 'IBM Plex Sans', sans-serif;
}
</style>
