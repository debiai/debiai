<template>
  <div id="DocumentationBlock">
    <div id="questionMark">
      <b
        id="i"
        @mouseenter="show = true"
        @mouseleave="show = false"
        >i</b
      >
      <transition name="fade">
        <p
          id="docBlock"
          :class="{ top: top }"
          @mouseenter="show = true"
          @mouseleave="show = false"
          v-show="show"
        >
          <slot />
        </p>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: "DocumentationBlock",
  props: {
    followCursor: {
      type: Boolean,
      default: false,
    },
    top: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      show: false,
    };
  },
  mounted() {
    if (this.followCursor) {
      this.$el.addEventListener("mousemove", (e) => {
        this.$el.querySelector("#docBlock").style.left = e.clientX + 10 + "px";
        this.$el.querySelector("#docBlock").style.top = e.clientY + 10 + "px";
      });
    }
  },
};
</script>

<style scoped>
#questionMark #i {
  margin: 0 7px 0 7px;
  cursor: pointer;
  border: solid 1px var(--blueDark);
  color: var(--blueDark);
  background-color: rgb(245, 254, 255);
  border-radius: 100%;
  width: 18px;
  height: 15px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 3px;
  text-decoration: none;
  font-size: initial;
}

/* #questionMark:hover > #docBlock {
  visibility: visible;
  opacity: 1;
} */

#docBlock {
  /* opacity: 0; */
  /* visibility: hidden; */
  position: absolute;
  padding: 20px;
  margin: 0px;
  border: solid 1px var(--blueDark);
  border-radius: 3px;
  color: var(--blueDark);
  background-color: rgb(213, 251, 255);
  text-align: left;
  z-index: 1000;
  /* transition: visibility 0s, opacity 0.1s linear; */
  font-size: initial;
  text-decoration: none;
  align-self: flex-start;
  font-weight: normal;
  box-shadow: 0px 0px 25px rgba(0, 0, 0, 0.1);
  max-width: 500px;
  max-height: 500px;
  overflow-y: auto;
}

#docBlock.top {
  transform: translateY(-100%);
}
</style>

<style>
/* Style for the slot */
#docBlock * {
  border-color: var(--blueDark);
}
</style>
