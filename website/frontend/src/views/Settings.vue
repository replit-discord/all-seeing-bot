<template>
  <div>
    <h1>settings</h1>
    <p>update settings that directoy control the bot</p>

    <section>
      <h3>choose</h3>
      <el-radio v-model="radioValue" label="a">alfa</el-radio>
      <el-radio v-model="radioValue" label="b">bravo</el-radio>
    </section>

    <section>
      <h3>selections</h3>
      <el-switch
        v-model="switchValue"
        active-color="#13ce66"
        inactive-color="#ff4949"
        active-text="occurs when true"
      >
      </el-switch>
    </section>

    <section>
      <h3>transfers</h3>
      <el-transfer
        v-model="transferValue"
        :data="transferData"
        :titles="['From', 'To']"
      >
      </el-transfer>
    </section>

    <section>
      <h3>input</h3>
      <el-input placeholder="input here" v-model="inputValue"></el-input>
    </section>
  </div>
</template>

<script>
export default {
  name: "Settings",
  data() {
    let generateData = () => {
      const data = [];
      for (let i = 1; i <= 15; i++) {
        data.push({
          key: i,
          label: `Option ${i}`,
          disabled: i % 4 === 0
        });
      }
      return data;
    };

    return {
      radioValue: "a",
      switchValue: true,
      transferData: generateData(),
      transferValue: [1, 4],
      inputValue: ""
    }
  }
}
</script>

<style lang="postcss" scoped>
section {
  padding: $spacing 0;
}
</style>
