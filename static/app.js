const form = document.getElementById('review-form');
const output = document.getElementById('output');

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const data = new FormData(form);

  const response = await fetch('/api/review', {
    method: 'POST',
    body: data,
  });

  const payload = await response.json();
  if (!response.ok) {
    alert(payload.error || 'Unable to review file');
    return;
  }

  document.getElementById('review').textContent = payload.review;
  document.getElementById('coverage').textContent = `${payload.coverage}%`;
  document.getElementById('tree').textContent = payload.tree;
  output.classList.remove('hidden');
});
