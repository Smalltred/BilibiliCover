<template>
  <div class="app">
    <SiteNav :view="view" @navigate="view = $event" />

    <!-- 主视图:Hero(标题+输入)+ loading inline + modal 弹结果 -->
    <div class="content">
      <template v-if="view === 'home'">
        <HeroInput :loading="loading" @submit="submit" />
        <LoadingCenter v-if="loading" />
        <CoverPreview
          v-else-if="result || error"
          :data="result"
          :error="error"
          @reset="reset"
        />
      </template>

      <!-- 文档视图 -->
      <ApiDocs v-else-if="view === 'docs'" />
    </div>

    <SiteFooter />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import HeroInput from '@/components/HeroInput.vue'
import CoverPreview from '@/components/CoverPreview.vue'
import LoadingCenter from '@/components/LoadingCenter.vue'
import ApiDocs from '@/components/ApiDocs.vue'
import SiteNav from '@/components/SiteNav.vue'
import SiteFooter from '@/components/SiteFooter.vue'
import { useResolver } from '@/composables/useResolver.js'

const view = ref('home') // 'home' | 'docs'
const { loading, result, error, submit, reset } = useResolver()
</script>

<style scoped>
.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: 100%;
  max-width: 1100px;
  margin: 0 auto;
  padding: 0 24px;
}

.content {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 32px 0;
}
</style>