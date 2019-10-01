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
import f from "./charlie";

export default {
  name: "App",
  components: {
    "navigation": Navigation
  },
  mounted() {
    console.log("mounted");
    console.log(f);
  }
};
</script>

<style lang="postcss">
$blue: orange;

* {
  margin: 0;
  padding: 0;
  border: 0 none;
  font-family: 'IBM Plex Sans', sans-serif;
}
</style>
