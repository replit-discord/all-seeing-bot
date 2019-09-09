<template>
  <div>
    <h1>all-seeing-bot admin panel</h1>
    <p>control settings related to the
      <el-link href="https://github.com/repl-it-discord/All-Seeing-Bot" target="__blank" type="primary">
      all-seeing-bot</el-link>. updates real time
    </p>
    <section>
      <h2>to sign in you must be authentiacted</h2>
      <div v-if="!isSignedIn">
        <el-button type="primary" >Sign In</el-button>
      </div>
    </section>
  </div>
</template>

<script>
  export default {
    name: "Home"
  }
</script>

<style lang="postcss" scoped>
section {
  padding: $spacing 0;
}
</style>
