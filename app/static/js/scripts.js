// The clearFilters function was written by GPT-4

function clearFilters() {
  // Get the form element
  const form = document.getElementById('filter-form');

  // Reset the form fields
  form.reset();

  // Clear the select fields specifically
  document.getElementById('category').selectedIndex = 0;
  if (document.getElementById('group')) {
    document.getElementById('group').selectedIndex = 0;
  }

  // Submit the form to reload the page with default values
  form.submit();
}
