<template>
  <div>
    <h1>settings</h1>
    <p>update settings that directoy control the bot</p>

    <h3>name</h3>
    <el-input placeholder="input here" v-model="inputValue" style="width: 200px"></el-input>

    <div v-for="perm in Object.keys(permissions)" :key=perm class="permission">
      <p>{{ perm }}</p>
      <el-switch
        v-model="permissions[perm]"
        active-color="#13ce66"
        inactive-color="#ff4949">
      </el-switch>
    </div>
  </div>
</template>

<script>
export default {
  name: "Settings",
  data() {
    return {
      isSignedIn: false,
      permissions: {
        muteduration: false,
        offenseduration: false,
        offenselimit: false,
        help: false,
        reset: false,
        read: false,
        write: false,
        ban: false,
        unban: false,
        phraselimit: false,
        muteincrement: false,
        emojimax: false,
        mentionlimit: false,
        actionlog: false,
        trust: false,
        trustrole: false,
        untrustrole: false,
        kick: false,
        mute: false,
        unmute: false,
        warn: false,
        warns: false,
        warnings: false,
        removewarn: false,
        modmail: false,
        muterole: false
      },
      inputValue: ""
    }
  }
}
</script>

<style scoped lang="postcss">
.permission {
  padding: 10px;
}
</style>
