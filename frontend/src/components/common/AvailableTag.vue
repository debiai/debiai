<template>
  <div>
    <div
      class="status available"
      v-if="available"
    >
      ✓ Available
    </div>
    <div
      class="status notAvailable"
      v-else
    >
      ❌ Not available
    </div>
  </div>
</template>

<script>
export default {
  name: "AvailableTag",
  props: {
    available: { type: Boolean, required: true },
  },
};
</script>

<style scoped>
/* Status */
.status {
  padding: 0.2rem 0.5rem;
  font-weight: bold;
}
.status.available {
  color: var(--success);
}
.status.notAvailable {
  color: var(--danger);
}
</style>
