document.addEventListener('DOMContentLoaded', async () => {
  const resp = await fetch('/api/v1/spots');
  if (!resp.ok) return;
  const spots = await resp.json();
  const container = document.getElementById('spots');
  if (!container) return;
  spots.forEach((s) => {
    const div = document.createElement('div');
    div.textContent = `${s.id} - ${s.status}`;
    container.appendChild(div);
  });
});
