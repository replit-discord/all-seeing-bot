<template>
  <div id="root">
    <h1>this is the root</h1>
    <router-view></router-view>
  </div>
</template>

<script lang="ts">
import f from "./charlie";

export default {
  name: "App",
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
}

h1 {
  background-color: $orange;
  animation-delay: 100ms;
}
</style>
