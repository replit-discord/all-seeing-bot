<template>
  <div>
    <h1>all-seeing-bot admin panel</h1>
    <p>control settings related to the
      <el-link href="https://github.com/repl-it-discord/All-Seeing-Bot" target="__blank" type="primary">
      all-seeing-bot</el-link>. updates real time
    </p>
    <section>
      <h2>to false you must be authentiacted</h2>
      <div v-if="!isSignedIn">
        <a href="https://discordapp.com/oauth2/authorize?client_id=585606487372464215&redirect_uri=http%3A%2F%2Flocalhost%3A3000/callback&response_type=code&scope=identify%20guilds.join" target="__blank">
          <el-button type="primary">Sign In</el-button>
        </a>
      </div>
    </section>
  </div>
</template>

<script>
  export default {
    name: "Home",
    data() {
      return {
        isSignedIn: false,
        permissions: {
        	'muteduration': false,
          'offenseduration': false,
          'offenselimit': false,
          'help': false,
          'reset': false,
          'read': false,
          'write': false,
          'ban': false,
          'unban': false,
          'phraselimit': false,
          'muteincrement': false,
          'emojimax': false,
          'mentionlimit': false,
          'actionlog': false,
          'trust': false,
          'trustrole': false,
          'untrustrole': false,
          'kick': false,
          'mute': false,
          'unmute': false,
          'warn': false,
          'warns': false,
          'warnings': false,
          'removewarn': false,
          'modmail': false,
          'muterole': false
        }
      }
    }
  }
</script>

<style lang="postcss" scoped>
section {
  padding: $spacing 0;
}
</style>
