document.addEventListener("DOMContentLoaded", function () {
  console.log("JavaScript loaded"); // To confirm JS file loads

  // Store the previous scroll position and toggle state
  let previousScrollPosition = 0;
  let isAtTop = true; // Track if we're at the top of the page

  // Define the toggleScroll function
  function toggleScroll() {
    const scrollIcon = document.getElementById("scrollIcon");

    if (isAtTop) {
      // Save the current scroll position
      previousScrollPosition = window.scrollY;
      // Scroll to the top
      window.scrollTo({ top: 0, behavior: 'smooth' });
      // Change icon to down arrow
      scrollIcon.src = "/static/assets/img/down-arrow.svg";
      console.log("Scrolled to top, icon changed to down arrow");
    } else {
      // Scroll back to the previous position
      window.scrollTo({ top: previousScrollPosition, behavior: 'smooth' });
      // Change icon to up arrow
      scrollIcon.src = "/static/assets/img/up-arrow.svg";
      console.log("Scrolled to previous position, icon changed to up arrow");
    }

    // Toggle the state
    isAtTop = !isAtTop;
  }

  // Attach the event listener to the button
  const scrollButton = document.getElementById("scrollButton");
  scrollButton.addEventListener("click", toggleScroll);
});