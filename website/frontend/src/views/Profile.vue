<template>
  <div>
    <h1>profile template</h1>
  </div>
</template>

<script>
export default {
  data() {
    return {
      userData: {}
    }
  },
  created() {
    fetch("/user", { method: "GET"})
      .then(res => {
        return res.text();
      })
      .then(json => {
        console.log(json);
      })
      .catch(err => {
        console.log(err);
      });
  }
}
</script>
