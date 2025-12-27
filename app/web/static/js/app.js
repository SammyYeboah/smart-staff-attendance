// static/js/app.js
function toggleNav(){
  const sidebar = document.getElementById('sidebar');
  const isOpen = sidebar.classList.toggle('open');
  const toggle = document.querySelector('.nav-toggle');
  toggle.setAttribute('aria-expanded', String(isOpen));
  sidebar.setAttribute('aria-hidden', String(!isOpen));
}
