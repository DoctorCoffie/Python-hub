const spot = document.querySelector(".python-spot");
if (spot) {
  spot.animate(
    [
      { transform: "translateY(0px)" },
      { transform: "translateY(-8px)" },
      { transform: "translateY(0px)" },
    ],
    {
      duration: 3200,
      iterations: Infinity,
      easing: "ease-in-out",
    }
  );
}
