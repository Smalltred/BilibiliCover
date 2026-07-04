<!--
  页脚 —— 只保留版权信息
  视图切换在顶部 SiteNav 完成,这里只做版权
-->
<template>
  <footer class="footer">
    <p class="copyright">
      © 2026 <a href="https://hecady.com" target="_blank" rel="noopener">hecady</a>
    </p>
  </footer>
</template>

<style scoped>
.footer {
  margin-top: auto;
  padding: 24px 0 32px;
  text-align: center;
}

.copyright {
  font-size: 12px;
  color: var(--text-muted);
  margin: 0;
}

.copyright a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition);
}

.copyright a:hover {
  color: var(--accent);
}
</style>