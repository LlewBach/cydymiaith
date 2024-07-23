// The clearFilters function was written with the help of GPT-4 and refactored by myself

function clearFilters() {
  const form = document.getElementById('filter-form');

  const selectInputs = form.querySelectorAll('select');
  if (selectInputs) {
    selectInputs.forEach(select => {
      select.selectedIndex = 0;
    });
  }

  const textInputs = form.querySelectorAll('input[type="text"]');
  if (textInputs) {
    textInputs.forEach(input => {
      input.value = '';
    });
  }

  const emailInput = form.querySelector('input[type="email"]');
  if (emailInput) {
    emailInput.value = '';
  }

  form.submit();
}
